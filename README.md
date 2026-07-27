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

## Kuratierte Tag-4/5-Workflows

`11_day4_day5_workflows` enthält die reproduzierbaren Steuer- und Auswertungsteile der späteren Workflows:

- `main_reverse_complement` – gerichtete PAF-/Junction-Auswertung des Main-Workflows
- `flye` – Flye-Retry und Fehlerbereinigung
- `raven` – Raven-Fehlerklassifikation und Retry
- `directional_ucsc` – gerichtete UCSC-Referenzen, Genome Hub und Mapping
- `large_dataset_mapping` – MAPQ-20-Mapping großer FASTQ-Datensätze

Jeder dieser Ordner enthält eine `WORKFLOW.md` und `requirements.md`. Rohdaten, große BAM/SAM/FASTQ-Bestände, Assemblies und Clusterlogs werden nicht versioniert.

## Aktuelle pGP95-Referenz

`pGP95.fasta` enthält 1.747 gerichtete pGP95-Plasmidrecords mit dem experimentell
bestätigten 7.158-bp-pGP564-Backbone. Die Insertsequenzen wurden gegenüber der
vorherigen 7.371-bp-Version unverändert übernommen; der homologe Insert-Junction
liegt jetzt bei 0-basiertem Index 4982. SHA-256:
`033d3dd0ad3b69b7cac96fed7ed3f896e2c5cc48d9f71fa13dd5ed7ecadc995e`.
