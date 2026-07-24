# Requirements und Inputs

## Software

- Minimap2 2.31-r1302 mit `-ax map-ont --sam-hit-only`
- Samtools
- Python 3
- Für Excel-Ausgaben: `openpyxl` (historische lokale Infrastruktur)

## Inputs

- `Day2/Pipeline2/dorado_reads.fastq`
- `Day2/Pipeline2/targeted_reference.fa` und `.fai`
- `Day2/Pipeline2/targeted_reference.map-ont.bam`
- Optional die bestehende Excel-Tabelle `day3/junction_mappings_selected_hits.xlsx`

Der BAM-Workflow verwendet primäre und supplementary Alignments, aber keine sekundären Alignments. Ausgaben: TSV/Excel mit Readintervallen, Referenzintervallen, Gap, Insertlänge und MAPQ.
