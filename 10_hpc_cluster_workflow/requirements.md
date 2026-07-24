# Requirements und Inputs

## Infrastruktur

- BMC-Clusterzugang und LRZ-eduVPN Full-Tunnel außerhalb des BMC
- SSH/`plink.exe` oder OpenSSH
- SLURM mit Partition `slim18`
- Speicherort `/work/project/becstr_013/`

## Software

- Minimap2, Samtools, Python 3.6+; für die dokumentierte Clusterumgebung insbesondere `/opt/software/python-3.6/bin/python3.6`
- Optional Mamba/Conda-Umgebung mit `minimap2`, `samtools`, `blast`, `cutadapt`, `seqkit`

## Inputs

- FASTQ-Archiv `20230920_DNA_Korber_Drin3plex.zip` oder ein daraus gestreamtes FASTQ
- `pGP564_backbone.fa`
- `Day2/plasmid_assembly_workflow/minimal_inserts.fa`/`.tsv`
- Für die 3176-Record-Library: Backbone plus 1.588 eindeutige Inserts

Passwörter und private Schlüssel dürfen weder in Skripten noch in Requirements gespeichert werden. Für jeden Job eigene Outputordner, Logs und Checksummen verwenden.
