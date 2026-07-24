#!/usr/bin/env bash
set -euo pipefail
if [ "$#" -lt 3 ]; then
  echo "Usage: $0 UNMAPPED.fastq REFERENCE.fa OUTPUT_DIR" >&2
  exit 2
fi
unmapped=$1
reference=$2
outdir=$3
mkdir -p "$outdir"
seqkit fq2fa "$unmapped" -o "$outdir/unmapped.fasta"
makeblastdb -in "$reference" -dbtype nucl -out "$outdir/reference_db"
blastn -task blastn-short -query "$outdir/unmapped.fasta" -db "$outdir/reference_db" \
  -word_size 11 -evalue 1e-5 -outfmt '6 qseqid sseqid pident length qlen qstart qend sstart send evalue bitscore' \
  -out "$outdir/hits.tsv"
