# Methodenarchiv

Dieses Verzeichnis bündelt die großen datenproduzierenden Methoden aus den Statusdokumenten von Tag 1 bis Tag 3. Jeder Unterordner enthält eine `README.md` mit Ablauf und Befehlen sowie `requirements.md` mit Software, Referenzen, Inputs und erwarteten Formaten.

## Methodenübersicht

1. `01_minimap2_samtools_mapping` – Mapping, BAM, Flagstat und Coverage
2. `02_adapter_trimming` – Cutadapt/SPLAT-Adaptertrimming mit Folgemapping
3. `03_blast_unmapped_control` – BLAST-Kontrolle unmapped Reads
4. `04_cross_species_mapping` – Vergleichsmapping gegen Fremdorganismen
5. `05_positive_controls` – echte Hefegenom- und Backbone-Positivkontrollen
6. `06_targeted_reference_library` – Insert-/Backbone-Referenzbibliotheken
7. `07_junction_mapping_selection` – Junction-Tabelle, Koordinatenkorrektur und Hit-Auswahl
8. `08_plasmid_assembly_breakpoints` – Plasmid-/Breakpoint-Workflow
9. `09_visualization_genome_browser` – Plots und Browser-FASTA/Breakpoint-Pakete
10. `10_hpc_cluster_workflow` – BMC-HPC, SLURM, Library-Mapping und Aggregation

Die großen BAM-/FASTQ-Dateien bleiben an ihren bisherigen Speicherorten. Die Requirements nennen ihre Pfade und Formate, damit die Methoden reproduzierbar gestartet werden können.
