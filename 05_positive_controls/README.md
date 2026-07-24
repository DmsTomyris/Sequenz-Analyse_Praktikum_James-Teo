# Positivkontrollen

## Zweck

Nachweisen, dass FASTQ-Verarbeitung, Referenz, Mapper und BAM-Auswertung grundsätzlich funktionieren.

## Hefekontrolle

```bash
minimap2 -x sr -a genome.fa real_yeast_100k.fastq \
  | samtools sort -o yeast_control.bam
samtools index yeast_control.bam
samtools flagstat yeast_control.bam > flagstat.txt
samtools coverage yeast_control.bam > coverage.tsv
```

Die öffentliche Kontrolle `SRR8455574` ergab 97,56 % primär gemappte Reads. Eine Backbone-Kontrolle kann analog gegen `pGP564_backbone.fa` laufen.
