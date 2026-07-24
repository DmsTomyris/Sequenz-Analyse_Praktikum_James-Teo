import csv, os, re, subprocess
from pathlib import Path
os.environ['PATH']='/home/teo-helmer/.local/bin:'+os.environ.get('PATH','')
root=Path('/mnt/c/Users/teohe/OneDrive/Desktop/.AAAA-Praktikum/Day2/plasmid_assembly_workflow')
def qspan(c):
    ops=re.findall(r'(\d+)([MIDNSHP=X])',c); start=sum(int(n) for n,op in re.findall(r'^(\d+)([SH])',c)); aligned=sum(int(n) for n,op in ops if op in 'MI=X'); ref=sum(int(n) for n,op in ops if op in 'MDN=X'); return start,start+aligned,aligned,ref
groups={}
p=subprocess.Popen(['samtools','view','-F','260',str(root/'mapped_plasmids.bam')],stdout=subprocess.PIPE,text=True)
for line in p.stdout:
    f=line.rstrip().split('\t');
    if len(f)<11: continue
    qs,qe,al,rs=qspan(f[5]); rec={'read_id':f[0],'ref':f[2],'pos':int(f[3]),'end':int(f[3])+rs-1,'mapq':int(f[4]),'cigar':f[5],'qstart':qs,'qend':qe,'aligned':al,'flag':int(f[1])}
    groups.setdefault(f[0],[]).append(rec)
p.wait(); rows=[]
for rid,alns in groups.items():
    bs=[a for a in alns if a['ref']=='pGP564' and a['mapq']>=20 and a['aligned']>=50]
    ins=[a for a in alns if a['ref'].startswith('YGPM') and a['mapq']>=20 and a['aligned']>=50]
    for b in bs:
        for i in ins:
            overlap=max(0,min(b['qend'],i['qend'])-max(b['qstart'],i['qstart']))
            if overlap==0: rows.append([rid,i['ref'],i['pos'],i['end'],i['qstart'],i['qend'],i['mapq'],i['cigar'],b['pos'],b['end'],b['qstart'],b['qend'],b['mapq'],b['cigar']])
with open(root/'final_plasmid_insertions.tsv','w',newline='') as f:
    w=csv.writer(f,delimiter='\t'); w.writerow(['read_id','insert_clone','insert_ref_start','insert_ref_end','insert_query_start','insert_query_end','insert_mapq','insert_cigar','backbone_ref_start','backbone_ref_end','backbone_query_start','backbone_query_end','backbone_mapq','backbone_cigar']); w.writerows(rows)
print('reads_with_both_nonoverlap',len(set(r[0] for r in rows))); print('alignment_pairs',len(rows)); print('rows',root/'final_plasmid_insertions.tsv')
