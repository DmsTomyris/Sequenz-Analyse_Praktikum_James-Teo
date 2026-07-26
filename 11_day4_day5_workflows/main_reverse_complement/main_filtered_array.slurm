#!/usr/bin/env bash
#SBATCH --job-name=mainfiltpaf
#SBATCH --partition=slim16
#SBATCH --array=0-3
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --exclusive
#SBATCH --time=2-00:00:00
#SBATCH --output=logs/%x-%A_%a.out
#SBATCH --error=logs/%x-%A_%a.err
set -euo pipefail
PROJECT=/work/project/becstr_013
REF="$PROJECT/library/yeast_backbone_insert_3176.fasta"
OUT="$PROJECT/mapping_main_filtered_full_paf_optimized"
N=$(printf '%02d' "$SLURM_ARRAY_TASK_ID")
cd "$PROJECT"
module load ngs/minimap2/2.10
minimap2 -t "$SLURM_CPUS_PER_TASK" -x map-ont --secondary=no "$REF" "$OUT/chunks/chunk_${N}.fastq" > "$OUT/chunks/chunk_${N}.paf" 2> "$OUT/chunks/chunk_${N}.log"
