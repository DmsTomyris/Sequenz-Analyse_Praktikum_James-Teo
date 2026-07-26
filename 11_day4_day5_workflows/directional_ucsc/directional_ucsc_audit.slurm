#!/usr/bin/env bash
#SBATCH --job-name=dir_ucsc_audit
#SBATCH --partition=slim18
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=08:00:00
#SBATCH --output=/work/project/becstr_013/directional_ucsc_work/logs/audit-%j.out
#SBATCH --error=/work/project/becstr_013/directional_ucsc_work/logs/audit-%j.err

set -euo pipefail

BASE=/work/project/becstr_013
ROOT="$BASE/genome_build_direction_thresholds"
TOOLS="$BASE/directional_ucsc_work/tools"
PYTHON=/opt/software/python-3.6/bin/python3.6

module load ngs/samtools/1.8

"$PYTHON" "$ROOT/scripts/validate_directional_ucsc_hub.py" \
  --root "$ROOT" \
  --samtools "$(command -v samtools)" \
  --bigBedInfo "$TOOLS/bigBedInfo" \
  --bigWigInfo "$TOOLS/bigWigInfo" \
  --hubCheck "$TOOLS/hubCheck"
