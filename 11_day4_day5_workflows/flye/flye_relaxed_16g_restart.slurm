#!/usr/bin/env bash
# Retry workflow for all non-completed relaxed-Flye inserts.
# The original completed assemblies remain in flye_relaxed_1588_v2.
#SBATCH --job-name=flye16g_retry
#SBATCH --partition=slim16,slim18
#SBATCH --array=1-1%100
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --time=12:00:00
#SBATCH --output=logs/%x-%A_%a.out
#SBATCH --error=logs/%x-%A_%a.err
set -Eeuo pipefail

BASE=/work/project/becstr_013
PROJECT="$BASE/cluster2_flye_work"
ENV="$BASE/miniforge3/envs/flye"
ROOT="$PROJECT/flye_relaxed_1588_v3"
MANIFEST="$ROOT/restart_manifest.tsv"
BACKBONE="$PROJECT/references/pGP564_full_backbone.fa"
SPLIT="$PROJECT/split_reconstructed/inserts"
export PATH="$ENV/bin:$PATH"

row=$(awk -v n="$SLURM_ARRAY_TASK_ID" 'NR == n + 1 {print; exit}' "$MANIFEST")
IFS=$'\t' read -r index insert_id insert_bp expected_bp genome_size <<< "$row"
test -n "$insert_id"
insert="$SPLIT/${insert_id}.fasta"
out="$ROOT/$insert_id"
mkdir -p "$out"

on_error() {
  rc=$?
  if (( rc != 0 )); then
    printf 'insert_id\t%s\nstatus\tFAILED\nexit_code\t%s\n' "$insert_id" "$rc" > "$out/status.tsv"
  fi
}
trap on_error EXIT

test -x "$ENV/bin/flye"
test -s "$BACKBONE"
test -s "$insert"

{
  printf 'insert_id\t%s\n' "$insert_id"
  printf 'status\tRUNNING\n'
  printf 'workflow_version\tflye_relaxed_16G_retry_v1\n'
  printf 'min_overlap\t1000\nmode\tmeta\nkeep_haplotypes\tYES\nalt_contigs\tRETAINED\n'
  printf 'backbone_input\t%s\ninsert_reads_input\t%s\n' "$BACKBONE" "$insert"
  printf 'allocated_cpus\t%s\nallocated_memory\t16G\nexpected_plasmid_bp\t%s\n' "$SLURM_CPUS_PER_TASK" "$expected_bp"
} > "$out/status.tsv"

flye --nano-raw "$BACKBONE" "$insert" \
  --genome-size "$genome_size" \
  --min-overlap 1000 \
  --meta \
  --keep-haplotypes \
  --out-dir "$out/assembly" \
  --threads "$SLURM_CPUS_PER_TASK" \
  > "$out/flye.stdout.log" 2> "$out/flye.stderr.log"

test -s "$out/assembly/assembly.fasta"
flye --version > "$out/flye.version.txt"
printf 'insert_id\t%s\nstatus\tCOMPLETED\nworkflow_version\tflye_relaxed_16G_retry_v1\n' "$insert_id" > "$out/status.tsv"
find "$out" -maxdepth 2 -type f -print0 | xargs -0 sha256sum > "$out/checksums.sha256"
