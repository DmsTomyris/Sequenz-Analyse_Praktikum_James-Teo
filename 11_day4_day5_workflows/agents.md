# AGENTS.md – Mapping-Workflow und BMC-HPC

Diese Datei dokumentiert unsere bisherigen Mapping-Runs und die Nutzung des BMC-HPC-Clusters.

## Agentenkoordination und Tagesprotokoll

Mittlerweile arbeiten mehrere Agenten parallel. Aktuell sind `Cluster3`, `Cluster4` und `master3` als arbeitende Agenten eingetragen.

Vor jeder Aufgabe muss jeder Agent zuerst `day5.md` lesen und prüfen, ob dort seit dem letzten Arbeitsschritt Änderungen, neue Ergebnisse, offene Probleme oder neue Vorgaben dokumentiert wurden. Zusätzlich muss der Agent vor dem Start prüfen, ob relevante Dateien seit dem letzten Stand von einem anderen Agenten verändert wurden, damit keine Ergebnisse überschrieben werden.

Nach jedem signifikanten Arbeitsschritt muss der ausführende Agent den Schritt in `day5.md` dokumentieren. Der Eintrag muss mindestens den bearbeitenden Agenten, Methode, Input, relevante Parameter, Output, signifikante Ergebnisse und technische Korrekturen oder Abweichungen enthalten. Bei späteren Fortsetzungen ist die Datei fortlaufend zu aktualisieren. `day2.md`, `day2.5.md`, `day3.md` und `day4.md` bleiben als historische Dokumentationen bestehen und werden ab jetzt nicht mehr fortgeschrieben.

## Projektdateien

Lokaler Ordner: `C:\Users\teohe\OneDrive\Desktop\.AAAA-Praktikum`

- `PBK89872_pass_barcode77_merged.fastq`: zusammengeführte Original-FASTQ
- `genome.fa`: Hefegenomreferenz
- `pGP564_backbone.fa`: Backbone-Referenz
- `positive_controls/real_yeast_SRR8455574_100k.fastq`: Positivkontrolle

## Hauptergebnisse

| Referenz | Primäre Reads | Anteil an ca. 21.500 Reads |
|---|---:|---:|
| Hefe | 20 | 0,093 % |
| Backbone | 15 | 0,070 % |
| Hefe + Backbone | 35 | ca. 0,163 % |

Cross-Species mit `map-ont`: Mensch 9, Maus 2, Drosophila 0, Zebrafisch 2, *E. coli* 20 Reads. BLAST fand keine überzeugenden zusätzlichen starken Treffer in den Minimap-unmapped Reads.

## Bisherige Runs

### Run 1 – Ausgangsmapping

- **Tool:** Minimap2, Samtools
- **Input:** Original-FASTQ, `genome.fa`, `pGP564_backbone.fa`
- **Parameter:** `minimap2 -ax map-ont`; primäre Alignments
- **Output:** `mapping_results/` mit BAM, Index, Flagstat, Coverage
- **Ergebnis:** Hefe 20, Backbone 15, insgesamt 35 Reads; 99,837 % unmapped.

### Run 2 – Short-Read-Diagnose

- **Tool:** Minimap2, Samtools
- **Input:** Original-FASTQ und dieselben Referenzen
- **Parameter:** `minimap2 -ax sr`
- **Output:** `mapping_results/short_preset/`
- **Ergebnis:** Hefe 44, Backbone 16 Reads; 21.358 Reads unmapped.
- **Änderung:** Preset von `map-ont` auf `sr`.

### Run 3 – erstes SPLAT-/Adaptertrimming

- **Tool:** Cutadapt/SPLAT, Minimap2, Samtools
- **Input:** Original-FASTQ
- **Parameter:** 5′-Adapter `ACACGACGCTCTTCCGATCT`, Mindestlänge 30 bp, anschließend `map-ont`
- **Output:** `mapping_results_splat_trimmed/trimmed.fastq` und Mappingordner
- **Ergebnis:** 19.611 Adaptertreffer, 379 verworfene Reads; Hefe 20, Backbone 15.

