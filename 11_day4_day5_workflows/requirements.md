# Gemeinsame Voraussetzungen

- Linux-Cluster mit SLURM und Bash.
- Minimap2 2.10-r761 oder kompatible Version.
- Samtools, Python 3.10+ und Standardbibliothek.
- Für Assembly-Workflows: Flye bzw. Raven 1.8.3.
- Für UCSC-Workflows: UCSC-Build-Tools, `bedGraphToBigWig` und `bedToBigBed`.
- Schreibrechte auf einem `/work`-Projektpfad.
- Inputs als FASTQ, FASTA, PAF/SAM oder TSV gemäß der jeweiligen `WORKFLOW.md`.

Keine Rohdaten oder großen Ergebnisdateien werden aus diesem Repository automatisch heruntergeladen.
