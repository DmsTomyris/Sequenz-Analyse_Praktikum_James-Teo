#!/usr/bin/env python3
import argparse
import csv
import re
import subprocess
from collections import defaultdict

CIGAR_RE = re.compile(r"(\d+)([MIDNSHP=X])")
QUERY_OPS = set("MIS=XH")
REF_OPS = set("MDN=X")


def read_fastq_lengths(path):
    lengths = {}
    with open(path, encoding="utf-8", errors="replace") as handle:
        while True:
            header = handle.readline()
            if not header:
                break
            sequence = handle.readline().strip()
            handle.readline()
            handle.readline()
            read_id = header[1:].split()[0]
            lengths[read_id] = len(sequence)
    return lengths


def read_fasta_lengths(path):
    lengths = {}
    name = None
    length = 0
    with open(path, encoding="utf-8", errors="replace") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            if line.startswith(">"):
                if name is not None:
                    lengths[name] = length
                name = line[1:].split()[0]
                length = 0
            else:
                length += len(line)
    if name is not None:
        lengths[name] = length
    return lengths


def intervals(pos, cigar):
    query_pos = 0
    ref_pos = pos
    query_start = None
    query_end = None
    ref_start = None
    ref_end = None
    for length_text, op in CIGAR_RE.findall(cigar):
        length = int(length_text)
        if op in QUERY_OPS:
            if op in "M=X":
                if query_start is None:
                    query_start = query_pos + 1
                query_end = query_pos + length
            query_pos += length
        if op in REF_OPS:
            if op in "M=X":
                if ref_start is None:
                    ref_start = ref_pos
                ref_end = ref_pos + length - 1
            ref_pos += length
    if query_start is None or ref_start is None:
        return None
    return query_start, query_end, ref_start, ref_end


def original_read_interval(start, end, read_length, flag):
    if flag & 16:
        return read_length - end + 1, read_length - start + 1
    return start, end


def gap_length(first_start, first_end, second_start, second_end):
    if first_end < second_start:
        return second_start - first_end - 1
    if second_end < first_start:
        return first_start - second_end - 1
    return 0


def signed_gap_length(first_start, first_end, second_start, second_end):
    if first_end < second_start:
        return second_start - first_end - 1
    if second_end < first_start:
        return first_start - second_end - 1
    return -(min(first_end, second_end) - max(first_start, second_start) + 1)


def parse_alignments(bam, reference, read_lengths, include_secondary=False):
    by_read = defaultdict(lambda: {"backbone": [], "insert": []})
    command = ["samtools", "view", "-F", "4", bam]
    with subprocess.Popen(command, stdout=subprocess.PIPE, text=True) as proc:
        for line in proc.stdout:
            fields = line.rstrip("\n").split("\t")
            if len(fields) < 11:
                continue
            read_id, flag_text, ref_name, pos_text, mapq_text, cigar = fields[:6]
            flag = int(flag_text)
            if flag & 256 and not include_secondary:  # optional alternative-hit filter
                continue
            if cigar == "*":
                continue
            iv = intervals(int(pos_text), cigar)
            if iv is None:
                continue
            read_length = read_lengths.get(read_id, 0)
            query_start, query_end = original_read_interval(
                iv[0], iv[1], read_length, flag
            )
            record = {
                "read_id": read_id,
                "ref_name": ref_name,
                "query_start": query_start,
                "query_end": query_end,
                "ref_start": iv[2],
                "ref_end": iv[3],
                "mapq": int(mapq_text),
                "flag": flag,
                "cigar": cigar,
                "read_length": read_length,
            }
            by_read[read_id]["backbone" if ref_name == "pGP564" else "insert"].append(record)
        return_code = proc.wait()
    if return_code:
        raise RuntimeError(f"samtools view failed with exit code {return_code}")
    return by_read


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bam", required=True)
    parser.add_argument("--fastq", required=True)
    parser.add_argument("--reference", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--include-secondary", action="store_true")
    args = parser.parse_args()

    read_lengths = read_fastq_lengths(args.fastq)
    reference_lengths = read_fasta_lengths(args.reference)
    by_read = parse_alignments(args.bam, args.bam, read_lengths, args.include_secondary)
    rows = []
    for read_id, groups in by_read.items():
        if not groups["backbone"] or not groups["insert"]:
            continue
        for backbone in groups["backbone"]:
            for insert in groups["insert"]:
                rows.append({
                    "read_id": read_id,
                    "read_length": backbone["read_length"],
                    "read_on_backbone": f"{backbone['query_start']}_{backbone['query_end']}",
                    "backbone_on_reference": f"{backbone['ref_start']}_{backbone['ref_end']}",
                    "read_on_insert": f"{insert['query_start']}_{insert['query_end']}",
                    "insert_name": insert["ref_name"],
                    "insert_on_reference": f"{insert['ref_start']}_{insert['ref_end']}",
                    "insert_length": reference_lengths[insert["ref_name"]],
                    "gap_length": gap_length(
                        backbone["query_start"], backbone["query_end"],
                        insert["query_start"], insert["query_end"],
                    ),
                    "gap_length_signed": (
                        lambda value: "+" if value > 0 else str(value)
                    )(signed_gap_length(
                        backbone["query_start"], backbone["query_end"],
                        insert["query_start"], insert["query_end"],
                    )),
                    "backbone_mapq": backbone["mapq"],
                    "insert_mapq": insert["mapq"],
                })
    rows.sort(key=lambda row: (row["read_id"], row["read_on_backbone"], row["read_on_insert"]))
    fieldnames = [
        "read_id", "read_length", "read_on_backbone", "backbone_on_reference",
        "read_on_insert", "insert_name", "insert_on_reference", "insert_length",
        "gap_length", "gap_length_signed", "backbone_mapq", "insert_mapq",
    ]
    with open(args.output, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)
    print(f"reads_in_fastq\t{len(read_lengths)}")
    print(f"reads_with_backbone_and_insert\t{len({row['read_id'] for row in rows})}")
    print(f"alignment_pairs\t{len(rows)}")


if __name__ == "__main__":
    main()