### Run 4 – zweites Trimming

- **Tool:** Cutadapt/SPLAT, Minimap2, Samtools
- **Input:** `trimmed.fastq`
- **Parameter:** gleicher Adapter, Mindestlänge 30 bp, `map-ont`
- **Output:** zweites Trim-FASTQ und Mappingordner
- **Ergebnis:** 12.363 Adaptertreffer, 623 verworfene Reads; Mappingtreffer unverändert.

### Run 5 – drittes Trimming

- **Tool:** Cutadapt/SPLAT, Minimap2, Samtools
- **Input:** zweimal getrimmtes FASTQ
- **Parameter:** gleicher Adapter, Mindestlänge 30 bp, `map-ont`
- **Output:** drittes Trim-FASTQ und Mappingordner
- **Ergebnis:** 5.999 Adaptertreffer, 1.207 verworfene Reads; Hefe 20, Backbone 15.

### Run 6 – viertes Trimming

- **Tool:** Cutadapt/SPLAT, Minimap2, Samtools
- **Input:** dreimal getrimmtes FASTQ
- **Parameter:** gleicher Adapter, Mindestlänge 30 bp, `map-ont`
- **Output:** viertes Trim-FASTQ und Mappingordner
- **Ergebnis:** 2.983 Adaptertreffer, 919 verworfene Reads; Mappingtreffer unverändert.

**Bewertung:** Wiederholtes Trimming entfernte weitere Reads, verbesserte aber die absoluten Hefe-/Backbone-Treffer nicht.

### Run 7 – BLAST-Kontrolle

- **Tool:** BLASTN-short, Samtools
- **Input:** Minimap-unmapped Reads aus Run 6
- **Parameter:** `word_size 11`, E-Wert `1e-5`, mindestens 80 % Identität und 50 bp Query-Abdeckung
- **Output:** `fourth_blast_check/`
- **Ergebnis:** keine überzeugenden zusätzlichen Treffer; 0 Reads mit mindestens 30 bp und mindestens 90 % Identität.

### Run 8 – Identitätsschwellen

- **Tool:** Minimap2 und BLAST
- **Input:** Original-FASTQ ohne Adapter-Cut
- **Parameter:** 70 %, 60 %, 50 %; Mindestlängen 50, 75, 100 bp
- **Output:** `raw_identity_test/`
- **Ergebnis:** beide Tools jeweils 35 Treffer pro Schwelle; Hefe 20, Backbone 15.

### Run 9 – Cross-Species mit Short-Read-Preset

- **Tool:** Minimap2, Samtools
- **Input:** Original-FASTQ; Hefe, Mensch, Maus, Drosophila, Zebrafisch, *E. coli*
- **Parameter:** `minimap2 -ax sr`; mindestens 70 % Identität und 50 bp
- **Output:** `cross_species_mapping/`
- **Ergebnis:** Mensch 11, Maus 2, Drosophila 4, Zebrafisch 2, *E. coli* 20 Reads.

### Run 10 – Cross-Species mit `map-ont`

- **Tool:** Minimap2, Samtools
- **Input:** Original-FASTQ ohne Adapter-Cut und dieselben Referenzen
- **Parameter:** `minimap2 -ax map-ont`
- **Output:** `individual_mapont_comparison/`
- **Ergebnis:** Hefe 20, Backbone 15, Mensch 9, Maus 2, Drosophila 0, Zebrafisch 2, *E. coli* 20 Reads.
- **Änderung:** Preset von `sr` zurück auf `map-ont`.

## Positivkontrolle

- Quelle: NCBI SRA `SRR8455574`
- Input: `positive_controls/real_yeast_SRR8455574_100k.fastq`
- Referenz: `genome.fa`
- Tool: Minimap2 2.31 mit `-x sr`; Samtools `flagstat` und `coverage`
- Ergebnis: 97.561 von 100.000 Reads primär gemappt (97,56 %); 56,88 % Referenzabdeckung.

