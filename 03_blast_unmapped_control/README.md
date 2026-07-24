# BLAST-Kontrolle unmapped Reads

## Zweck

Prüfen, ob Minimap2-unmapped Reads doch starke lokale Treffer gegen Hefe oder Backbone enthalten.

## Ablauf

```bash
samtools fastq -f 4 mapped.bam > unmapped.fastq
seqkit fq2fa unmapped.fastq -o unmapped.fasta
makeblastdb -in reference.fa -dbtype nucl -out reference_db
blastn -task blastn-short -query unmapped.fasta -db reference_db \
  -word_size 11 -evalue 1e-5 -outfmt 6 -out hits.tsv
```

Starke Treffer wurden mit mindestens 90 % Identität, 30 bp Alignment und 80 % Query-Abdeckung bewertet. FASTA statt FASTQ verwenden.
