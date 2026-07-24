from pathlib import Path
import re
import pandas as pd

ROOT = Path(r"C:\Users\teohe\OneDrive\Desktop\.AAAA-Praktikum")
run = ROOT / "Tag1" / "mapping_results_dorado_run1"
split_tsv = run / "yeast_backbone_split_reads.tsv"
junction_tsv = run / "yeast_backbone_junction_analysis.tsv"
fastq = ROOT / "dorado_reads.fastq"
yeast_fa = ROOT / "genome.fa"
backbone_fa = ROOT / "pGP564_backbone.fa"
xls = ROOT / "Yeast_Genomic_Tiling_Collection.xls"
out = run / "breakpoint_visualization_sequences.fasta"
manifest = run / "breakpoint_visualization_sequences.tsv"

def fasta(path):
    d = {}; name = None; seq = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith(">"):
            if name is not None: d[name] = "".join(seq).upper()
            name, seq = line[1:].split()[0], []
        elif name is not None: seq.append(line.strip())
    if name is not None: d[name] = "".join(seq).upper()
    return d

def read_fastq(path):
    d = {}
    with path.open(encoding="utf-8", errors="replace") as f:
        while (h := f.readline()):
            s = f.readline().strip(); f.readline(); f.readline()
            d[h.split()[0].lstrip("@")] = s.upper()
    return d

def wrap(s): return "\n".join(s[i:i+80] for i in range(0, len(s), 80))
def rec(h, s): return f">{h}\n{wrap(s)}\n"

yeast, backbone, reads = fasta(yeast_fa), fasta(backbone_fa), read_fastq(fastq)
split = pd.read_csv(split_tsv, sep="\t").set_index("read_id")
junction = pd.read_csv(junction_tsv, sep="\t")
minimal = pd.read_excel(xls, sheet_name="The dense collection", header=0)
minimal.columns = [str(c).strip() for c in minimal.columns]
minimal = minimal.rename(columns={"Clone #":"clone", "Chr":"chr", "Begin":"begin", "End":"end", "Collection":"collection"})
minimal = minimal[minimal.collection.astype(str).str.lower().eq("minimal")].copy()
minimal["clone"] = minimal["clone"].astype(str).str.strip()

backbone_name, backbone_seq = next(iter(backbone.items()))
records = [rec(f"backbone|{backbone_name}|full_reference|length={len(backbone_seq)}", backbone_seq)]
manifest_rows = [{"read_id":"", "clone":"", "component":"backbone", "source":str(backbone_fa), "start":1, "end":len(backbone_seq)}]
selected = junction[junction["hit_count"].fillna(0).astype(int) > 0]

for _, j in selected.iterrows():
    rid = j.read_id
    if rid not in split.index or rid not in reads: continue
    s, read = split.loc[rid], reads[rid]
    hit = re.search(r"([^:;]+):(\d+)-(\d+)", str(j.get("hits", "")))
    clone = hit.group(1) if hit else "unknown_clone"
    ir = minimal[minimal.clone.eq(clone)].head(1)
    if ir.empty: continue
    ir = ir.iloc[0]; chr_name = str(ir["chr"]).strip(); ref = chr_name if chr_name in yeast else f"chr{chr_name}"
    if ref not in yeast: continue
    insert_start, insert_end = int(ir["begin"]), int(ir["end"])
    q1, q2, y1, y2 = int(s.backbone_qstart), int(s.backbone_qend), int(s.yeast_qstart), int(s.yeast_qend)
    lo, hi = max(1, min(q1,q2,y1,y2)), min(len(read), max(q1,q2,y1,y2))
    entries = [("backbone_read_segment", read[min(q1,q2)-1:max(q1,q2)], min(q1,q2), max(q1,q2)), ("overlap_read_sequence", read[lo-1:hi], lo, hi), ("insert_reference", yeast[ref][insert_start-1:insert_end], insert_start, insert_end)]
    base = f"breakpoint_{rid}|clone={clone}|chr={chr_name}|insert={insert_start}-{insert_end}"
    for component, seq, start, end in entries:
        header = f"{base}|component={component}|length={len(seq)}"
        records.append(rec(header, seq)); manifest_rows.append({"read_id":rid, "clone":clone, "component":component, "source":"genome.fa" if component=="insert_reference" else "dorado_reads.fastq", "start":start, "end":end})

out.write_text("".join(records), encoding="utf-8")
pd.DataFrame(manifest_rows).to_csv(manifest, sep="\t", index=False)
print(f"selected breakpoint candidates: {len(selected)}")
print(f"written candidate reads: {(len(records)-1)//3}")
print(f"FASTA: {out}")
print(f"manifest: {manifest}")
