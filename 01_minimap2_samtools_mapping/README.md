# Minimap2/Samtools-Mapping

## Zweck

Reads gegen Hefe, Backbone oder eine andere FASTA-Referenz mappen und BAM, Index, Flagstat und Coverage erzeugen. Diese Methode bildet die Grundlage für die Runs 1–2, die Dorado-Auswertung und weitere Kontrollen.

## Standardablauf

```bash
minimap2 -t 8 -ax map-ont genome.fa reads.fastq \
  | samtools sort -@ 8 -o results/yeast.bam
samtools index results/yeast.bam
samtools flagstat results/yeast.bam > results/yeast.flagstat.txt
samtools coverage results/yeast.bam > results/yeast.coverage.txt
```

Für Short-Read-Diagnosen wird `-ax sr` statt `-ax map-ont` verwendet. Hefe und Backbone werden in getrennten Läufen gemappt.

## Wichtige Outputs

Historische Ergebnisse liegen in `Tag1/mapping_results/`, `Tag1/mapping_results/short_preset/` und `Day2/mapping_results_dorado_run1/`.
