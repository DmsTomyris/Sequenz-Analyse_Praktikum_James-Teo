#!/usr/bin/env bash
set -euo pipefail
if [ "$#" -lt 3 ]; then
  echo "Usage: $0 CONTROL.fastq REFERENCE.fa OUTPUT_PREFIX" >&2
  exit 2
fi
reads=$1
reference=$2
prefix=$3
minimap2 -x sr -a "$reference" "$reads" | samtools sort -o "${prefix}.bam"
samtools index "${prefix}.bam"
samtools flagstat "${prefix}.bam" > "${prefix}.flagstat.txt"
samtools coverage "${prefix}.bam" > "${prefix}.coverage.txt"
