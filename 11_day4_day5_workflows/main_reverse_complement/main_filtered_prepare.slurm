#!/usr/bin/env bash
#SBATCH --job-name=mainfiltprep
#SBATCH --partition=slim16
#SBATCH --cpus-per-task=1
#SBATCH --mem=64G
#SBATCH --time=04:00:00
#SBATCH --output=logs/%x-%j.out
#SBATCH --error=logs/%x-%j.err
set -euo pipefail
PROJECT=/work/project/becstr_013
READS="$PROJECT/unpacked_20230920_DNA_Korber_Drin3plex/20230920_DNA_Korber_Drin3plex/20230920_1625_2D_PAS00288_bab6ed79/fastq_pass/barcode48.fastq"
OUT="$PROJECT/mapping_main_filtered_full_paf_optimized"
PYTHON=/opt/software/python-3.6/bin/python3.6
cd "$PROJECT"
if [[ -e "$OUT" ]]; then echo "Output directory exists: $OUT" >&2; exit 2; fi
mkdir -p "$OUT/chunks"
"$PYTHON" "$PROJECT/filter_full_reads.py" --input "$READS" --output "$OUT/filtered.fastq" --stats "$OUT/filter_stats.tsv"
"$PYTHON" validate_fastq_stream.py < "$OUT/filtered.fastq" > "$OUT/fastq_validation.txt"
"$PYTHON" "$PROJECT/split_fastq.py" --input "$OUT/filtered.fastq" --output-dir "$OUT/chunks" --parts 4 > "$OUT/split.log"
printf 'source\t%s\nformat\tPAF\nsecondary\tno\nchunks\t4\ncpus_per_chunk\t16\nmem_per_chunk\t64G\n' "$READS" > "$OUT/run_metadata.tsv"
