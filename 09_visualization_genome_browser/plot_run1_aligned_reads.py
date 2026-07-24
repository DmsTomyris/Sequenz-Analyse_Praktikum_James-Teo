from pathlib import Path
import subprocess
import plotly.graph_objects as go
from plotly.subplots import make_subplots

ROOT = Path(r"C:\Users\teohe\OneDrive\Desktop\.AAAA-Praktikum")
fastq = ROOT / "dorado_reads.fastq"
bam = "/mnt/c/Users/teohe/OneDrive/Desktop/.AAAA-Praktikum/Tag1/mapping_results_dorado_run1/dorado_vs_yeast.bam"
out = ROOT / "Tag1" / "mapping_results_dorado_run1" / "aligned_reads_length_quality_plot.html"

# Primary mapped alignments only: exclude unmapped (4), secondary (256), supplementary (2048).
sam = subprocess.run(
    ["wsl", "-d", "Ubuntu-22.04", "--", "/home/teo-helmer/.local/bin/samtools",
     "view", "-F", "2308", bam], check=True, capture_output=True, text=True
).stdout
aligned = {}
for line in sam.splitlines():
    fields = line.split("\t")
    if len(fields) >= 6:
        aligned[fields[0]] = {"rname": fields[2], "pos": int(fields[3]), "mapq": int(fields[4]), "cigar": fields[5]}

rows = []
with fastq.open("r", encoding="utf-8", errors="replace") as fh:
    while True:
        h = fh.readline()
        if not h:
            break
        seq = fh.readline().strip()
        fh.readline()
        qual = fh.readline().strip()
        rid = h.split()[0].lstrip("@")
        if rid in aligned:
            qmean = sum(ord(c) - 33 for c in qual) / len(qual)
            row = aligned[rid]
            rows.append((len(seq), qmean, row["mapq"], row["rname"], row["pos"], rid))

x = [r[0] for r in rows]
y = [r[1] for r in rows]
custom = [f"Read: {r[5]}<br>Referenz: {r[3]}:{r[4]:,}<br>MAPQ: {r[2]}" for r in rows]

fig = make_subplots(
    rows=2, cols=2, shared_xaxes=True, shared_yaxes=True,
    column_widths=[0.82, 0.18], row_heights=[0.18, 0.82],
    horizontal_spacing=0.02, vertical_spacing=0.02,
    specs=[[{"type": "histogram"}, {"type": "histogram"}],
           [{"type": "scattergl"}, {"type": "histogram"}]],
)
fig.add_trace(go.Histogram(x=x, marker_color="#66c2a5", opacity=0.7, showlegend=False), row=1, col=1)
fig.add_trace(go.Scattergl(x=x, y=y, mode="markers", marker={"size": 5, "color": [r[2] for r in rows], "colorscale": "Viridis", "showscale": True, "colorbar": {"title": "MAPQ"}}, text=custom, hovertemplate="Länge: %{x} bp<br>mittlerer Q: %{y:.2f}<br>%{text}<extra></extra>", showlegend=False), row=2, col=1)
fig.add_trace(go.Histogram(y=y, marker_color="#66c2a5", opacity=0.7, showlegend=False), row=2, col=2)
fig.update_layout(
    title=f"Read lengths vs Average read quality — Minimap2 Run 1, primär alignte Reads (n={len(rows):,})",
    template="plotly_white", width=1250, height=720,
    margin={"l": 80, "r": 30, "t": 80, "b": 70},
)
fig.update_xaxes(title_text="Read length (bp)", row=2, col=1)
fig.update_yaxes(title_text="Average read quality (Phred)", row=2, col=1)
fig.update_xaxes(showticklabels=False, row=1, col=1)
fig.update_yaxes(showticklabels=False, row=2, col=2)
fig.write_html(out, include_plotlyjs=True, full_html=True)
print(f"Wrote {out}")
print(f"Primary mapped reads plotted: {len(rows)}")
print(f"Length range: {min(x)}-{max(x)} bp")
print(f"Mean Q range: {min(y):.2f}-{max(y):.2f}")
