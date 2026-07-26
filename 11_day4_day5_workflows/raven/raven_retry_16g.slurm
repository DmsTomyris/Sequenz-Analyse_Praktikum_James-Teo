#!/usr/bin/env bash
# Raven retry for inserts without a usable FASTA+GFA result.
#SBATCH --job-name=raven16g_retry
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
RAVEN_ENV="$BASE/miniforge3/envs/ravenasm"
ROOT="$PROJECT/raven_1588_retry16g_20260726"
MANIFEST="$ROOT/restart_manifest.tsv"
BACKBONE="$PROJECT/references/pGP564_full_backbone.fa"
SPLIT="$PROJECT/split_reconstructed/inserts"
RAVEN="$RAVEN_ENV/bin/raven"

row=$(awk -v n="$SLURM_ARRAY_TASK_ID" 'NR==n+1{print;exit}' "$MANIFEST")
IFS=$'\t' read -r index insert_id insert_bp expected_bp genome_size <<< "$row"
test -n "$insert_id"
insert="$SPLIT/${insert_id}.fasta"
out="$ROOT/$insert_id"
mkdir -p "$out"

on_error() {
  rc=$?
  if (( rc != 0 )); then
    printf 'insert_id\t%s\nstatus\tFAILED\nexit_code\t%s\nworkflow_version\traven_16G_retry_v1\n' "$insert_id" "$rc" > "$out/status.tsv"
  fi
}
trap on_error EXIT

test -x "$RAVEN"
test -s "$BACKBONE"
test -s "$insert"
{
  printf 'insert_id\t%s\nstatus\tRUNNING\nworkflow_version\traven_16G_retry_v1\n' "$insert_id"
  printf 'assembler\tRaven 1.8.3\nbackbone_input\t%s\ninsert_reads_input\t%s\n' "$BACKBONE" "$insert"
  printf 'identity_threshold\t0\nmax_overlaps\t64\nmin_unitig_size\t1000\npolishing_rounds\t1\nallocated_cpus\t%s\nallocated_memory\t16G\n' "$SLURM_CPUS_PER_TASK"
} > "$out/status.tsv"

"$RAVEN" --threads "$SLURM_CPUS_PER_TASK" --identity 0 --kMaxNumOverlaps 64 --min-unitig-size 1000 --polishing-rounds 1 --graphical-fragment-assembly "$out/assembly_graph.gfa" "$BACKBONE" "$insert" > "$out/assembly.fasta" 2> "$out/raven.stderr.log"
test -s "$out/assembly.fasta"
"$RAVEN" --version > "$out/raven.version.txt"
printf 'insert_id\t%s\nstatus\tCOMPLETED\nworkflow_version\traven_16G_retry_v1\nassembler\tRaven 1.8.3\n' "$insert_id" > "$out/status.tsv"
sha256sum "$out/assembly.fasta" "$out/assembly_graph.gfa" > "$out/checksums.sha256"
