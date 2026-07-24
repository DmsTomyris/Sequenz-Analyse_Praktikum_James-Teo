# Cross-Species-Mapping

## Zweck

Abschätzen, ob Reads besser zu Fremdorganismen als zu den Zielreferenzen passen. Die Ergebnisse dürfen ohne Proben-, Barcode- und Referenzprüfung nicht als Kontamination interpretiert werden.

## Ablauf

Für jede Spezies separat ausführen:

```bash
minimap2 -t 8 -ax map-ont species.fa reads.fastq \
  | samtools sort -@ 8 -o species.bam
samtools index species.bam
samtools flagstat species.bam > species.flagstat.txt
samtools coverage species.bam > species.coverage.txt
```

Die historische Short-Read-Variante nutzt `-ax sr` und dieselben BAM-Auswertungen.
