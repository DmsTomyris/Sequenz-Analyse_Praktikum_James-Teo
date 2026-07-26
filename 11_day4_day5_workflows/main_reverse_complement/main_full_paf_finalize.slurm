#!/usr/bin/env bash
#SBATCH --job-name=mainfullfinal
#SBATCH --partition=slim16
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=02:00:00
#SBATCH --output=logs/%x-%j.out
#SBATCH --error=logs/%x-%j.err
set -euo pipefail
PROJECT=/work/project/becstr_013
OUT="$PROJECT/mapping_main_full_paf_optimized"
PYTHON=/opt/software/python-3.6/bin/python3.6
cd "$PROJECT"
mapfile -t PAFS < <(find "$OUT/chunks" -maxdepth 1 -name 'chunk_*.paf' -print | sort)
[[ "${#PAFS[@]}" -eq 4 ]]
"$PYTHON" "$PROJECT/aggregate_paf_best.py" --paf "${PAFS[@]}" --hits "$OUT/best_hits.tsv" --counts "$OUT/counts_by_target.tsv"
printf 'status\tcompleted\nformat\tPAF\nsecondary\tno\nchunks\t4\n' > "$OUT/run_status.tsv"
sha256sum "$OUT"/fastq_validation.txt "$OUT"/run_metadata.tsv "$OUT"/chunks/*.fastq "$OUT"/chunks/*.paf "$OUT"/best_hits.tsv "$OUT"/counts_by_target.tsv > "$OUT/checksums.sha256"
