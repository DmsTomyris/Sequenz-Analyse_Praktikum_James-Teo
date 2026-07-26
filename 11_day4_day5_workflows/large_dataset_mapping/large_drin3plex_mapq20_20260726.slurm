#!/usr/bin/env bash
#SBATCH --job-name=drin3plex_mapq20
#SBATCH --partition=slim18
#SBATCH --array=0-2%3
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=2-00:00:00
#SBATCH --output=/work/project/becstr_013/large_drin3plex_mapq20_20260726/logs/%A_%a.out
#SBATCH --error=/work/project/becstr_013/large_drin3plex_mapq20_20260726/logs/%A_%a.err
set -euo pipefail

module load ngs/minimap2/2.10
module load ngs/samtools/1.8

WORK=/work/project/becstr_013/large_drin3plex_mapq20_20260726
READS=/work/project/becstr_013/unpacked_20230920_DNA_Korber_Drin3plex/20230920_DNA_Korber_Drin3plex/20230920_1625_2D_PAS00288_bab6ed79/fastq_pass/barcode48.fastq
P85=/work/project/becstr_013/genome_build_direction_thresholds/ucsc_hub/assemblies/pGP85/source/pGP85.fasta
P95=/work/project/becstr_013/genome_build_direction_thresholds/ucsc_hub/assemblies/pGP95/source/pGP95.fasta
COMBINED=$WORK/yeast_plus_backbone.fa

targets=(pGP85 pGP95 yeast_plus_backbone)
refs=($P85 $P95 $COMBINED)
target=${targets[$SLURM_ARRAY_TASK_ID]}
ref=${refs[$SLURM_ARRAY_TASK_ID]}
mkdir -p "$WORK/bam" "$WORK/metrics" "$WORK/logs"

tmp=${SLURM_TMPDIR:-$WORK/tmp_${SLURM_JOB_ID}_${SLURM_ARRAY_TASK_ID}}
mkdir -p "$tmp"
trap 'rm -rf "$tmp"' EXIT

printf 'target\t%s\nreference\t%s\nreads\t%s\nminimap2\t%s\nsamtools\t%s\nmapq_threshold\t20\n' \
  "$target" "$ref" "$READS" "$(minimap2 --version)" "$(samtools --version | head -1)" > "$WORK/metrics/${target}.metadata.tsv"

minimap2 -t "$SLURM_CPUS_PER_TASK" -ax map-ont --secondary=no "$ref" "$READS" \
  2> "$WORK/logs/${target}.minimap2.log" \
  | samtools view -b -q 20 -F 4 - \
  | samtools sort -@ 4 -o "$WORK/bam/${target}.mapq20.bam" -
samtools index "$WORK/bam/${target}.mapq20.bam"
samtools flagstat "$WORK/bam/${target}.mapq20.bam" > "$WORK/metrics/${target}.mapq20.flagstat.txt"

total=$(awk 'END {print NR/4}' "$READS")
mapped_unique=$(samtools view "$WORK/bam/${target}.mapq20.bam" | cut -f1 | sort -u | wc -l)
fraction=$(awk -v a="$mapped_unique" -v b="$total" 'BEGIN {if (b) printf "%.12f", a/b; else print 0}')
printf 'target\t%s\ntotal_fastq_reads\t%s\nunique_reads_mapq_ge20\t%s\nmapq_ge20_fraction\t%s\nmapq_ge20_percent\t%.8f\n' \
  "$target" "$total" "$mapped_unique" "$fraction" "$(awk -v f="$fraction" 'BEGIN {print 100*f}')" > "$WORK/metrics/${target}.tsv"
touch "$WORK/metrics/${target}.DONE"
