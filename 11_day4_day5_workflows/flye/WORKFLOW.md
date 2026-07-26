# Flye-Workflow

## Zweck

Fehlgeschlagene bzw. abgebrochene Flye-Assemblies werden mit kontrollierten Ressourcen erneut gestartet und anschließend gegen den bestehenden Cluster4-Satz verglichen.

## Input

- Pro Insert eine FASTA mit Backbone plus Insert.
- Status-/Fehlertabelle der vorherigen Flye-Läufe.
- optional vorhandene Assembly- und Cluster4-IDs zur Duplikatprüfung.

## Ablauf und Befehle

```bash
bash flye_cleanup_restart.sh
sbatch flye_relaxed_16g_restart.slurm
```

Das Cleanup bestimmt Retry-Kandidaten; das SLURM-Script nutzt 8 CPUs, 16 GiB und begrenzte Parallelität. Vorher die Input- und Outputverzeichnisse im Script anpassen.

## Output und QC

Pro erfolgreichem Insert eine Assembly-FASTA, Status-/Fehlerlogs und eine Retry-Zusammenfassung. Assemblies ohne vollständige FASTA werden als fehlgeschlagen markiert. Keine Roh-Assemblies in Git ablegen.
