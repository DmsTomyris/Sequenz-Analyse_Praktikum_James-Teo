#!/usr/bin/env bash
#SBATCH --job-name=dir_ucsc_fin
#SBATCH --partition=slim18
#SBATCH --array=0-3%4
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=1-00:00:00
#SBATCH --output=/work/project/becstr_013/directional_ucsc_work/logs/finalize-%A_%a.out
#SBATCH --error=/work/project/becstr_013/directional_ucsc_work/logs/finalize-%A_%a.err

set -euo pipefail

BASE=/work/project/becstr_013
ROOT="$BASE/genome_build_direction_thresholds"
SCRIPTS="$ROOT/scripts"
TOOLS="$BASE/directional_ucsc_work/tools"
ASSEMBLIES=(pGP85 scR64pGP85 pGP95 scR64pGP95)
ASSEMBLY="${ASSEMBLIES[$SLURM_ARRAY_TASK_ID]}"
WORK="$ROOT/mapping_work/$ASSEMBLY"
ASSEMBLY_DIR="$ROOT/ucsc_hub/assemblies/$ASSEMBLY"
TRACKS="$ASSEMBLY_DIR/tracks"
CHROM_SIZES="$ASSEMBLY_DIR/$ASSEMBLY.chrom.sizes"
PYTHON=/opt/software/python-3.6/bin/python3.6

module load ngs/samtools/1.8

for index in 0 1 2 3; do
  chunk=$(printf 'chunk_%02d' "$index")
  test -s "$WORK/$chunk.bam"
  test -s "$WORK/$chunk.bam.bai"
done
test ! -e "$TRACKS/raw_primary.bam"

TMP="$WORK/.finalize.${SLURM_JOB_ID}"
mkdir -p "$TMP"
trap 'rm -rf -- "$TMP"' EXIT

samtools merge \
  -@ "$SLURM_CPUS_PER_TASK" \
  -f "$TMP/raw_primary.bam" \
  "$WORK/chunk_00.bam" "$WORK/chunk_01.bam" \
  "$WORK/chunk_02.bam" "$WORK/chunk_03.bam"
samtools index "$TMP/raw_primary.bam"
samtools quickcheck -v "$TMP/raw_primary.bam"

samtools view \
  -@ "$SLURM_CPUS_PER_TASK" \
  -b -q 20 \
  -o "$TMP/mapq20.bam" \
  "$TMP/raw_primary.bam"
samtools index "$TMP/mapq20.bam"
samtools quickcheck -v "$TMP/mapq20.bam"

samtools view -h "$TMP/raw_primary.bam" \
  | "$PYTHON" "$SCRIPTS/filter_junction_sam.py" \
      --junctions "$ASSEMBLY_DIR/junctions.tsv" \
      --min-mapq 20 \
      --flank-bases 50 \
      2> "$TMP/junction_filter_stats.tsv" \
  | samtools view -b - \
  | samtools sort \
      -@ "$SLURM_CPUS_PER_TASK" \
      -T "$TMP/junction.sort" \
      -o "$TMP/junction_evidence.bam" -
samtools index "$TMP/junction_evidence.bam"
samtools quickcheck -v "$TMP/junction_evidence.bam"

make_coverage() {
  local bam=$1
  local label=$2
  samtools depth -aa "$bam" \
    | "$PYTHON" "$SCRIPTS/coverage_to_bedgraph.py" \
    > "$TMP/$label.bedGraph"
  "$TOOLS/bedGraphToBigWig" \
    "$TMP/$label.bedGraph" \
    "$CHROM_SIZES" \
    "$TMP/$label.bw"
}

make_coverage "$TMP/raw_primary.bam" raw_coverage
make_coverage "$TMP/mapq20.bam" mapq20_coverage
make_coverage "$TMP/junction_evidence.bam" junction_coverage

for file in \
  raw_primary.bam raw_primary.bam.bai \
  mapq20.bam mapq20.bam.bai \
  junction_evidence.bam junction_evidence.bam.bai \
  raw_coverage.bw mapq20_coverage.bw junction_coverage.bw
do
  mv "$TMP/$file" "$TRACKS/$file"
done
mv "$TMP/junction_filter_stats.tsv" "$WORK/junction_filter_stats.tsv"

samtools flagstat "$TRACKS/raw_primary.bam" > "$WORK/raw_primary.flagstat.txt"
samtools flagstat "$TRACKS/mapq20.bam" > "$WORK/mapq20.flagstat.txt"
samtools flagstat "$TRACKS/junction_evidence.bam" > "$WORK/junction_evidence.flagstat.txt"
samtools idxstats "$TRACKS/raw_primary.bam" > "$WORK/raw_primary.idxstats.tsv"
sha256sum "$TRACKS"/*.bam "$TRACKS"/*.bai "$TRACKS"/*.bw \
  > "$WORK/final_track_checksums.sha256"
{
  printf 'status\tCOMPLETED\n'
  printf 'assembly\t%s\n' "$ASSEMBLY"
  printf 'job_id\t%s\n' "$SLURM_JOB_ID"
  printf 'raw_bam\t%s\n' "$TRACKS/raw_primary.bam"
  printf 'mapq20_bam\t%s\n' "$TRACKS/mapq20.bam"
  printf 'junction_bam\t%s\n' "$TRACKS/junction_evidence.bam"
} > "$WORK/finalize.status.tsv"
touch "$WORK/FINAL_DONE"
