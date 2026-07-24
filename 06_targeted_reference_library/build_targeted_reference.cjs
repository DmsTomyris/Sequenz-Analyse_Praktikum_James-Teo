const fs=require('fs'); const XLSX=require('C:/Users/teohe/node_modules/xlsx');
const root='C:/Users/teohe/OneDrive/Desktop/.AAAA-Praktikum'; const out=root+'/Day2/plasmid_assembly_workflow'; fs.mkdirSync(out,{recursive:true});
function readFasta(path){const d={};let name=null,seq=[];for(const line of fs.readFileSync(path,'utf8').split(/\r?\n/)){if(line.startsWith('>')){if(name)d[name]=seq.join('');name=line.slice(1).split(/\s+/)[0];seq=[];}else if(line.trim())seq.push(line.trim());}if(name)d[name]=seq.join('');return d;}
const genome=readFasta(root+'/genome.fa'); const wb=XLSX.readFile(root+'/Yeast_Genomic_Tiling_Collection.xls'); const rows=XLSX.utils.sheet_to_json(wb.Sheets['The dense collection'],{header:1,defval:null}); const h=rows[0]; const ci=Object.fromEntries(h.map((v,i)=>[v,i]));
const inserts=rows.slice(1).filter(r=>String(r[ci.Collection]).toLowerCase()==='minimal').map(r=>({clone:String(r[ci['Clone #']]).trim(),chr:String(r[ci.Chr]).trim(),begin:+r[ci.Begin],end:+r[ci.End]}));
if(inserts.length!==1588) throw new Error('Expected 1588 minimal inserts, got '+inserts.length);
let bed='';let fasta='';let meta='clone\tchr\tbegin\tend\tlength\n';
for(const x of inserts){const key=x.chr; if(!genome[key]) throw new Error('Missing chromosome '+key); const s=genome[key].slice(x.begin-1,x.end-1); if(s.length!==x.end-x.begin) throw new Error('Unexpected length '+x.clone); bed+=`${x.chr}\t${x.begin-1}\t${x.end-1}\t${x.clone}\n`; fasta+=`>${x.clone}\n${s.match(/.{1,80}/g).join('\n')}\n`; meta+=`${x.clone}\t${x.chr}\t${x.begin}\t${x.end}\t${s.length}\n`;}
fs.writeFileSync(out+'/minimal_inserts.bed',bed);fs.writeFileSync(out+'/minimal_inserts.fa',fasta);fs.writeFileSync(out+'/minimal_inserts.tsv',meta);
const backbone=fs.readFileSync(root+'/pGP564_backbone.fa','utf8').replace(/^>[^\n]*/,'>pGP564'); fs.writeFileSync(out+'/targeted_reference.fa',backbone.trimEnd()+'\n'+fasta); console.log('minimal_inserts',inserts.length,'reference',out+'/targeted_reference.fa');
