# Main Reverse-Complement-Workflow

## Zweck

Reads werden gegen eine gerichtete Bibliothek aus Backbone und Insert gemappt. Für jedes Read wird die beste eindeutige Normal- oder Reverse-Complement-Richtung anhand der PAF-Blöcke bestimmt.

## Input

- FASTQ mit Nanopore-Reads.
- gerichtete Insert-/Backbone-FASTA oder vorbereitete Zielbibliothek.
- Referenzkoordinaten: Insert zwischen Backbone 5042/5043.

## Ablauf

1. `main_full_paf_prepare.slurm` erzeugt Chunks und Metadaten.
2. `main_full_paf_array.slurm` führt `minimap2 -ax map-ont --secondary=no` bzw. PAF-Mapping aus.
3. `main_full_paf_finalize.slurm` sammelt PAFs und vergibt Richtungsaufrufe.
4. Die `main_filtered_*`-Skripte wiederholen den Ablauf mit den qualifizierenden Junction-Filtern.
5. `create_revcomp_final_distribution.py` erstellt die Richtungsverteilung; `filter_junction_sam.py` und `coverage_to_bedgraph.py` liefern Zusatz-QC.

## Output

PAF/BAM-Zwischenergebnisse, eindeutige Richtungs-Tabelle, QC-Zählungen und Verteilungsplot. Große Outputs müssen unter `/work/...` liegen; ins Repository gehört nur die Zusammenfassung.

## Voraussetzungen und Start

```bash
sbatch main_full_paf_prepare.slurm
sbatch main_full_paf_array.slurm
sbatch main_full_paf_finalize.slurm
```

Vorher Pfade und `SLURM_CPUS_PER_TASK`, Referenznamen sowie Input-FASTQ im Script prüfen. Ein Read zählt nur, wenn die Zielkriterien im Script erfüllt sind; sekundäre Alignments werden nicht als eigenständige Reads gezählt.
