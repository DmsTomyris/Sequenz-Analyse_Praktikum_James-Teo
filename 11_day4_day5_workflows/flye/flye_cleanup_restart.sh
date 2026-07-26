#!/usr/bin/env bash
set -Eeuo pipefail

# Preserve only valid completed Flye assemblies from v2 and prepare the retry manifest.
# Run without --apply for a dry run; run with --apply only after reviewing the counts.
BASE=/work/project/becstr_013
PROJECT="$BASE/cluster2_flye_work"
OLD="$PROJECT/flye_relaxed_1588_v2"
OUT="$PROJECT/flye_relaxed_1588_v3"
SOURCE_MANIFEST="$PROJECT/flye_manifest.tsv"
COMPLETED="$OUT/preserved_completed_ids.tsv"
RESTART="$OUT/restart_manifest.tsv"
APPLY=${1:-}

test -d "$OLD"
test -s "$SOURCE_MANIFEST"
mkdir -p "$OUT"
: > "$COMPLETED"

for d in "$OLD"/*; do
  [[ -d "$d" ]] || continue
  id=$(basename "$d")
  status=$(awk -F '\t' '$1 == "status" {print $2; exit}' "$d/status.tsv" 2>/dev/null || true)
  if [[ "$status" == COMPLETED && -s "$d/assembly/assembly.fasta" ]]; then
    printf '%s\n' "$id" >> "$COMPLETED"
  elif [[ "$APPLY" == --apply ]]; then
    rm -rf -- "$d"
  fi
done
sort -u -o "$COMPLETED" "$COMPLETED"

awk -F '\t' -v OFS='\t' '
  NR == FNR {done[$1] = 1; next}
  FNR == 1 {print "restart_index", "insert_id", "insert_bp", "expected_bp", "genome_size"; next}
  !done[$2] {n++; print n, $2, $3, $4, $5}
' "$COMPLETED" "$SOURCE_MANIFEST" > "$RESTART"

printf 'preserved_completed\t%s\n' "$(wc -l < "$COMPLETED")"
printf 'restart_candidates\t%s\n' "$(($(wc -l < "$RESTART") - 1))"
if [[ "$APPLY" != --apply ]]; then
  printf 'mode\tDRY_RUN\n'
else
  printf 'mode\tAPPLIED\n'
fi
