# Requirements und Inputs

## Software

- Node.js für `build_targeted_reference.cjs`
- Python 3
- Samtools oder ein FASTA-Indexierer für `.fai`

## Inputs

- `pGP564_backbone.fa`
- `genome.fa`
- `Day2/plasmid_assembly_workflow/minimal_inserts.tsv` oder `minimal_inserts.bed`
- Optional `Yeast_Genomic_Tiling_Collection.xls` zur unabhängigen Koordinatenprüfung

Inputs müssen eindeutige Insertnamen, 1-basierte Koordinaten und gültige DNA-Sequenzen besitzen.
