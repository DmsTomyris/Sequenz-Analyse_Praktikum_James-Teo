# Großdatensatz-Mapping

## Zweck

Ein großer entpackter FASTQ wird mit Minimap2 auf pGP85, pGP95 und Hefe+Backbone gemappt. Berichtet werden eindeutige Readnamen nach MAPQ≥20.

## Input

- Entpackter FASTQ, nicht ZIP oder komprimierter SRA-Cache.
- Drei nichtleere Referenz-FASTA.
- Referenzindizes, sofern vom Clusterworkflow benötigt.

## Start

```bash
sbatch large_drin3plex_mapq20_20260726.slurm
```

Das Script nutzt `minimap2 -ax map-ont --secondary=no`, 16 CPUs, 64 GiB und `samtools view -q 20 -F 4`. Den absoluten `/work`-Pfad und die FASTQ-Größe vor dem Start prüfen.

## Output und QC

BAM/BAI, Logs und je Referenz eine MAPQ-20-Metrik gegen die FASTQ-Gesamtzahl. Die Auswertung zählt Readnamen, nicht SAM-Zeilen; Sekundäralignments werden nicht zusätzlich gezählt.
