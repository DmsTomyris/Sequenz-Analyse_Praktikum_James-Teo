#!/usr/bin/env bash
#SBATCH --job-name=dir_ucsc_build
#SBATCH --partition=slim18
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=04:00:00
#SBATCH --output=/work/project/becstr_013/directional_ucsc_work/logs/build-%j.out
#SBATCH --error=/work/project/becstr_013/directional_ucsc_work/logs/build-%j.err

set -euo pipefail

BASE=/work/project/becstr_013
WORK="$BASE/directional_ucsc_work"
TOOLS="$WORK/tools"
SCRIPTS="$WORK/scripts"
OUTPUT="$BASE/genome_build_direction_thresholds"
GFF_URL='https://ftp.ensembl.org/pub/release-116/gff3/saccharomyces_cerevisiae/Saccharomyces_cerevisiae.R64-1-1.63.gff3.gz'
PYTHON=/opt/software/python-3.6/bin/python3.6

test ! -e "$OUTPUT"
test -s "$WORK/inputs/genome.fa"
test -s "$WORK/inputs/minimal_inserts.tsv"
test -s "$WORK/inputs/Saccharomyces_cerevisiae.R64-1-1.63.gff3.gz"

"$PYTHON" "$SCRIPTS/build_directional_ucsc_hub.py" \
  --reference "$BASE/reversed_komplement/library/yeast_backbone_insert_revcomp_3176.fasta" \
  --direction-summary "$BASE/reversed_komplement/main_run/direction_summary.tsv" \
  --minimal-inserts-tsv "$WORK/inputs/minimal_inserts.tsv" \
  --genome "$WORK/inputs/genome.fa" \
  --backbone "$BASE/pGP564_backbone.fa" \
  --gff3 "$WORK/inputs/Saccharomyces_cerevisiae.R64-1-1.63.gff3.gz" \
  --gff-url "$GFF_URL" \
  --faToTwoBit "$TOOLS/faToTwoBit" \
  --twoBitInfo "$TOOLS/twoBitInfo" \
  --bedToBigBed "$TOOLS/bedToBigBed" \
  --output-root "$OUTPUT"

mkdir -p "$OUTPUT/scripts"
cp -p "$SCRIPTS"/* "$OUTPUT/scripts/"
touch "$OUTPUT/BUILD_DONE"
