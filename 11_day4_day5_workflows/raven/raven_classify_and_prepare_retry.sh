#!/usr/bin/env bash
set -Eeuo pipefail

BASE=/work/project/becstr_013
PROJECT="$BASE/cluster2_flye_work"
OLD="$PROJECT/raven_1588"
SOURCE_MANIFEST="$PROJECT/flye_manifest.tsv"
STAMP=20260726
RESULT="$PROJECT/raven_results_faulty_$STAMP"
RETRY="$PROJECT/raven_1588_retry16g_$STAMP"
CLASS="$RESULT/classification.tsv"
RESTART="$RETRY/restart_manifest.tsv"

test -d "$OLD"
test -s "$SOURCE_MANIFEST"
mkdir -p "$RESULT" "$RETRY"
printf 'insert_id\told_status\tclassification\tfasta_bp\tcontigs\tgfa_segments\texit_code\n' > "$CLASS"

fasta_stats() {
  awk 'BEGIN{valid=0;seq=0;total=0;contigs=0} /^>/{if(seq>0)total+=seq;seq=0;contigs++;valid=1;next} /^[A-Za-z]+$/{seq+=length($0);next} {invalid=1} END{if(seq>0)total+=seq;if(valid&&!invalid&&total>0)printf "%d\t%d\n",total,contigs;else exit 1}' "$1"
}
gfa_segments() { awk -F '\t' '$1=="S"{n++} END{if(n>0)print n;else exit 1}' "$1"; }

for d in "$OLD"/*; do
  [[ -d "$d" ]] || continue
  id=$(basename "$d")
  status=$(awk -F '\t' '$1=="status"{print $2;exit}' "$d/status.tsv" 2>/dev/null || true)
  [[ "$status" == COMPLETED ]] && continue
  exit_code=$(awk -F '\t' '$1=="exit_code"{print $2;exit}' "$d/status.tsv" 2>/dev/null || true)
  fasta="$d/assembly.fasta"
  gfa="$d/assembly_graph.gfa"
  if [[ -s "$fasta" && -s "$gfa" ]] && fs=$(fasta_stats "$fasta") && gs=$(gfa_segments "$gfa"); then
    read -r bp contigs <<< "$fs"
    target="$RESULT/FAULTY_RAVEN_${status:-UNKNOWN}_${id}"
    mkdir -p "$target"
    cp -p "$fasta" "$target/assembly_FAULTY.fasta"
    cp -p "$gfa" "$target/assembly_graph_FAULTY.gfa"
    [[ -f "$d/status.tsv" ]] && cp -p "$d/status.tsv" "$target/status_original.tsv"
    [[ -f "$d/raven.stderr.log" ]] && cp -p "$d/raven.stderr.log" "$target/raven.stderr.log"
    sha256sum "$target/assembly_FAULTY.fasta" "$target/assembly_graph_FAULTY.gfa" > "$target/checksums.sha256"
    printf '%s\t%s\tFAULTY_USABLE_FASTA_GFA\t%s\t%s\t%s\t%s\n' "$id" "$status" "$bp" "$contigs" "$gs" "$exit_code" >> "$CLASS"
  else
    printf '%s\t%s\tRETRY_NO_USABLE_FASTA_GFA\t0\t0\t0\t%s\n' "$id" "$status" "$exit_code" >> "$CLASS"
  fi
done

printf 'retry_index\tinsert_id\tinsert_bp\texpected_bp\tgenome_size\n' > "$RESTART"
awk -F '\t' -v OFS='\t' 'NR==FNR{if($3=="RETRY_NO_USABLE_FASTA_GFA")retry[$1]=1;next} FNR>1&&retry[$2]{n++;print n,$2,$3,$4,$5}' "$CLASS" "$SOURCE_MANIFEST" >> "$RESTART"
printf 'usable_faulty\t%s\n' "$(grep -c 'FAULTY_USABLE' "$CLASS" || true)"
printf 'retry_candidates\t%s\n' "$(grep -c 'RETRY_NO_USABLE' "$CLASS" || true)"
