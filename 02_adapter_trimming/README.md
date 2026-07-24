# Adaptertrimming

## Zweck

Entfernen des 5'-Adapters und anschließendes Mapping, um zu prüfen, ob Adapterreste die Zuordnung beeinflussen.

## Befehl

```bash
cutadapt -g ACACGACGCTCTTCCGATCT -m 30 \
  -o trimmed.fastq input.fastq > cutadapt.log
minimap2 -ax map-ont genome.fa trimmed.fastq \
  | samtools sort -o trimmed.bam
samtools index trimmed.bam
samtools flagstat trimmed.bam > trimmed.flagstat.txt
samtools coverage trimmed.bam > trimmed.coverage.txt
```

Für weitere Zyklen wird das vorherige `trimmed.fastq` als Input verwendet. Die historischen vier Zyklen zeigten kaum Änderung der Mappingzahlen.
