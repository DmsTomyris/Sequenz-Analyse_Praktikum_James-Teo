#!/usr/bin/env bash
set -euo pipefail
if [ "$#" -lt 3 ]; then
  echo "Usage: $0 READS.fastq SPECIES_REFERENCE.fa OUTPUT_PREFIX [PRESET]" >&2
  exit 2
fi
reads=$1
reference=$2
prefix=$3
preset=${4:-map-ont}
minimap2 -ax "$preset" "$reference" "$reads" | samtools sort -o "${prefix}.bam"
samtools index "${prefix}.bam"
samtools flagstat "${prefix}.bam" > "${prefix}.flagstat.txt"
samtools coverage "${prefix}.bam" > "${prefix}.coverage.txt"
