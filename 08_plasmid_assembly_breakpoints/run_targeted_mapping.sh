#!/usr/bin/env bash
set -euo pipefail
export PATH=/home/teo-helmer/.local/bin:$PATH
OUT=/mnt/c/Users/teohe/OneDrive/Desktop/.AAAA-Praktikum/Day2/plasmid_assembly_workflow
READS=/mnt/c/Users/teohe/OneDrive/Desktop/.AAAA-Praktikum/dorado_reads.fastq
samtools faidx "$OUT/targeted_reference.fa"
minimap2 -t 8 -ax map-ont --sam-hit-only "$OUT/targeted_reference.fa" "$READS" | samtools sort -@ 4 -o "$OUT/mapped_plasmids.bam"
samtools index "$OUT/mapped_plasmids.bam"
samtools flagstat "$OUT/mapped_plasmids.bam" > "$OUT/mapped_plasmids.flagstat.txt"
samtools coverage "$OUT/mapped_plasmids.bam" > "$OUT/mapped_plasmids.coverage.txt"
