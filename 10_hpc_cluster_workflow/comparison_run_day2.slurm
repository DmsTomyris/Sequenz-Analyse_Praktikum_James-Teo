#!/usr/bin/env bash
#SBATCH --job-name=day2_compare
#SBATCH --partition=slim18
#SBATCH --cpus-per-task=32
#SBATCH --mem=64G
#SBATCH --time=24:00:00
#SBATCH --output=logs/%x-%j.out
#SBATCH --error=logs/%x-%j.err

set -euo pipefail

PROJECT=/work/project/becstr_013
SCRIPT_DIR="$PROJECT/comparison_day2"
ZIP="$PROJECT/20230920_DNA_Korber_Drin3plex.zip"
ENTRY='20230920_DNA_Korber_Drin3plex/20230920_1625_2D_PAS00288_bab6ed79/fastq_pass/barcode48.fastq.gz'
REFERENCE="$PROJECT/comparison_day2/targeted_reference.fa"
OUT="$PROJECT/comparison_day2/run_324000_retry"
PYTHON=/opt/software/python-3.6/bin/python3.6
NREADS=324000

cd "$PROJECT"
module load ngs/minimap2/2.10

if [[ -e "$OUT" ]]; then
  echo "Output directory already exists: $OUT" >&2
  exit 2
fi
mkdir -p "$OUT"

unzip -tq "$ZIP" > "$OUT/zip_validation.txt"
unzip -p "$ZIP" "$ENTRY" | gzip -dc | \
  "$PYTHON" "$SCRIPT_DIR/subset_fastq.py" --records "$NREADS" --output "$OUT/reads_324000.fastq" \
  > "$OUT/subset.log"

set -o pipefail
minimap2 -t "$SLURM_CPUS_PER_TASK" -ax map-ont --sam-hit-only \
  "$REFERENCE" "$OUT/reads_324000.fastq" 2> "$OUT/minimap2.log" | \
  samtools sort -@ 8 -o "$OUT/targeted_reference.map-ont.bam"

samtools index "$OUT/targeted_reference.map-ont.bam"
samtools flagstat "$OUT/targeted_reference.map-ont.bam" > "$OUT/targeted_reference.map-ont.flagstat.txt"
samtools coverage "$OUT/targeted_reference.map-ont.bam" > "$OUT/targeted_reference.map-ont.coverage.txt"

"$PYTHON" "$SCRIPT_DIR/extract_junction_mappings.py" \
  --bam "$OUT/targeted_reference.map-ont.bam" \
  --fastq "$OUT/reads_324000.fastq" \
  --reference "$REFERENCE" \
  --output "$OUT/junction_mappings.tsv" \
  > "$OUT/junction_summary.txt"

sha256sum "$OUT"/* > "$OUT/checksums.sha256"
