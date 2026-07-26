# Raven-Workflow

## Zweck

Raven-Assemblies werden gesammelt, formale Fehler werden nach Ursache klassifiziert und geeignete Kandidaten mit einem 16-GiB-Retry erneut bearbeitet.

## Input

- Pro Insert eine FASTA mit Backbone und Insert.
- Raven-Statusdateien, stderr/stdout und vorhandene FASTA/GFA-Ausgaben.
- Retry-Kandidatenliste aus der Klassifikation.

## Ablauf und Befehle

```bash
bash raven_classify_and_prepare_retry.sh
sbatch raven_retry_16g.slurm
```

Die Klassifikation unterscheidet mindestens Exit 1, Exit 137/SIGKILL und Exit 139/Segmentation Fault. Eine vorhandene nichtleere FASTA/GFA wird als verwertbare Ausgabe separat markiert und nicht doppelt gezählt.

## Output und QC

Retry-FASTAs, Klassifikations-/Status-TSVs und eine eindeutige Assembly-Liste. Für die Ergebnisbewertung müssen `all_alignments` und MAPQ≥20 getrennt ausgewertet werden.
