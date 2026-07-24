#!/usr/bin/env python3
import argparse
import csv
import re
import sys
from collections import defaultdict


CIGAR_RE = re.compile(r"(\d+)([MIDNSHP=X])")
REF_OPS = set("MDN=X")
ALIGNED_REF_OPS = set("M=X")


def cigar_lengths(cigar):
    ref_consumed = 0
    aligned_ref = 0
    for length, op in CIGAR_RE.findall(cigar):
        length = int(length)
        if op in REF_OPS:
            ref_consumed += length
        if op in ALIGNED_REF_OPS:
            aligned_ref += length
    return ref_consumed, aligned_ref


def sam_tag(fields, name, default):
    prefix = name + ":"
    for field in fields[11:]:
        if field.startswith(prefix):
            value = field.split(":", 2)
            if len(value) == 3:
                try:
                    return int(value[2])
                except ValueError:
                    return default
    return default


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference-length", type=int, default=7371)
    parser.add_argument("--flank", type=int, required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--technical", required=True)
    args = parser.parse_args()

    ref_lengths = {}
    best = {}
    for raw in sys.stdin:
        if raw.startswith("@SQ"):
            fields = raw.rstrip("\n").split("\t")
            name = next((x[3:] for x in fields if x.startswith("SN:")), None)
            length = next((x[3:] for x in fields if x.startswith("LN:")), None)
            if name and length:
                ref_lengths[name] = int(length)
            continue
        if raw.startswith("@"):
            continue
        fields = raw.rstrip("\n").split("\t")
        if len(fields) < 11:
            continue
        read_id = fields[0]
        flag = int(fields[1])
        if flag & 4 or fields[2] == "*" or fields[5] == "*":
            continue
        reference_id = fields[2]
        if reference_id.endswith("-rev"):
            orientation = "reverse"
            insert_id = reference_id[:-4]
        else:
            orientation = "normal"
            insert_id = reference_id
        if reference_id not in ref_lengths:
            continue
        insert_length = ref_lengths[reference_id] - args.reference_length
        if insert_length <= 0:
            continue
        ref_start0 = int(fields[3]) - 1
        ref_consumed, aligned_ref = cigar_lengths(fields[5])
        ref_end0 = ref_start0 + ref_consumed
        left_boundary = args.reference_length
        right_boundary = args.reference_length + insert_length
        left_flank = 0
        right_flank = 0
        if ref_start0 < left_boundary < ref_end0:
            left_flank = min(left_boundary - ref_start0, ref_end0 - left_boundary)
        if ref_start0 < right_boundary < ref_end0:
            right_flank = min(right_boundary - ref_start0, ref_end0 - right_boundary)
        if max(left_flank, right_flank) < args.flank:
            continue
        score = sam_tag(fields, "AS", -1)
        mapq = int(fields[4])
        key = (read_id, reference_id)
        rank = (score, mapq, aligned_ref, -ref_start0, -ref_end0)
        candidate = (rank, reference_id, insert_id, orientation, score, mapq,
                     ref_start0 + 1, ref_end0, ref_lengths[reference_id],
                     left_flank, right_flank)
        if key not in best or rank > best[key][0]:
            best[key] = candidate

    counts = defaultdict(lambda: [0, 0])
    for reference_id in ref_lengths:
        insert_id = reference_id[:-4] if reference_id.endswith("-rev") else reference_id
        counts[insert_id]
    with open(args.technical, "w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow([
            "read_id", "insert_id", "artificial_reference_id", "orientation",
            "alignment_score", "mapping_quality", "reference_start_1based",
            "reference_end_1based_exclusive", "reference_length",
            "left_junction_flank", "right_junction_flank", "qualifying_junction"
        ])
        for key in sorted(best):
            read_id, reference_id = key
            item = best[key]
            _, reference_id, insert_id, orientation, score, mapq, ref_start, ref_end, ref_length, left_flank, right_flank = item
            writer.writerow([read_id, insert_id, reference_id, orientation, score, mapq,
                             ref_start, ref_end, ref_length, left_flank, right_flank, "PASS"])
            counts[insert_id][0 if orientation == "normal" else 1] += 1

    with open(args.summary, "w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["insert_id", "normal_reads", "reverse_reads", "normal_percent", "reverse_percent"])
        for insert_id in sorted(counts):
            normal, reverse = counts[insert_id]
            total = normal + reverse
            if total:
                normal_pct = "{:.6f}".format(100.0 * normal / total)
                reverse_pct = "{:.6f}".format(100.0 * reverse / total)
            else:
                normal_pct = "NA"
                reverse_pct = "NA"
            writer.writerow([insert_id, normal, reverse, normal_pct, reverse_pct])
    print("best_read_reference_hits\t{}".format(len(best)))
    print("insert_rows_with_hits\t{}".format(len(counts)))
    print("flank_bp\t{}".format(args.flank))


if __name__ == "__main__":
    main()
