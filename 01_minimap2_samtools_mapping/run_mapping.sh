#!/usr/bin/env bash
set -euo pipefail
if [ "$#" -lt 3 ]; then
  echo "Usage: $0 READS.fastq REFERENCE.fa OUTPUT_PREFIX [THREADS]" >&2
  exit 2
fi
reads=$1
reference=$2
prefix=$3
threads=${4:-8}
mkdir -p "$(dirname "$prefix")"
minimap2 -t "$threads" -ax map-ont "$reference" "$reads" \
  | samtools sort -@ "$threads" -o "${prefix}.bam"
samtools index "${prefix}.bam"
samtools flagstat "${prefix}.bam" > "${prefix}.flagstat.txt"
samtools coverage "${prefix}.bam" > "${prefix}.coverage.txt"
