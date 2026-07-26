#!/usr/bin/env bash
#SBATCH --job-name=chunkfilter
#SBATCH --partition=slim16
#SBATCH --cpus-per-task=1
#SBATCH --mem=64G
#SBATCH --time=08:00:00
#SBATCH --output=logs/%x-%j.out
#SBATCH --error=logs/%x-%j.err
set -euo pipefail
PROJECT=/work/project/becstr_013
READS="$PROJECT/unpacked_20230920_DNA_Korber_Drin3plex/20230920_DNA_Korber_Drin3plex/20230920_1625_2D_PAS00288_bab6ed79/fastq_pass/barcode48.fastq"
OUT="$PROJECT/mapping_main_filtered_chunked"
PYTHON=/opt/software/python-3.6/bin/python3.6
cd "$PROJECT"
if [[ -e "$OUT" ]]; then echo "Output directory exists: $OUT" >&2; exit 2; fi
mkdir -p "$OUT"
"$PYTHON" "$PROJECT/chunked_filter_full.py" --input "$READS" --output-dir "$OUT" --block-size 1000
