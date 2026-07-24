#!/usr/bin/env bash
#SBATCH --job-name=plasmid_map
#SBATCH --partition=slim18
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=24:00:00
#SBATCH --output=logs/%x-%j.out
#SBATCH --error=logs/%x-%j.err

set -euo pipefail

FLANK=${1:?Usage: sbatch mapping_run.slurm FLANK RUN_TAG}
RUN_TAG=${2:?Usage: sbatch mapping_run.slurm FLANK RUN_TAG}
PROJECT=/work/project/becstr_013
ZIP="$PROJECT/20230920_DNA_Korber_Drin3plex.zip"
ENTRY='20230920_DNA_Korber_Drin3plex/20230920_1625_2D_PAS00288_bab6ed79/fastq_pass/barcode48.fastq.gz'
REFERENCE="$PROJECT/library/yeast_backbone_insert_3176.fasta"
OUT="$PROJECT/mapping_run_${RUN_TAG}"
PYTHON=/opt/software/python-3.6/bin/python3.6

cd "$PROJECT"
module load ngs/minimap2/2.10
if [[ -e "$OUT" ]]; then
  echo "Output directory already exists: $OUT" >&2
  exit 2
fi
mkdir -p "$OUT"

unzip -tq "$ZIP" > "$OUT/zip_validation.txt"
unzip -p "$ZIP" "$ENTRY" | gzip -dc | "$PYTHON" validate_fastq_stream.py > "$OUT/fastq_validation.txt"

set -o pipefail
unzip -p "$ZIP" "$ENTRY" | gzip -dc | \
  minimap2 -t "$SLURM_CPUS_PER_TASK" -ax map-ont --secondary=yes -N 5000 -p 0.0 \
    "$REFERENCE" - 2> "$OUT/minimap2.log" | \
  "$PYTHON" aggregate_minimap2_hits.py \
    --flank "$FLANK" \
    --summary "$OUT/summary_${RUN_TAG}.tsv" \
    --technical "$OUT/technical_${RUN_TAG}.tsv" \
    > "$OUT/aggregator.log"

sha256sum "$OUT"/* > "$OUT/checksums.sha256"
