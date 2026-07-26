#!/usr/bin/env bash
#SBATCH --job-name=dir_ucsc_map
#SBATCH --partition=slim18
#SBATCH --array=0-15%4
#SBATCH --cpus-per-task=16
#SBATCH --mem=48G
#SBATCH --time=1-00:00:00
#SBATCH --output=/work/project/becstr_013/directional_ucsc_work/logs/map-%A_%a.out
#SBATCH --error=/work/project/becstr_013/directional_ucsc_work/logs/map-%A_%a.err

set -euo pipefail

BASE=/work/project/becstr_013
ROOT="$BASE/genome_build_direction_thresholds"
CHUNKS="$BASE/mapping_main_full_paf_optimized/chunks"
ASSEMBLIES=(pGP85 scR64pGP85 pGP95 scR64pGP95)
ASSEMBLY_INDEX=$((SLURM_ARRAY_TASK_ID / 4))
CHUNK_INDEX=$((SLURM_ARRAY_TASK_ID % 4))
ASSEMBLY="${ASSEMBLIES[$ASSEMBLY_INDEX]}"
CHUNK=$(printf 'chunk_%02d' "$CHUNK_INDEX")
REFERENCE="$ROOT/ucsc_hub/assemblies/$ASSEMBLY/source/$ASSEMBLY.fasta"
INPUT="$CHUNKS/$CHUNK.fastq"
WORK="$ROOT/mapping_work/$ASSEMBLY"
OUTPUT="$WORK/$CHUNK.bam"
TMP="$WORK/.${CHUNK}.${SLURM_JOB_ID}"

module load ngs/minimap2/2.10
module load ngs/samtools/1.8

test -e "$ROOT/BUILD_DONE"
test -s "$REFERENCE"
test -s "$INPUT"
mkdir -p "$WORK"
test ! -e "$OUTPUT"
mkdir -p "$TMP"
trap 'rm -rf -- "$TMP"' EXIT

minimap2 \
  -t "$SLURM_CPUS_PER_TASK" \
  -ax map-ont \
  --secondary=no \
  "$REFERENCE" \
  "$INPUT" \
  2> "$WORK/$CHUNK.minimap2.log" \
  | samtools sort \
      -@ "$SLURM_CPUS_PER_TASK" \
      -T "$TMP/sort" \
      -o "$TMP/output.bam" \
      -

samtools quickcheck -v "$TMP/output.bam"
samtools index "$TMP/output.bam"
mv "$TMP/output.bam" "$OUTPUT"
mv "$TMP/output.bam.bai" "$OUTPUT.bai"
{
  printf 'status\tCOMPLETED\n'
  printf 'assembly\t%s\n' "$ASSEMBLY"
  printf 'chunk\t%s\n' "$CHUNK"
  printf 'job_id\t%s\n' "$SLURM_JOB_ID"
  printf 'minimap2_version\t%s\n' "$(minimap2 --version)"
  printf 'samtools_version\t%s\n' "$(samtools --version | head -1)"
  printf 'preset\tmap-ont\n'
  printf 'secondary\tno\n'
  printf 'cpus\t%s\n' "$SLURM_CPUS_PER_TASK"
} > "$WORK/$CHUNK.status.tsv"
sha256sum "$OUTPUT" "$OUTPUT.bai" > "$WORK/$CHUNK.checksums.sha256"
