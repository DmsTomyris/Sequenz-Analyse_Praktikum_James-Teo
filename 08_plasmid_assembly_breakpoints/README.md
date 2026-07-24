# Plasmid-Assembly- und Breakpoint-Workflow

## Zweck

Insertgrenzen aus der Yeast Genomic Tiling Collection extrahieren, eine gezielte Referenz bauen, Plasmidreads mappen und Backbone-/Insert-Junctions untersuchen.

## Ablauf

```bash
python extract_breakpoints_corrected.py
node build_targeted_reference.cjs
bash run_targeted_mapping.sh
python make_read_7b83c260_alignment.py
```

Die Dateien `plasmid_assembly_workflow_corrected.md`, TSV-Ergebnisse und BAM-QC dokumentieren die historischen Korrekturen und Resultate. Die Junction-Tabelle ist eine Kandidatenliste und kein automatischer biologischer Beweis.
