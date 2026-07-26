#!/usr/bin/env python3
"""Condense `samtools depth -aa` output into non-zero bedGraph intervals."""

from __future__ import print_function

import sys


def emit(chromosome, start0, end0, depth):
    if chromosome is not None and depth > 0 and start0 < end0:
        sys.stdout.write("{}\t{}\t{}\t{}\n".format(
            chromosome, start0, end0, depth
        ))


def main():
    current_chrom = None
    interval_start = None
    interval_end = None
    current_depth = None
    for raw in sys.stdin:
        if not raw.strip():
            continue
        chromosome, position, depth_text = raw.rstrip("\n\r").split("\t")[:3]
        start0 = int(position) - 1
        depth = int(depth_text)
        if (
            chromosome == current_chrom
            and start0 == interval_end
            and depth == current_depth
        ):
            interval_end += 1
            continue
        emit(current_chrom, interval_start, interval_end, current_depth)
        current_chrom = chromosome
        interval_start = start0
        interval_end = start0 + 1
        current_depth = depth
    emit(current_chrom, interval_start, interval_end, current_depth)


if __name__ == "__main__":
    main()
