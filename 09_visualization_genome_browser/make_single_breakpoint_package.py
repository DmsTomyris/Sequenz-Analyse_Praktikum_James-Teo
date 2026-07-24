from pathlib import Path
import pandas as pd
import re

ROOT=Path(r"C:\Users\teohe\OneDrive\Desktop\.AAAA-Praktikum")
RUN=ROOT/"Tag1"/"mapping_results_dorado_run1"
OUT=RUN/"single_breakpoint_YGPM-23h16_1093a8b8"
OUT.mkdir(exist_ok=True)

def fasta(path):
    d={}; name=None; seq=[]
    for line in path.read_text(encoding="utf-8",errors="replace").splitlines():
        if line.startswith(">"):
            if name is not None: d[name]="".join(seq).upper()
            name=line[1:].split()[0]; seq=[]
        elif name is not None: seq.append(line.strip())
    if name is not None: d[name]="".join(seq).upper()
    return d
def fastq(path):
    d={}
    with path.open(encoding="utf-8",errors="replace") as f:
        while h:=f.readline():
            d[h.split()[0].lstrip("@")]=f.readline().strip().upper(); f.readline(); f.readline()
    return d
def wrap(s): return "\n".join(s[i:i+80] for i in range(0,len(s),80))
def rec(h,s): return f">{h}\n{wrap(s)}\n"

rid="1093a8b8-1471-436a-998b-4a39cbd56d1f"
split=pd.read_csv(RUN/"yeast_backbone_split_reads.tsv",sep="\t").set_index("read_id").loc[rid]
junction=pd.read_csv(RUN/"yeast_backbone_junction_analysis.tsv",sep="\t").set_index("read_id").loc[rid]
backbone=next(iter(fasta(ROOT/"pGP564_backbone.fa").values()))
yeast=fasta(ROOT/"genome.fa")
read=fastq(ROOT/"dorado_reads.fastq")[rid]

clone="YGPM-23h16"; insert_start=121559; insert_end=134765; chr_name=str(split.yeast_ref); ref=chr_name if chr_name in yeast else "chr"+chr_name
insert=yeast[ref][insert_start-1:insert_end]
bp=int(split.backbone_pos)
left=backbone[:bp-1]; right=backbone[bp-1:]
q_backbone=read[int(split.backbone_qstart)-1:int(split.backbone_qend)]
q_yeast=read[int(split.yeast_qstart)-1:int(split.yeast_qend)]
q_lo=min(int(split.yeast_qstart),int(split.backbone_qstart)); q_hi=max(int(split.yeast_qend),int(split.backbone_qend))
q_bridge=read[q_lo-1:q_hi]
assembled=left+insert+right

fasta_out=OUT/"single_breakpoint_visualization.fasta"
entries=[
 (f"backbone_left|pGP564|1-{bp-1}|cut_before_backbone_mapping",left),
 (f"insert|{clone}|yeast_chr_{chr_name}|{insert_start}-{insert_end}",insert),
 (f"backbone_right|pGP564|{bp}-{len(backbone)}|mapping_starts_here",right),
 (f"assembled_backbone_insert_backbone|cut={bp}|insert={clone}",assembled),
 (f"supporting_read_yeast_segment|read={rid}|q={int(split.yeast_qstart)}-{int(split.yeast_qend)}",q_yeast),
 (f"supporting_read_backbone_segment|read={rid}|q={int(split.backbone_qstart)}-{int(split.backbone_qend)}",q_backbone),
 (f"supporting_read_bridge|read={rid}|q={q_lo}-{q_hi}",q_bridge),
]
fasta_out.write_text("".join(rec(h,s) for h,s in entries),encoding="utf-8")
(OUT/"metadata.tsv").write_text("\n".join([
 "field\tvalue",
 f"read_id\t{rid}", f"clone\t{clone}", f"yeast_reference\t{chr_name}", f"insert_coordinates\t{insert_start}-{insert_end}",
 f"backbone_cut_before_position\t{bp}", f"backbone_length\t{len(backbone)}", f"read_yeast_query\t{int(split.yeast_qstart)}-{int(split.yeast_qend)}",
 f"read_backbone_query\t{int(split.backbone_qstart)}-{int(split.backbone_qend)}", f"yeast_mapq\t{int(split.yeast_mapq)}", f"backbone_mapq\t{int(split.backbone_mapq)}",
 f"assembled_length\t{len(assembled)}", "note\tBreakpoint candidate; not experimentally validated"
 ]),encoding="utf-8")
print(fasta_out); print(OUT/"metadata.tsv"); print(f"read={rid} backbone_cut={bp} insert={clone}:{insert_start}-{insert_end}")