Die Positivkontrolle zeigt, dass FASTQ-Verarbeitung, Hefegenomreferenz, Minimap2 und BAM-Auswertung grundsätzlich funktionieren.

## Nutzung des BMC-HPC-Clusters

### Zugriff

Außerhalb des BMC zuerst LRZ eduVPN aktivieren und **Full-Tunnel** wählen. Danach per SSH auf den Master/Login-Node verbinden. Hostname, Benutzername und Port müssen von der Forschungsgruppe kommen.

```bash
ssh <USER>@<MASTER-HOST>
```

Passwörter und private Schlüssel niemals in Chat, Git oder Jobdateien speichern. Für dauerhaften Zugriff einen lokalen `ed25519`-Schlüssel verwenden.

### Speicher

- Große Daten und SRA-Cache nach `/work/projects/<PROJEKT>/`.
- `~` nicht für große FASTQ oder Referenzen verwenden.
- Es gibt kein verlässliches Cluster-Backup; lokale Kopien behalten.
- Speicherverbrauch prüfen: `du -sh .`

### Software

Private Miniforge-/Mamba-Umgebungen werden gegenüber den alten Modulen empfohlen:

```bash
mkdir -p ~/tmp
cd ~/tmp
wget https://github.com/conda-forge/miniforge/releases/download/24.1.2-0/Miniforge3-24.1.2-0-Linux-x86_64.sh
bash Miniforge3-24.1.2-0-Linux-x86_64.sh -b -p /work/projects/<PROJEKT>/miniforge3
mamba create -y -n yeastmap python=3.11 minimap2 samtools blast cutadapt seqkit
conda activate yeastmap
```

Regeln: nur `conda-forge` und `bioconda`, niemals `defaults`; Base minimal halten; Installationen mit `mamba`; kein `conda update --all`.

Alte Module werden pro Shell/Job geladen:

```bash
module avail
module load ngs/minimap2/2.10
module load ngs/samtools/1.8
```

### Datenübertragung

```powershell
scp -r C:\Users\teohe\OneDrive\Desktop\.AAAA-Praktikum <USER>@<MASTER-HOST>:/work/projects/<PROJEKT>/
```

Für wiederholte Transfers `rsync -avP` verwenden. Nach Transfers Dateigrößen oder Checksummen prüfen.

### SRA-Daten

Internet-Downloads nur auf dem Master/Login-Node. Nicht `fasterq-dump` verwenden; stattdessen:

```bash
prefetch <SRR_ID>
fastq-dump --split-files --gzip <SRR_ID>
```

Der SRA-Cache muss auf `/work` liegen. Nach Abschluss gegebenenfalls `cache-mgr -c` ausführen.

### SLURM

Rechenjobs ausschließlich auf Compute-Nodes ausführen.

Interaktiver Test:

```bash
srun -p slim18 -I -c 4 --mem=16G --time=01:00:00 --pty /bin/bash
```

Beispiel `mapping.slurm`:

```bash
#!/usr/bin/env bash
#SBATCH --job-name=yeast_mapping
#SBATCH --partition=slim18
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=04:00:00
#SBATCH --output=logs/%x-%j.out
#SBATCH --error=logs/%x-%j.err
set -euo pipefail
source /work/projects/<PROJEKT>/miniforge3/etc/profile.d/conda.sh
conda activate yeastmap
cd /work/projects/<PROJEKT>/AAAA-Praktikum
mkdir -p logs results
minimap2 -t "$SLURM_CPUS_PER_TASK" -ax map-ont genome.fa PBK89872_pass_barcode77_merged.fastq \
  | samtools sort -@ "$SLURM_CPUS_PER_TASK" -o results/yeast.bam
samtools index results/yeast.bam
samtools flagstat results/yeast.bam > results/yeast.flagstat.txt
samtools coverage results/yeast.bam > results/yeast.coverage.txt
```

Einreichen und überwachen:

```bash
sbatch mapping.slurm
squeue -u "$USER"
sacct -j <JOB-ID> --format="JobID,State,Elapsed,ReqMem,MaxRSS,AllocCPUS"
```

