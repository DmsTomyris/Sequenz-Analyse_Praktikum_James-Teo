# Junction-Mapping und Hit-Auswahl

## Zweck

Reads mit Backbone- und Insertabschnitt erkennen, CIGAR-/Readkoordinaten korrekt berechnen und Kandidaten nach Schnittstellennähe auswählen.

## Ablauf

```bash
python extract_junction_mappings.py \
  --bam Day2/Pipeline2/targeted_reference.map-ont.bam \
  --fastq Day2/Pipeline2/dorado_reads.fastq \
  --reference Day2/Pipeline2/targeted_reference.fa \
  --output junction_mappings.tsv
python make_junction_excel.py junction_mappings.tsv junction_mappings.xlsx
python select_best_junction_hits.py
python extract_within_20bp.py
```

Die Auswahl nimmt pro Read den Backbone-Hit mit geringstem Abstand zu 5042 und den Insert-Hit mit geringstem Abstand zu einem Insertende. Hard-Clips und Reverse-Strand müssen in Original-Read-Koordinaten berücksichtigt werden.

## Aktuelles Ergebnis

`day3/junction_mappings_selected_hits_20bp.xlsx` enthält das vierte Sheet `within_20bp` mit 72 Reads, deren beide Schnittstellen maximal 20 bp vom Ziel entfernt liegen.
