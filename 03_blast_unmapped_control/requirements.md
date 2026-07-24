# Requirements und Inputs

## Software

- Samtools
- Seqkit
- BLAST+ (`blastn`, `makeblastdb`)

## Inputs

- BAM aus einem Minimap2-Lauf, z. B. `Tag1/mapping_results_splat_trimmed/fourth_mapping/trimmed_fourth.sorted.bam`
- Referenz-FASTA: `genome.fa` oder `pGP564_backbone.fa`
- Schreibbarer BLAST-DB- und Outputordner

## Wichtige Formate

BLAST-Query ist eine FASTA-Datei. Tabellarischer Output sollte Query-ID, Subject-ID, Identität, Alignmentlänge, Querylänge, Koordinaten, E-Wert und Bit-Score enthalten.
