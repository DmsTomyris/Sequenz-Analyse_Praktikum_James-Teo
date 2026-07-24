# Targeted-Reference- und Insertbibliothek

## Zweck

Erzeugen und validieren einer Referenz aus Backbone plus Insertsequenzen. Diese Referenz wird für die gezielte Junction-Auswertung verwendet.

## Lokaler Workflow

```bash
node build_targeted_reference.cjs
python extract_breakpoints_corrected.py
```

Die aktuelle gezielte Referenz liegt unter `Day2/Pipeline2/targeted_reference.fa` und enthält den Backbone plus 1.588 Inserts. Vor dem Mapping Namen, Längen und Sequenzen gegen `genome.fa` validieren.

## HPC-Variante

Die 3176-Record-Bibliothek enthält für jedes Insert Normal- und Reverse-Record; siehe `methoden/10_hpc_cluster_workflow`.
