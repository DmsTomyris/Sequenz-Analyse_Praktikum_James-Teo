#!/usr/bin/env bash
#SBATCH --job-name=yeast_library
#SBATCH --partition=slim18
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=00:10:00
#SBATCH --output=logs/%x-%j.out
#SBATCH --error=logs/%x-%j.err

set -euo pipefail

PROJECT=/work/project/becstr_013
cd "$PROJECT"
mkdir -p logs library
/opt/software/python-3.6/bin/python3.6 --version

/opt/software/python-3.6/bin/python3.6 build_yeast_backbone_insert_library.py \
  --backbone pGP564_backbone.fa \
  --inserts minimal_inserts.fa \
  --output library/yeast_backbone_insert_3176.fasta \
  --report library/yeast_backbone_insert_3176.validation.txt
