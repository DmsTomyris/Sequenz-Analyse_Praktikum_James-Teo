# Requirements und Inputs

## Software

- SRA Toolkit für den Datenbezug, falls die Kontrolle neu erzeugt wird
- Minimap2, Samtools

## Inputs

- Öffentliche Illumina-WGS-Kontrolle `SRR8455574`, z. B. die ersten 100.000 Reads
- Referenz `genome.fa`
- Optional `pGP564_backbone.fa` für eine Backbone-Kontrolle
- FASTQ ohne künstliche Read-Erzeugung; Adaptertrimming für die Hauptkontrolle nicht erforderlich
