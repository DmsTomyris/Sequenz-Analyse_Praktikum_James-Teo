# Requirements und Inputs

## Software

- Minimap2 (für ONT: `-x map-ont`; Diagnose: `-x sr`)
- Samtools mit `sort`, `index`, `flagstat`, `coverage`
- Bash/WSL oder Linux; mindestens 8 Threads empfohlen

## Inputs

- FASTQ: `Tag1/PBK89872_pass_barcode77_merged.fastq` oder `Day2/Pipeline2/dorado_reads.fastq`
- Referenz-FASTA: `genome.fa` oder `pGP564_backbone.fa`
- Für jede Referenz ein beschreibbarer Outputordner

FASTQ muss valide 4-zeilige Records enthalten; FASTA muss gültige DNA-Sequenzen und eindeutige Namen enthalten.
