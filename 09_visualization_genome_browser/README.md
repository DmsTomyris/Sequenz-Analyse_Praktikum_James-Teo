# Visualisierung und Genome Browser

## Zweck

Mapping- und Breakpoint-Ergebnisse für die manuelle Prüfung darstellen. Die Visualisierung unterstützt die Interpretation, ersetzt aber kein BAM-/CRAM-Alignment-Viewer.

## Ablauf

```bash
python plot_run1_aligned_reads.py
python make_breakpoint_browser_fasta.py
python make_single_breakpoint_package.py
```

Der vereinfachte Browser unter `genome-browser/` kann anschließend mit Node.js gestartet werden. Als Overlay-Input eignet sich `Tag1/mapping_results_dorado_run1/yeast_backbone_junction_analysis.tsv`.
