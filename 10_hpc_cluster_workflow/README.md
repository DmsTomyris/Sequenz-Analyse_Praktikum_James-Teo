# BMC-HPC-/SLURM-Workflow

## Zweck

Große Referenzbibliotheken und Mappingläufe reproduzierbar auf dem BMC-HPC ausführen. Login erfolgt am Master, rechenintensive Jobs ausschließlich über SLURM-Compute-Nodes.

## Grundablauf

```bash
sbatch library_build.slurm
sbatch comparison_run_day2.slurm
squeue -u "$USER"
sacct -j JOBID --format="JobID,State,Elapsed,ReqMem,MaxRSS,AllocCPUS"
```

Vorher Referenzen und FASTQ nach `/work/project/becstr_013/` übertragen, Softwaremodule/Miniforge aktivieren und einen kleinen Testlauf ausführen. Große Daten nicht im Home-Verzeichnis speichern.

## Enthaltene Skripte

Librarybau, FASTQ-Validierung/Subsetting, Minimap2-Aggregation, Excel-Erstellung, SLURM-Jobs und die nicht-interaktive SSH-Verbindung sind als Kopien in diesem Ordner enthalten.
