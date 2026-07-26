#!/usr/bin/env bash
#SBATCH --job-name=mainfullprep
#SBATCH --partition=slim16
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --time=02:00:00
#SBATCH --output=logs/%x-%j.out
#SBATCH --error=logs/%x-%j.err
set -euo pipefail
PROJECT=/work/project/becstr_013
READS="$PROJECT/unpacked_20230920_DNA_Korber_Drin3plex/20230920_DNA_Korber_Drin3plex/20230920_1625_2D_PAS00288_bab6ed79/fastq_pass/barcode48.fastq"
OUT="$PROJECT/mapping_main_full_paf_optimized"
PYTHON=/opt/software/python-3.6/bin/python3.6
cd "$PROJECT"
if [[ -e "$OUT" ]]; then echo "Output directory exists: $OUT" >&2; exit 2; fi
mkdir -p "$OUT/chunks"
"$PYTHON" validate_fastq_stream.py < "$READS" > "$OUT/fastq_validation.txt"
"$PYTHON" "$PROJECT/split_fastq.py" --input "$READS" --output-dir "$OUT/chunks" --parts 4 > "$OUT/split.log"
printf 'input\t%s\nchunks\t4\nformat\tPAF\nsecondary\tno\nreference\t%s\n' "$READS" "$PROJECT/library/yeast_backbone_insert_3176.fasta" > "$OUT/run_metadata.tsv"
