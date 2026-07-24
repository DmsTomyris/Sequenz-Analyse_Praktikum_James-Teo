#!/usr/bin/env python3
"""Build normal and reversed insertions into a constant pGP564 backbone."""

import argparse
import hashlib
import re
from pathlib import Path
from typing import List, Optional, Tuple


DNA_RE = re.compile(r"^[ACGTN]+$")


def read_fasta(path: Path) -> List[Tuple[str, str]]:
    records = []
    identifier = None  # type: Optional[str]
    chunks: list[str] = []
    with path.open("r", encoding="utf-8") as handle:
        for raw in handle:
            line = raw.strip()
            if not line:
                continue
            if line.startswith(">"):
                if identifier is not None:
                    records.append((identifier, "".join(chunks).upper()))
                identifier = line[1:].split()[0]
                chunks = []
            else:
                if identifier is None:
                    raise ValueError(f"Sequence before first FASTA header in {path}")
                chunks.append(line)
    if identifier is not None:
        records.append((identifier, "".join(chunks).upper()))
    return records


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def wrap(sequence: str, width: int = 80) -> str:
    return "\n".join(sequence[i : i + width] for i in range(0, len(sequence), width))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backbone", type=Path, required=True)
    parser.add_argument("--inserts", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    if args.output.exists():
        raise FileExistsError(f"Refusing to overwrite existing output: {args.output}")
    if args.report.exists():
        raise FileExistsError(f"Refusing to overwrite existing report: {args.report}")

    backbone_records = read_fasta(args.backbone)
    insert_records = read_fasta(args.inserts)
    if len(backbone_records) != 1:
        raise ValueError(f"Expected one backbone record, found {len(backbone_records)}")
    if len(insert_records) != 1588:
        raise ValueError(f"Expected 1588 inserts, found {len(insert_records)}")

    backbone_id, backbone = backbone_records[0]
    identifiers = [identifier for identifier, _ in insert_records]
    if len(set(identifiers)) != len(identifiers):
        raise ValueError("Insert identifiers are not unique")
    if len(backbone) < 5042:
        raise ValueError("Backbone is shorter than the insertion coordinate")
    if not DNA_RE.fullmatch(backbone):
        raise ValueError("Backbone contains characters outside A/C/G/T/N")
    for identifier, sequence in insert_records:
        if not sequence or not DNA_RE.fullmatch(sequence):
            raise ValueError(f"Invalid or empty DNA sequence for {identifier}")

    prefix = backbone[:5042]
    suffix = backbone[5042:]
    temporary = args.output.with_name(args.output.name + ".partial")
    if temporary.exists():
        raise FileExistsError(f"Refusing to overwrite existing temporary output: {temporary}")

    record_count = 0
    with temporary.open("x", encoding="utf-8", newline="\n") as handle:
        for identifier, insert in insert_records:
            normal = prefix + insert + suffix
            reversed_insert = insert[::-1]
            reversed_form = prefix + reversed_insert + suffix
            handle.write(f">{identifier}\n{wrap(normal)}\n")
            handle.write(f">{identifier}-rev\n{wrap(reversed_form)}\n")
            record_count += 2

    if record_count != 3176:
        if temporary.exists():
            temporary.unlink()
        raise ValueError(f"Generated {record_count} records instead of 3176")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary.replace(args.output)
    report_text = "\n".join(
        [
            "yeast_backbone_insert_library validation",
            f"backbone_id\t{backbone_id}",
            f"backbone_length\t{len(backbone)}",
            "insertion_coordinate_1based\tbetween_5042_and_5043",
            f"insert_count\t{len(insert_records)}",
            f"output_record_count\t{record_count}",
            "reverse_definition\tsequence reversal only; no complement",
            f"output_sha256\t{sha256(args.output)}",
            f"backbone_sha256\t{sha256(args.backbone)}",
            f"inserts_sha256\t{sha256(args.inserts)}",
            "status\tPASS",
            "",
        ]
    )
    with args.report.open("w", encoding="utf-8", newline="\n") as report_handle:
        report_handle.write(report_text)
    print(report_text, end="")


if __name__ == "__main__":
    main()
