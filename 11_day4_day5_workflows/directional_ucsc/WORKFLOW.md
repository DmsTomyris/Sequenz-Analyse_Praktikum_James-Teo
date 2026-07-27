# Richtungsabhängiger UCSC-Workflow

## Zweck

Aus 85-%- und 95-%-Schwellen werden gerichtete Plasmidreferenzen und ein UCSC Genome Hub gebaut. Danach werden Reads auf alle Referenzen gemappt und Junction-Evidence mit MAPQ≥20 ausgewertet.

## Input

- Backbone-/Insert-FASTA und Richtungsaufrufe.
- Hefegenomreferenz für den kombinierten Hub.
- FASTQ-Chunks für das Mapping.
- UCSC-Tools und gültige Chrom-/Gen-Tabellen.

## Ablauf

```bash
python build_directional_ucsc_hub.py
sbatch directional_ucsc_build.slurm
sbatch directional_ucsc_map_array.slurm
sbatch directional_ucsc_finalize_array.slurm
sbatch directional_ucsc_audit.slurm
python validate_directional_ucsc_hub.py
```

Die vier Referenzvarianten sind pGP85, scR64pGP85, pGP95 und scR64pGP95. Das Mapping nutzt `map-ont --secondary=no`; die Junction-Evidence verlangt MAPQ≥20 und mindestens 50 ausgerichtete Basen auf beiden Seiten.

## Output und QC

FASTA/2bit/Chrom- und Gen-Tabellen, BigWig/BigBed, BAM/PAF-Metriken, Manifest und Auditbericht. Build-Checksummen und Sortierung vor dem Genome-Browser-Upload prüfen. Große Tracks gehören nicht in Git.

## Backbone-Referenz ab 2026-07-27

Der Workflow erwartet den experimentell bestätigten 7.158-bp-pGP564-Backbone.
Gegenüber der früher verwendeten 7.371-bp-Sequenz fehlen die nicht bestätigte
60-bp-Tandemduplikation und die zusätzliche 153-bp-Sequenz. Da die
60-bp-Duplikation vor dem Klonierungs-Junction lag, verschiebt sich dessen
homologe 0-basierte Position von 5042 auf 4982. `build_directional_ucsc_hub.py`
verwendet deshalb `BACKBONE_LENGTH = 7158` und `INSERT_INDEX = 4982`.

Die im Repository-Root gespeicherte `pGP95.fasta` enthält 1.747 Records. Alle
Insertsequenzen sind gegenüber der alten Referenz bitidentisch; nur der
Backbone wurde ersetzt. Die Transformation ist mit
`update_pGP95_backbone_to_7158.py` reproduzierbar. Validierungsdetails stehen in
`pGP95_7158_validation.json`.