Erst einen Testlauf machen, dann Ressourcen passend dimensionieren. Nicht unnötig RAM oder CPUs reservieren.

## Reproduzierbarkeitsregeln

1. Für jeden Run ein eigenes Outputverzeichnis verwenden.
2. Jobscript, Toolversionen, Referenznamen und Parameter speichern.
3. `samtools flagstat`, `samtools coverage` und Joblogs archivieren.
4. Minimap-unmapped Reads für BLAST-Kontrollen aufbewahren.
5. Ergebnisse nicht als Kontamination interpretieren, bevor Sample-, Barcode- und Referenzzuordnung geprüft sind.

## Bevorzugtes Tabellenformat

Tabellarische Ergebnisse und größere Tabellen werden standardmäßig als Excel-Datei (`.xlsx`) gespeichert und weitergegeben. TSV-Dateien dürfen nur als technische Zwischen- oder Austauschdateien verwendet werden; die primäre Ergebnisdatei soll Excel sein.

## Quellen

- Lokale Cluster-README: `C:\Users\teohe\Downloads\README.md`
- [Environment Modules](https://envmodules.io/)
- [BMC-CompBio SLURM](https://github.com/bmc-CompBio-user/SLURM)
- [BMC-CompBio Jupyter](https://github.com/bmc-CompBio/HPC_doc/blob/master/jupyter_notebook.md)
- [NCBI SRA Toolkit](https://github.com/ncbi/sra-tools/wiki/Toolkit-Configuration)
- [LRZ eduVPN](https://doku.lrz.de/display/PUBLIC/VPN+-+eduVPN+-+Installation+und+Konfiguration)
- [SSH-Key-Anleitung](https://www.tecmint.com/ssh-passwordless-login-using-ssh-keygen-in-5-easy-steps/)
- [Miniforge](https://github.com/conda-forge/miniforge)

## Aktuelle Protokollregel ab Tag 5

Ab jetzt ist `day5.md` das Hauptprotokoll. Vor jeder Aufgabe muss jeder Agent zuerst `day5.md` lesen und den aktuellen Dateiänderungsstand prüfen. Nach jedem signifikanten Arbeitsschritt ist der Schritt in `day5.md` zu dokumentieren; der Eintrag enthält mindestens Agent, Methode, Input, relevante Parameter, Output, Ergebnisse sowie technische Korrekturen oder Abweichungen.

`day5/` ist ab jetzt der Hauptordner für alle neuen Skripte, Ergebnisse und weiteren digitalen Arbeitsdateien. `day2.md`, `day2.5.md`, `day3.md` und `day4.md` bleiben als historische Dokumentationen bestehen; ihre Dateien und Ordner werden nicht gelöscht.

## Rückkehr zum normalen Projektordner

Die zwischenzeitliche Verlagerung in `Sequenz-Analyse_Praktikum_James-Teo/` wurde auf Nutzeranweisung rückgängig gemacht. Ab sofort ist wieder der normale Projektordner `C:\Users\teohe\OneDrive\Desktop\.AAAA-Praktikum` der maßgebliche Arbeits- und Ablageort.

- **Hauptprotokoll:** `day5.md` im normalen Projektordner.
- **Neue Ergebnisse, Skripte und Arbeitsdateien:** im normalen Projektordner; neue Tagesergebnisse gehören in `day5/`.
- **Vor jeder Aufgabe:** `day5.md` lesen, den Dateiänderungsstand prüfen und im normalen Projektordner arbeiten.
- **Git-Unterordner:** `Sequenz-Analyse_Praktikum_James-Teo/` bleibt als Git-Repository bestehen, ist aber nicht mehr der aktive Arbeitsort.

Die Arbeitsdateien und Ergebnisordner wurden zurück in den normalen Projektordner übertragen. Einige wenige technische Duplikate können wegen temporärer OneDrive-Dateisperren noch im Git-Unterordner verbleiben; maßgeblich für die weitere Arbeit ist ausschließlich der normale Projektordner.
