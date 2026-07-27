#!/usr/bin/env python3
"""Replace the 7371-bp pGP564 backbone in every pGP95 FASTA record."""

import argparse
import hashlib
import json
from pathlib import Path


VALID_DNA = set("ACGTRYSWKMBDHVN")
OLD_INSERT_INDEX = 5042
NEW_INSERT_INDEX = 4982


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_fasta(path):
    records = []
    name = None
    parts = []
    with Path(path).open("r", encoding="ascii", errors="strict") as handle:
        for line_number, raw in enumerate(handle, 1):
            line = raw.strip()
            if not line:
                continue
            if line.startswith(">"):
                if name is not None:
                    records.append((name, "".join(parts).upper()))
                name = line[1:].strip().split()[0]
                if not name:
                    raise ValueError("{}:{} empty FASTA header".format(path, line_number))
                parts = []
            else:
                if name is None:
                    raise ValueError(
                        "{}:{} sequence before first header".format(path, line_number)
                    )
                parts.append(line)
    if name is not None:
        records.append((name, "".join(parts).upper()))
    if not records:
        raise ValueError("{} contains no FASTA records".format(path))
    names = [name for name, _ in records]
    if len(names) != len(set(names)):
        raise ValueError("{} contains duplicate IDs".format(path))
    for name, sequence in records:
        invalid = set(sequence) - VALID_DNA
        if not sequence or invalid:
            raise ValueError(
                "{} record {} has invalid characters {}".format(
                    path, name, "".join(sorted(invalid))
                )
            )
    return records


def read_single_sequence(path):
    records = read_fasta(path)
    if len(records) != 1:
        raise ValueError("{} must contain exactly one FASTA record".format(path))
    return records[0][1]


