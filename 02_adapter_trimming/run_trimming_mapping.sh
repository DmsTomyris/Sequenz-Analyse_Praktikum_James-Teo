#!/usr/bin/env bash
set -euo pipefail
if [ "$#" -lt 3 ]; then
  echo "Usage: $0 INPUT.fastq REFERENCE.fa OUTPUT_PREFIX" >&2
  exit 2
fi
input=$1
reference=$2
prefix=$3
trimmed="${prefix}.trimmed.fastq"
cutadapt -g ACACGACGCTCTTCCGATCT -m 30 -o "$trimmed" "$input" > "${prefix}.cutadapt.txt"
minimap2 -ax map-ont "$reference" "$trimmed" | samtools sort -o "${prefix}.bam"
samtools index "${prefix}.bam"
samtools flagstat "${prefix}.bam" > "${prefix}.flagstat.txt"
samtools coverage "${prefix}.bam" > "${prefix}.coverage.txt"
