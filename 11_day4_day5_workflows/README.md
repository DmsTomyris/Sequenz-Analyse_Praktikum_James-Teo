# Kuratierte Workflows aus Tag 4 und Tag 5

Dieser Ordner enthält nur reproduzierbare Arbeitsabläufe, kleine Steuer-/Auswertungsskripte und wichtige Berichte. Roh-FASTQ, BAM/SAM-Massenbestände, Assembly-Ergebnisse, große Referenzbibliotheken und Clusterlogs bleiben außerhalb von Git.

## Enthaltene Workflows

1. `main_reverse_complement/` – PAF-basierte Richtungszuordnung des Main-Workflows.
2. `flye/` – Flye-Restart und Nachbearbeitung fehlgeschlagener Runs.
3. `raven/` – Raven-Fehlerklassifikation und 16-GiB-Retry.
4. `directional_ucsc/` – richtungsabhängige Referenz-/Genome-Hub-Builds und Mapping.
5. `large_dataset_mapping/` – MAPQ-20-Mapping eines großen FASTQ-Datensatzes.

Jeder Unterordner enthält eine eigene `WORKFLOW.md` mit Zweck, Inputformat, Outputs, Abhängigkeiten, Parametern, Startbefehlen und QC.

## Gemeinsame Regeln

- Große Inputs liegen auf dem BMC-HPC unter `/work`, nicht im Git-Repository.
- SLURM-Skripte werden nur auf Compute-Nodes ausgeführt.
- Vor einem produktiven Lauf einen kleinen Testlauf durchführen.
- Job-ID, Toolversionen, Referenz-Checksumme und Outputpfad archivieren.
- Für neue Ergebnisse gilt weiterhin der normale Projektordner und `day5.md` als Hauptprotokoll.
