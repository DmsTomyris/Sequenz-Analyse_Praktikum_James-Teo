#!/usr/bin/env python3
"""Filter SAM records to alignments spanning a plasmid junction with evidence."""

from __future__ import print_function

import argparse
import re
import sys


CIGAR_RE = re.compile(r"(\d+)([MIDNSHP=X])")


def read_junctions(path):
    junctions = {}
    with open(path, "r") as handle:
        header = handle.readline().rstrip("\n\r").split("\t")
        for raw in handle:
            if not raw.strip():
                continue
            row = dict(zip(header, raw.rstrip("\n\r").split("\t")))
            junctions[row["chromosome_id"]] = (
                int(row["left_junction_0based"]),
                int(row["right_junction_0based"]),
            )
    return junctions


def aligned_bases_in_interval(blocks, start, end):
    total = 0
    for block_start, block_end in blocks:
        total += max(0, min(block_end, end) - max(block_start, start))
    return total


def aligned_blocks(pos0, cigar):
    reference = pos0
    blocks = []
    parsed = CIGAR_RE.findall(cigar)
    if not parsed or "".join(length + op for length, op in parsed) != cigar:
        return []
    for length_text, op in parsed:
        length = int(length_text)
        if op in ("M", "=", "X"):
            blocks.append((reference, reference + length))
            reference += length
        elif op in ("D", "N"):
            reference += length
        elif op in ("I", "S", "H", "P"):
            continue
    return blocks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--junctions", required=True)
    parser.add_argument("--min-mapq", type=int, default=20)
    parser.add_argument("--flank-bases", type=int, default=50)
    args = parser.parse_args()
    junctions = read_junctions(args.junctions)
    kept = 0
    examined = 0
    for raw in sys.stdin:
        if raw.startswith("@"):
            sys.stdout.write(raw)
            continue
        fields = raw.rstrip("\n\r").split("\t")
        if len(fields) < 11:
            continue
        examined += 1
        flag = int(fields[1])
        if flag & 0x4 or flag & 0x100:
            continue
        chromosome = fields[2]
        if chromosome not in junctions or int(fields[4]) < args.min_mapq:
            continue
        blocks = aligned_blocks(int(fields[3]) - 1, fields[5])
        if not blocks:
            continue
        passed = False
        for junction in junctions[chromosome]:
            left = aligned_bases_in_interval(
                blocks, junction - args.flank_bases, junction
            )
            right = aligned_bases_in_interval(
                blocks, junction, junction + args.flank_bases
            )
            if left >= args.flank_bases and right >= args.flank_bases:
                passed = True
                break
        if passed:
            sys.stdout.write(raw)
            kept += 1
    print(
        "examined_records\t{}\nkept_records\t{}".format(examined, kept),
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