def write_record(handle, name, sequence, width=80):
    handle.write(">{}\n".format(name))
    for offset in range(0, len(sequence), width):
        handle.write(sequence[offset : offset + width] + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-pgp95", required=True)
    parser.add_argument("--old-backbone-7371", required=True)
    parser.add_argument("--new-backbone-7158", required=True)
    parser.add_argument("--output-fasta", required=True)
    parser.add_argument("--output-manifest", required=True)
    parser.add_argument("--output-validation", required=True)
    args = parser.parse_args()

    source = Path(args.input_pgp95)
    output = Path(args.output_fasta)
    manifest_path = Path(args.output_manifest)
    validation_path = Path(args.output_validation)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    validation_path.parent.mkdir(parents=True, exist_ok=True)

    old_backbone = read_single_sequence(args.old_backbone_7371)
    new_backbone = read_single_sequence(args.new_backbone_7158)
    if len(old_backbone) != 7371 or len(new_backbone) != 7158:
        raise ValueError("Expected 7371-bp old and 7158-bp new backbones")
    reconstructed_new = (
        old_backbone[:3600] + old_backbone[3660:6180] + old_backbone[6333:]
    )
    if reconstructed_new != new_backbone:
        raise ValueError(
            "The supplied backbones do not differ by the verified 60- and 153-bp blocks"
        )
    if old_backbone[:OLD_INSERT_INDEX].replace(
        old_backbone[3600:3660], "", 1
    ) != new_backbone[:NEW_INSERT_INDEX]:
        raise ValueError("Left backbone-junction homology validation failed")

    duplication_marker = old_backbone[3585:3616]
    no153_marker = new_backbone[6105:6136]
    if (
        old_backbone.count(duplication_marker) != 1
        or new_backbone.count(duplication_marker) != 0
        or old_backbone.count(no153_marker) != 0
        or new_backbone.count(no153_marker) != 1
    ):
        raise ValueError("Diagnostic marker validation failed")

    records = read_fasta(source)
    old_right_length = len(old_backbone) - OLD_INSERT_INDEX
    transformed = []
    manifest_rows = []
    old_total = 0
    new_total = 0
    for name, sequence in records:
        insert_end = len(sequence) - old_right_length
        if insert_end < OLD_INSERT_INDEX:
            raise ValueError("{} is shorter than the old backbone".format(name))
        if sequence[:OLD_INSERT_INDEX] != old_backbone[:OLD_INSERT_INDEX]:
            raise ValueError("{} left old-backbone segment mismatch".format(name))
        if sequence[insert_end:] != old_backbone[OLD_INSERT_INDEX:]:
            raise ValueError("{} right old-backbone segment mismatch".format(name))
        insert = sequence[OLD_INSERT_INDEX:insert_end]
        new_sequence = (
            new_backbone[:NEW_INSERT_INDEX] + insert + new_backbone[NEW_INSERT_INDEX:]
        )
        new_insert_end = NEW_INSERT_INDEX + len(insert)
        if new_sequence[:NEW_INSERT_INDEX] != new_backbone[:NEW_INSERT_INDEX]:
            raise ValueError("{} left new-backbone segment mismatch".format(name))
        if new_sequence[new_insert_end:] != new_backbone[NEW_INSERT_INDEX:]:
            raise ValueError("{} right new-backbone segment mismatch".format(name))
        if len(sequence) - len(new_sequence) != 213:
            raise ValueError("{} did not shrink by exactly 213 bp".format(name))
        if new_sequence.count(duplication_marker) != 0:
            raise ValueError("{} retains the B7371 duplication marker".format(name))
        if new_sequence.count(no153_marker) != 1:
            raise ValueError("{} lacks the unique A7158 no-153 marker".format(name))
        transformed.append((name, new_sequence))
        old_total += len(sequence)
        new_total += len(new_sequence)
        manifest_rows.append(
            (
                name,
                len(sequence),
                len(new_sequence),
                len(insert),
                OLD_INSERT_INDEX,
                NEW_INSERT_INDEX,
                sha256_bytes(insert.encode("ascii")),
                sha256_bytes(sequence.encode("ascii")),
                sha256_bytes(new_sequence.encode("ascii")),
            )
        )

    with output.open("w", encoding="ascii", newline="\n") as handle:
        for name, sequence in transformed:
            write_record(handle, name, sequence)

    with manifest_path.open("w", encoding="ascii", newline="\n") as handle:
        handle.write(
            "record_id\told_length_bp\tnew_length_bp\tinsert_length_bp\t"
            "old_insert_index_0based\tnew_insert_index_0based\tinsert_sha256\t"
            "old_sequence_sha256\tnew_sequence_sha256\n"
        )
        for row in manifest_rows:
            handle.write("\t".join(map(str, row)) + "\n")

    reread = read_fasta(output)
    if reread != transformed:
        raise ValueError("Written FASTA differs after re-import")
    if len(records) != 1747:
        raise ValueError("Expected 1747 pGP95 records, observed {}".format(len(records)))
    expected_total = old_total - 213 * len(records)
    if new_total != expected_total:
        raise ValueError("Global base-total reconciliation failed")

    validation = {
        "status": "PASS",
        "records": len(records),
        "unique_record_ids": len(set(name for name, _ in records)),
        "old_backbone_length_bp": len(old_backbone),
        "new_backbone_length_bp": len(new_backbone),
        "old_insert_index_0based": OLD_INSERT_INDEX,
        "new_insert_index_0based": NEW_INSERT_INDEX,
        "per_record_length_change_bp": -213,
        "old_total_sequence_bases": old_total,
        "new_total_sequence_bases": new_total,
        "expected_new_total_sequence_bases": expected_total,
        "source_fasta_sha256": sha256_file(source),
        "output_fasta_sha256": sha256_file(output),
        "old_backbone_sha256": sha256_file(args.old_backbone_7371),
        "new_backbone_sha256": sha256_file(args.new_backbone_7158),
        "records_with_B7371_duplication_marker": sum(
            sequence.count(duplication_marker) > 0 for _, sequence in transformed
        ),
        "records_with_exactly_one_A7158_no153_marker": sum(
            sequence.count(no153_marker) == 1 for _, sequence in transformed
        ),
        "insert_sequences_preserved": len(records),
        "fasta_reimport_matches_generated_records": True,
    }
    validation_path.write_text(
        json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(validation, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
