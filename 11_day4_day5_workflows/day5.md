# Day 5 – Hauptprotokoll

Dieses Dokument ist ab Tag 5 das verbindliche Arbeitsprotokoll für alle Agenten. Vor jedem Arbeitsschritt wird `day5.md` gelesen; nach jedem signifikanten Schritt wird der Eintrag hier fortgeführt.

## 1. Start von Tag 5 und Umstellung der Hauptablage

**Bearbeitender Agent:** `master2`

### Methode

- Der aktuelle Hauptstand wurde aus `day4.md` und `agents.md` geprüft.
- `agents.md` wurde auf den neuen Protokollort `day5.md` umgestellt.
- Der neue Arbeitsordner `day5/` wurde erstellt.

### Output

- Neues Hauptprotokoll: `day5.md`
- Neuer Hauptordner für alle Day-5-Skripte und -Ergebnisse: `day5/`

### Regel ab diesem Schritt

Alle neuen digitalen Arbeitsschritte, Skripte, Zwischenprodukte, Ergebnisdateien, Logs und Tabellen gehören ab jetzt in `day5/` und werden in `day5.md` dokumentiert. Die historischen Ordner und Protokolle `day2`, `day2.5`, `day3` und `day4` bleiben unverändert erhalten.

## 2. Abschlusskontrolle aller Codex-Reverse-Komplement-Runs

**Bearbeitender Agent:** `Codex (/root)`

### Methode

- `agents.md` wurde auf Nutzeranweisung vollständig neu gelesen. Dabei wurde die Umstellung auf `day5.md` als verbindliches Hauptprotokoll erkannt; anschließend wurde `day5.md` vollständig gelesen und der lokale Dateiänderungsstand geprüft.
- Nur-Lese-Clusterkontrolle am 26.07.2026 um 15:12 Uhr CEST mit `squeue`, `sacct`, `DONE`-/Statusdateien, Finaloutputs, Snapshot-Historie und Fehlerlogs.
- Die finale `checksums.sha256` des Main Runs wurde vollständig mit `sha256sum -c` geprüft.
- Es wurden keine Jobs oder Clusterdateien verändert.

### Jobstatus

- Referenzbibliothek `2062282`: `COMPLETED`, Exit `0:0`, Validierung `PASS`.
- Paarweiser Referenzexport `2062283`: `COMPLETED`, Exit `0:0`.
- Ursprüngliches Mappingarray `2063861`: als Gesamtjob `COMPLETED`; drei produktive Originaltasks erfolgreich.
- Ursprünglicher Chunk-2-Task `2063864`: erwarteter historischer OOM-Fehler, `FAILED`, Exit `9:0`.
- Chunk-2-Recovery `2065409`: `COMPLETED`, Exit `0:0`, 64 GiB RAM.
- Ersatz-Finalizer `2065492`: `COMPLETED`, Exit `0:0`.
- Snapshotjobs `2065410`, `2065415`, `2067238`, `2068467`, `2069918` und `2069996`: alle `COMPLETED`, Exit `0:0`; alle sechs Snapshotvalidierungen `PASS`.
- Aktuelle Queue: keine laufenden oder wartenden Reverse-Komplement-Jobs.

### Finale Outputs und Ergebnisse

- Finaler Runmarker: `/work/project/becstr_013/reversed_komplement/main_run/DONE`, Status `COMPLETED`.
- Alle vier Chunkordner besitzen `DONE` und `status COMPLETED`.
- `run_summary.tsv`: `status PASS`.
- 1.495.785 Quellreads.
- 1.288.094 Reads mit mindestens einem PAF-Alignment.
- 1.230.467 Reads eindeutig einem qualifizierenden Backbone-plus-Insert-Target zugeordnet, entsprechend 82,2623 % aller Quellreads.
- Mehrdeutige beste Reads: 0.
- Normal: 578.095 Reads beziehungsweise 46,9818 % der gerichteten Reads.
- Reverse-Komplement: 652.372 Reads beziehungsweise 53,0182 % der gerichteten Reads.
- 207.691 Reads ohne PAF; weitere 57.627 PAF-Reads ohne qualifizierendes Backbone-plus-Insert-Target.
- Finale Dateien: `counts_by_target.tsv`, `direction_summary.tsv`, `run_summary.tsv` und `checksums.sha256`.
- Alle acht Einträge der finalen Gesamtprüfsummenliste einschließlich der vier Chunk-Prüfsummendateien: `OK`.

### Technische Einordnung

- Nicht jeder Einzelversuch war erfolgreich: Der erste Chunk-2-Versuch lief in die 32-GiB-Grenze. Der dafür vorgesehene Recovery-Run wurde erfolgreich abgeschlossen, sodass der produktive Gesamtrun vollständig und valide beendet wurde.
- Zwei Snapshotlogs enthielten eine nicht fatale SLURM-cgroup-Warnung. Die betroffenen Jobs endeten dennoch mit Exit `0:0`, schrieben vollständige Snapshots und bestanden deren `PASS`-Validierung.

## 3. Präzisierung des Kriteriums „eindeutig zugeordnet“

**Bearbeitender Agent:** `Codex (/root)`

### Methode und Input

- Read-only-Prüfung des tatsächlich ausgeführten Aggregators `day4/aggregate_revcomp_junction_paf.py`, des SLURM-Skripts `day4/main_revcomp_array.slurm` und des archivierten Workflow-Audit-Pakets.

### Relevante Parameter und Ergebnis

- Mapping: Minimap2 `-x map-ont --secondary=no`.
- Ein Read/Target-Paar qualifizierte sich, sobald seine kombinierten PAF-Blöcke sowohl das Insertintervall als auch mindestens einen Backbonebereich überlappten.
- Es wurde keine zusätzliche Mindestidentität, Mindest-MAPQ, Mindestzahl überlappender Basen oder Mindestdifferenz zum zweitbesten Target verlangt.
- Qualifizierende Targets wurden lexikographisch nach `(Summe Matches, Summe Alignmentblocklängen, maximale MAPQ)` geordnet.
- „Eindeutig zugeordnet“ bedeutet: Genau ein Target besitzt das maximale Scoretupel. Bei einem exakten Gleichstand mehrerer Targets wurde der Read als mehrdeutig ausgeschlossen.
- Technische Konsequenz: Schon eine Verbesserung um eine Matchbase, bei gleicher Matchzahl eine zusätzliche Alignmentblockbase oder erst danach eine höhere MAPQ genügte für einen eindeutigen Bestscore.

### Output

- Keine neuen Ergebnisdateien; nur diese nachvollziehbare Kriterienpräzisierung in `day5.md`.
## 2. Live-Status der Flye- und Raven-Workflows

**Bearbeitender Agent:** `Cluster3`

- **Vorgabeprüfung:** `AGENTS.md` und `day5.md` wurden vor der Abfrage gelesen; `day5/` bleibt die aktuelle Ablage.
- **Methode:** Read-only-Abfragen auf dem Cluster mit `squeue`, `sacct`, `find`, `awk`, Logauswertung und Größenprüfung; keine laufenden Jobs oder Outputs wurden verändert.
- **Flye-Job:** `2063866`, Array `1-1588%100`; 100 Tasks `RUNNING`, 373 `PENDING` wegen `JobArrayTaskLimit`.
- **Flye-Outputs:** 799 `COMPLETED`, 206 `FAILED`, 210 `RUNNING` in den per-Insert-Statusdateien; 799 nichtleere `assembly/assembly.fasta`.
- **Flye-Fehlerbild:** mindestens 153 der 206 Fehler enthalten explizit `Looks like the system ran out of memory`; die übrigen Fehler werden weiter als Pipeline-Abbruch ausgewiesen. Ursache ist damit primär die Kombination aus 9G RAM, `--meta`, `--min-overlap 1000`, vollständigem Backbone und teils sehr großen/hohen-Coverage-Inputs.
- **Raven-Job:** `2065565` ist nicht mehr in `squeue`; `sacct` weist die letzten Arraytasks als beendet/fehlgeschlagen aus.
- **Raven-Outputs:** 1.084 `COMPLETED`, 500 `FAILED`, 4 alte `RUNNING`-Statusdateien; 1.483 nichtleere `assembly.fasta` liegen vor. Die vier `RUNNING`-Dateien stammen vom 25.07. und sind keine Belege für aktuell laufende Tasks.
- **Raven-Fehlerbild:** 475 `exit_code 1`, 24 `exit_code 137` (SIGKILL, typischerweise Speicher-/Schedulerabbruch), 1 `exit_code 139` (Segmentation Fault). Bei vielen `exit_code 1`-Fällen existieren bereits FASTA und GFA; deshalb ist der Statusmarker strenger als der vorhandene Output und muss vor einer Endauswertung separat validiert werden.
- **Toolversionen:** Flye `2.9.5-b1801`, Raven `1.8.3`.
- **Speicherverbrauch:** Flye-Outputverzeichnis ca. 16G, Raven-Outputverzeichnis ca. 528M.

## 4. Finaler Reverse-Komplement-Datensatz und aktuelle Abbildungen

**Bearbeitender Agent:** `Codex (/root)`

### Methode und Input

- `agents.md` und der aktuelle Stand von `day5.md` wurden vor Beginn erneut geprüft.
- Die finalen Dateien `counts_by_target.tsv`, `direction_summary.tsv`, `run_summary.tsv`, `run_metadata.tsv`, `checksums.sha256` und `DONE` wurden aus `/work/project/becstr_013/reversed_komplement/main_run/` nach `day5/revcomp_main_final/` übertragen.
- Für jede übertragene Datei wurde die lokale SHA-256-Prüfsumme direkt mit einer neu auf dem Cluster berechneten Prüfsumme verglichen; alle sechs Vergleiche waren identisch.
- Aus der finalen `direction_summary.tsv` wurde mit `day5/create_revcomp_final_distribution.py` eine aktualisierte Offline-Plotly-Abbildung im Stil des vorherigen Zwischenstands erzeugt. Die Darstellung wurde zusätzlich über Chrome/Playwright als PNG gerendert und visuell kontrolliert.

### Parameter und Ergebnisse

- Basis der zuvor genannten 82,2623 %: `1.230.467 / 1.495.785`, also eindeutig bestbewertete, Backbone-plus-Insert-qualifizierende Reads geteilt durch alle Quellreads.
- Die Zahl ist kein Anteil der Inserts oder PAF-Zeilen.
- 207.691 Quellreads besaßen kein PAF-Alignment; weitere 57.627 hatten zwar PAF-Alignment(s), aber kein qualifizierendes Backbone-plus-Insert-Target.
- Unter den 1.288.094 Reads mit PAF entsprechen die 1.230.467 Zuordnungen 95,5262 %.
- `ambiguous_best_reads` war 0; deshalb sind `reads_with_qualifying_target` und `assigned_unique_best_reads` in diesem Run beide 1.230.467.
- Diagrammprüfung: 1.588 eindeutige Insert-IDs, Summenabgleich `578.095 normal + 652.372 revcomp = 1.230.467`, finaler Runstatus `PASS`, keine Browser-Konsolenfehler.

### Output

- `day5/revcomp_main_final/normal_reverse_distribution_plotly_offline_final.html`
- `day5/revcomp_main_final/normal_reverse_distribution_final.png`
- Finale Quelldaten und Metadaten im selben Ordner.

### Technische Korrektur oder Abweichung

- Die zuvor lokal vorhandenen Abbildungen waren nur ein Zwischenstand mit 1.495.782 bestätigten Reads und wurden nicht überschrieben.
- Eine finale Excel-Arbeitsmappe konnte in dieser Sitzung noch nicht regelkonform erzeugt werden: Das vom Spreadsheets-Skill zwingend vorgeschriebene Paket `@oai/artifact-tool` und der vorgesehene Workspace-Dependency-Loader waren in der Laufzeit nicht verfügbar. Es wurde bewusst keine nicht freigegebene Ersatzbibliothek eingesetzt.

## 5. Entfernung der 0/0-Inserts aus der finalen Richtungsverteilung

**Bearbeitender Agent:** `Codex (/root)`

### Methode und Input

- Vor der Änderung wurden `agents.md`, `day5.md`, der aktuelle Skriptstand und die Änderungszeiten der betroffenen Ergebnisdateien geprüft.
- Input blieb die unveränderte finale `day5/revcomp_main_final/direction_summary.tsv`.
- `day5/create_revcomp_final_distribution.py` wurde so erweitert, dass Inserts mit `normal_reads == 0` und `revcomp_reads == 0` vor Sortierung und Ranking aus den Plotdaten entfernt werden.
- Zusätzlich prüft das Skript, dass die 0/0-Klassifikation exakt `directional_reads == 0` entspricht und dass die Summe der gerichteten Reads nach dem Filtern weiterhin 1.230.467 beträgt.

### Parameter und Ergebnis

- Ursprüngliche Insertzahl: 1.588.
- Entfernte 0/0-Inserts: 12.
- Dargestellte Inserts mit mindestens einem gerichteten Read: 1.576.
- Die zuvor sichtbaren senkrechten Einbrüche der blauen Kurve im rechten Diagrammteil sind entfernt.
- Titel und x-Achsenbeschriftung weisen nun ausdrücklich auf die ausgeblendeten 0/0-Inserts beziehungsweise die reduzierte Rangbasis hin.

### Output und Validierung

- Die ausdrücklich zur Korrektur freigegebenen Dateien wurden am gleichen Zielpfad aktualisiert:
  - `day5/revcomp_main_final/normal_reverse_distribution_plotly_offline_final.html`
  - `day5/revcomp_main_final/normal_reverse_distribution_final.png`
- Visuelle Kontrolle mit Chrome/Playwright: Kurvenverlauf ohne 0/0-Einbrüche, Titel und Achsen vollständig lesbar, keine Browser-Konsolenfehler.
- Neue SHA-256:
  - HTML: `17902730a7459b908b110d00ae4a23485bfec92425a1d157fafeedae649038bf`
  - PNG: `9d2b3ad58465b116e817f1dcf4010d1787721b9048184b3610a9a226b1a88d3a`
## 4. Cluster4-Workflow auf neue Flye-Assemblies erweitert

**Bearbeitender Agent:** `Cluster4`

- **Input:** `/work/project/becstr_013/cluster2_flye_work/flye_relaxed_1588_v2/`; zum Kontrollzeitpunkt 801 nichtleere `assembly/assembly.fasta` für Flye-IDs.
- **Abgleich:** Der bestehende Cluster4-Datensatz enthält 202 IDs. Davon überlappen 112 mit den Flye-Assemblies; daher wurden 689 tatsächlich neue IDs als Erweiterung ausgewählt, damit der Output keine Duplikate enthält.
- **Referenzen:** Für jede neue ID werden die bereits validierten `normal_backbone_insert.fasta` und `reverse_complement_backbone_insert.fasta` aus `cluster4_version2/input/references/<ID>/` verwendet.
- **Methode:** Pro ID zwei Minimap2-Läufe mit `-ax map-ont --secondary=yes -N 10000 -p 0.0`, Assembly als Ziel und jeweils eine der beiden vollständigen Backbone-Insert-Referenzen als Query. Alle Alignments werden behalten; der Parser verwendet aligned Query-Basen >=50 und Identität >=70% für die Statistik.
- **Neue Ablage:** `/work/project/becstr_013/cluster4_version2_flye_new/`; Manifest `manifest_new.tsv`, 689er Array, separate Ergebnisse und kombinierter Finalizer für 891 eindeutige IDs.
- **SLURM:** Mapping-Array `2071026` (`1-689%100`, 4 CPUs, 4G, 1h pro Task); abhängiger Finalizer `2071127` für die kombinierte Excel nach erfolgreichem Arrayabschluss.
- **Output geplant:** `cluster4_version2_first_202_plus_flye_new_summary.xlsx` mit den bisherigen 202 plus 689 neuen Datensätzen und den Sheets `all_alignments` sowie `MAPQ_ge_20`.
- **Technische Abweichung:** Die Nutzerangabe „800“ wurde gegen den Clusterbestand geprüft; ein zusätzlicher 801. fertiger Flye-Output war vorhanden. Wegen 112 Überschneidungen wird korrekt nur die neue, eindeutige Menge von 689 gemappt.
- **Abschluss:** Alle 689 Mapping-Tasks erzeugten vollständige Resultate mit Exit-Code `0:0`. Der direkte Finalizer `2071718` lief erfolgreich mit Exit-Code `0:0` und erzeugte 891 eindeutige Insert-Zeilen pro Excel-Sheet. Der abhängige Finalizer `2071127` blieb als veralteter Pending-Eintrag bestehen und wurde nicht für die Abschlussbewertung verwendet.
- **Lokaler Download:** `day4/workflows/cluster4_version2/flye_new_689/` enthält Manifest, Skripte, 5.515 technische Resultatdateien und die kombinierte Excel. Verifiziert wurden 891 eindeutige IDs in `all_alignments` und `MAPQ_ge_20`; Excel-SHA256 lokal: `2dc787eb310aaa74af3bbc021561bdd7db85d66854b7ba6e116b0200c9f5c3`.

## 6. Vergleich des erweiterten Cluster4-Datensatzes mit dem Main-Run

**Bearbeitender Agent:** `Cluster4`

- **Input:** Kombinierte Cluster4-Excel mit 891 IDs und `day4/outputs/revcomp_main_interim_20260725T095650Z/counts_by_target.tsv`.
- **Vergleichsregel:** Im Main-Run wurde pro ID die Richtung mit der höheren Read-Anzahl (`normal` vs. `revcomp`) als Referenzaufruf verwendet; `revcomp` entspricht `reverse`. TSV-Ties wurden aus der Übereinstimmungsquote ausgeschlossen.
- **`all_alignments`:** 407 eindeutige Cluster4-Richtungsaufrufe; 397 mit entscheidbarem Main-Run-Vergleich. Davon 232 Übereinstimmungen und 165 Abweichungen: **58,44 % Übereinstimmung**.
- **`MAPQ_ge_20`:** 475 eindeutige Cluster4-Richtungsaufrufe; 468 entscheidbare Vergleiche. Davon 312 Übereinstimmungen und 156 Abweichungen: **66,67 % Übereinstimmung**.
- **Aufteilung:** Für die alten 202 IDs beträgt die Übereinstimmung 69,57 % (`all_alignments`) bzw. 88,57 % (`MAPQ_ge_20`). Für die 689 neuen Flye-IDs beträgt sie 56,98 % bzw. 62,81 %.
- **Nicht entscheidbare Fälle:** Im kombinierten Datensatz liefern 484 (`all_alignments`) bzw. 416 (`MAPQ_ge_20`) IDs keinen eindeutigen Cluster4-Aufruf (`ambiguous`/`no_call`). Diese wurden nicht als falsche Richtungen gezählt.
- **Interpretation:** Die Prozente messen Übereinstimmung mit dem Readcount-basierten Main-Run, nicht die biologische Wahrheit. Der MAPQ-Filter verbessert die Übereinstimmung, besonders bei den ursprünglichen 202 IDs; bei den neuen Flye-Assemblies bleibt die Übereinstimmung deutlich niedriger.

## 3. Flye-Neustart mit 16G RAM

**Bearbeitender Agent:** `Cluster3`

- **Vorgabeprüfung:** `AGENTS.md` und `day5.md` wurden vor der Änderung gelesen; neue Skripte liegen unter `day5/`.
- **Ausgangslage:** Der alte relaxed-Flye-Job `2063866` hatte während der Prüfung 800 fertige Runs; während des kontrollierten Stopps wurde ein weiterer Task fertig, sodass 801 valide fertige Runs erhalten blieben.
- **Stop:** Job `2063866` wurde mit `scancel` beendet. Dadurch wurden laufende und wartende alte Flye-Tasks gestoppt; Raven und andere Workflows wurden nicht angefasst.
- **Cleanup-Methode:** `flye_cleanup_restart.sh` prüfte pro Insert `status=COMPLETED` und eine nichtleere `assembly/assembly.fasta`. Nur die übrigen 787 per-Insert-Verzeichnisse unter `flye_relaxed_1588_v2/` wurden gelöscht. Die 801 fertigen Verzeichnisse blieben erhalten; Logs und Workflowdefinitionen wurden nicht pauschal gelöscht.
- **Validierung:** 801 alte Insert-Verzeichnisse blieben bestehen; der neue Restart-Manifest enthält 788 Zeilen inklusive Header, also 787 Neustartkandidaten. Der verfügbare `/work`-Speicher beträgt ca. 28T.
- **Neuer Workflow:** `day5/flye_relaxed_16g_restart.slurm`, Clusterpfad `/work/project/becstr_013/cluster2_flye_work/flye_relaxed_16g_restart.slurm`.
- **Parameter:** Flye `--nano-raw`, `--min-overlap 1000`, `--meta`, `--keep-haplotypes`, kein `--asm-coverage`, kein `--no-alt-contigs`; 8 CPUs und 16G RAM pro Task. Die Kerne bleiben bei 8, damit 100 parallele Slots realistisch nutzbar sind; die höhere Speicherausstattung adressiert die dokumentierte OOM-Ursache.
- **Neuer Output:** `/work/project/becstr_013/cluster2_flye_work/flye_relaxed_1588_v3/`; Restart-Manifest `restart_manifest.tsv`.
- **Neuer Job:** `2070896`, Array `1-787%100`, Partitionen `slim16,slim18`, 12 Stunden je Task.
- **Live-Status nach Einreichung:** 100 Tasks `RUNNING`, Array-Rest `PENDING`; Ressourcenprüfung bestätigt 8 CPUs und 16G RAM je Task. `flye_relaxed_1588_v3` hatte beim Start noch ca. 792K Outputdaten.
- **Technische Abweichung:** Der Nutzer nannte zunächst 799 fertige Runs; aufgrund des live fertig gewordenen Tasks wurden korrekt 801 fertige Runs bewahrt und nur die verbleibenden 787 Runs neu gestartet.
## 4. Ursachen der Raven-Fehlermeldungen

**Bearbeitender Agent:** `Cluster3`

- **Methode:** Read-only-Prüfung des tatsächlich verwendeten `raven_1588.slurm`, der Exit-Codes, repräsentativer `raven.stderr.log`-Dateien sowie des Vorhandenseins von FASTA-, GFA-, Versions- und Checksum-Dateien.
- **Raven-Version:** `1.8.3`; `raven --version` selbst endet korrekt mit Exit-Code 0.
- **Exit 137:** 24 Tasks wurden mit SIGKILL beendet. Das spricht für Speicher-/cgroup- oder Scheduler-Abbruch bei 9G RAM; diese Tasks besitzen überwiegend keine vollständige Assembly.
- **Exit 139:** Ein Task endete mit Segmentation Fault. Das ist ein Raven-/Bibliotheksabbruch, nicht ein normaler biologischer „No assembly“-Befund.
- **Exit 1 mit FASTA und GFA:** 399 Tasks besitzen bereits beide Outputdateien, aber keine `raven.version.txt`/`checksums.sha256`. Die Logs enden nach Graph-/Polishing-Schritten ohne explizite Fehlermeldung. Hier beendet Raven den Prozess selbst mit Exit 1, obwohl verwertbar aussehende Outputs geschrieben wurden; der Bash-Exit-Handler überschreibt deshalb den Status mit `FAILED`.
- **Exit 1 mit GFA ohne FASTA:** 72 Tasks konstruierten einen Graphen, erzeugten aber keinen nichtleeren Konsensus-Output. Das anschließende `test -s assembly.fasta` schlägt fehl und setzt `FAILED`. Das entspricht meist „kein ausgabefähiger Contig“ bzw. zu wenig/zu fragmentierter Evidenz.
- **Exit 1 ohne FASTA/GFA:** 29 Tasks brachen sehr früh ab.
- **Inputfehler:** Mindestens ein früher Abbruch (`YGPM-15l07`) meldet explizit `bioparser::FastaParser: invalid file format`; die betreffende Insert-FASTA muss separat auf Header, Sequenzzeilen und Dateigröße geprüft werden.
- **Wichtige Schlussfolgerung:** Die 500 `FAILED`-Marker sind keine homogene Gruppe. 399 davon sind wahrscheinlich technisch abgeschlossene oder weit fortgeschrittene Raven-Läufe mit nachgelagertem Exit-1-Problem; 101 haben keinen vollständigen FASTA-Output und müssen als echte Fehl-/Leerlaufkandidaten behandelt werden. Die Statuslogik des Scripts ist daher strenger als eine reine Outputprüfung.
- **Nicht ursächlich:** Die Meldungen `updated overlaps`, `removed false overlaps` und die Racon-Polishing-Fortschrittsanzeigen sind normale Raven-Statusmeldungen, keine Fehler.
## 5. Raven-Cleanup, Faulty-Ergebnisablage und 16G-Retry

**Bearbeitender Agent:** `Cluster3`

- **Vorgabeprüfung:** `AGENTS.md` und `day5.md` wurden vor dem Arbeitsschritt gelesen; neue Skripte liegen unter `day5/`.
- **Methode:** Der alte Raven-Output `raven_1588/` wurde pro Insert anhand des tatsächlichen FASTA- und GFA-Inhalts geprüft. Eine FASTA wurde als verwertbar akzeptiert, wenn sie mindestens einen gültigen Header, valide Sequenzzeilen und >0 Basen enthielt; ein GFA musste mindestens ein Segment enthalten.
- **Verwendbare Faulty-Outputs:** 399 formal fehlgeschlagene, aber inhaltlich vorhandene FASTA+GFA-Paare wurden nach `/work/project/becstr_013/cluster2_flye_work/raven_results_faulty_20260726/FAULTY_RAVEN_FAILED_<YGPM-ID>/` kopiert. Die Dateien heißen `assembly_FAULTY.fasta` und `assembly_graph_FAULTY.gfa`; Originalstatus, stderr und Checksums liegen je Insert bei.
- **Validierung:** 399 Ergebnisordner wurden erzeugt; ein repräsentativer Checksum-Test für FASTA und GFA war `OK`. Die vollständige Klassifikation steht in `raven_results_faulty_20260726/classification.tsv`.
- **Neustartmenge:** 105 Inserts hatten keinen verwertbaren FASTA+GFA-Satz: 72 hatten nur GFA ohne FASTA, 29 weder FASTA noch GFA und 4 waren alte RUNNING-Marker ohne verwertbares Ergebnis. Diese 105 IDs stehen in `raven_1588_retry16g_20260726/restart_manifest.tsv`.
- **Neuer Workflow:** `day5/raven_retry_16g.slurm`, Clusterpfad `/work/project/becstr_013/cluster2_flye_work/raven_retry_16g.slurm`.
- **Parameter:** Raven 1.8.3, vollständiges Backbone plus genau ein Insert, `--identity 0`, `--kMaxNumOverlaps 64`, `--min-unitig-size 1000`, `--polishing-rounds 1`, GFA-Ausgabe; 8 CPUs und 16G RAM je Task, 12 Stunden Laufzeit.
- **Job:** `2071721`, Array `1-105%100`, Partitionen `slim16,slim18`. Beim Kontrollzeitpunkt waren 93 Tasks `RUNNING` und 12 `PENDING`.
- **Output des Retries:** `/work/project/becstr_013/cluster2_flye_work/raven_1588_retry16g_20260726/<YGPM-ID>/` mit `assembly.fasta`, GFA, Logs, Status, Version und Checksums.
- **Technische Abweichung:** Die 399 verwertbaren Faulty-Outputs wurden nicht gelöscht, sondern zur sicheren Nachprüfung kopiert und eindeutig markiert. Die ursprünglichen Raven-Verzeichnisse und Logs bleiben als technische Provenienz erhalten.

## 7. Richtungsabhängige Referenzgenome und UCSC-Assembly-Hub

**Bearbeitender Agent:** `Codex (/root)`

### Methode und Inputs

- Vor Beginn wurden `agents.md`, `day5.md`, lokale Änderungszeiten sowie der Clusterbestand geprüft. Der neue Zielpfad `/work/project/becstr_013/genome_build_direction_thresholds/` war nicht vorhanden.
- Verwendet werden ausschließlich die validierte Referenzbibliothek `reversed_komplement/library/yeast_backbone_insert_revcomp_3176.fasta`, die finale `direction_summary.tsv`, `minimal_inserts.tsv`, `genome.fa` und `pGP564_backbone.fa`; Flye-, Raven- und `cluster4_version2/input/references/`-Ergebnisse gehen nicht in die Sequenzen ein.
- Die Input-SHA-256 der Referenz (`9475580d...`), Richtungszusammenfassung (`32441bda...`) und des Backbones (`b3171c35...`) wurden erneut bestätigt.
- Für IDs mit mindestens 10 gerichteten Reads wird die exakte Ganzzahlregel `100 × max(normal, revcomp) >= Schwelle × directional_reads` verwendet. Alle 53 IDs mit weniger als 10 Reads, einschließlich 12 IDs mit `0/0`, werden in beiden Orientierungen aufgenommen.

### Referenz- und Hub-Build

- Build-Skript: `day5/build_directional_ucsc_hub.py`; produktiver SLURM-Job `2071846`, Status `COMPLETED`, Exit-Code `0:0`, Laufzeit 20 Sekunden.
- 85-%-Satz: 1.496 Einzel-IDs und 92 Doppel-IDs; 1.680 FASTA-Chromosomen.
- 95-%-Satz: 1.429 Einzel-IDs und 159 Doppel-IDs; 1.747 FASTA-Chromosomen.
- Vier UCSC-Assemblies:
  - `pGP85`: 1.680 Plasmidchromosomen.
  - `scR64pGP85`: 1.680 Plasmide plus 17 R64-1-1-Chromosomen, insgesamt 1.697.
  - `pGP95`: 1.747 Plasmidchromosomen.
  - `scR64pGP95`: 1.747 Plasmide plus 17 R64-1-1-Chromosomen, insgesamt 1.764.
- Je Assembly wurden Multi-FASTA, 2bit, `chrom.sizes`, `chromAlias.txt`, `trackDb.txt`, `groups.txt`, Beschreibungsseite und BigBed-Tracks für Plasmidstruktur, Auswahl, Insertquelle und projizierte Gene erzeugt. Die Kompositassemblies enthalten zusätzlich 6.600 R64-1-1-Gene.
- Genquelle: Ensembl/Ensembl Genomes Release 63 für R64-1-1 unter dem Release-116-FTP-Baum; GFF3-SHA-256 `717194a9...`.
- Buildvalidierung: `status PASS`; 3.503 von 3.503 Build-Prüfsummen lokal und auf dem Cluster gültig; `hubCheck -noTracks` ohne Fehler.

### Technische Korrekturen

- Der erste Build `2071844` brach vor Finalisierung ab, weil UCSC BED-Dateien in C-/ASCII-Chromosomensortierung verlangt. FASTA-, BED- und BAM-Headerreihenfolge wurden deterministisch lexikographisch vereinheitlicht.
- Build `2071845` war inhaltlich erfolgreich, schrieb im Assembly-Manifest aber temporäre Staging-Pfade. Der komplette Stand wurde ohne Löschung nach `directional_ucsc_work/failed_builds/genome_build_direction_thresholds.job2071845/` verschoben und mit relativen stabilen Pfaden neu gebaut.
- Aktuelle UCSC-Binaries benötigen glibc ≥2.28, der Cluster besitzt glibc 2.17. Deshalb werden die offiziellen UCSC-v385-Binaries projektlokal verwendet; die inkompatiblen Downloads bleiben unter `directional_ucsc_work/tools_glibc_too_new/` archiviert.
- Mappingversuch `2071847` endete für alle Tasks vor Start der Job-Shell durch eine SLURM-cgroup-Störung. Versuch `2072964` endete unmittelbar durch die fehlerhafte Prüfung des leeren `BUILD_DONE`-Markers mit `test -s`; korrekt ist `test -e`. Beide Versuche erzeugten keine BAMs. Die unerfüllbaren Finalizer `2071848` und `2072975` wurden beendet.

### Aktiver Mappingworkflow

- Produktives Mappingarray: `2073203`, vier Assemblies × vier FASTQ-Chunks, maximal vier parallele Tasks, `slim18`, 16 CPUs und 48 GiB RAM je Task.
- Mappingparameter: Minimap2 `-ax map-ont --secondary=no`, anschließend koordinatensortiertes BAM und BAI.
- Abhängiger Finalizer `2073204` erzeugt je Assembly `raw_primary`, `MAPQ20` und `junction_evidence` als BAM/BAI. Junctionevidenz verlangt MAPQ ≥20 und mindestens 50 ausgerichtete Basen auf beiden Seiten derselben Backbone/Insert-Junction.
- Außerdem werden je Assembly drei BigWigs für Roh-, MAPQ20- und Junction-Coverage erzeugt.
- Auditjob `2073209` wartet auf den Finalizer und prüft BAM-Header gegen `chrom.sizes`, `samtools quickcheck`, BigBed/BigWig, Hubkonfiguration, Dateiprüfsummen und erzeugt `validation.txt`.

### Lokaler Spiegel

- Lokaler Pfad: `day5/genome_build_direction_thresholds/`.
- Aktueller Spiegel: 3.512 Dateien und 271.071.747 Byte; alle 3.503 Build-Prüfsummen lokal gültig.
- Enthalten sind Einzel-FASTAs, vier Multi-FASTAs/2bit-Dateien, BigBed-Annotationen, Hubkonfiguration, Manifeste und Skripte. Große BAM/BAI-Dateien bleiben gemäß Planung auf Cluster/Hosting; BigWigs und finale Auditdateien werden nach Abschluss ergänzt.
- Excel bleibt technisch blockiert, weil der vom Spreadsheets-Workflow vorgeschriebene Workspace-Dependency-Loader für `@oai/artifact-tool` in dieser Sitzung nicht verfügbar ist. Es wurde keine alternative, nicht freigegebene Excel-Bibliothek verwendet.

## 7. Aktueller Raven-Assembly-Bestand geprüft

**Bearbeitender Agent:** `Cluster4`

- **Methode:** Read-only-Zählung nichtleerer `assembly.fasta`-Dateien sowie ID-Abgleich zwischen Hauptlauf, Retry und Faulty-Kopie auf dem Cluster.
- **Hauptlauf:** `/work/project/becstr_013/cluster2_flye_work/raven_1588/` enthält 1.483 eindeutige nichtleere Assembly-FASTAs.
- **Retry:** `/work/project/becstr_013/cluster2_flye_work/raven_1588_retry16g_20260726/` enthält aktuell 27 weitere nichtleere Assembly-FASTAs; diese IDs überlappen nicht mit den 1.483 Hauptlauf-IDs.
- **Kombiniert:** Damit sind aktuell 1.510 eindeutige Raven-Assemblies sichtbar.
- **Faulty-Kopie:** Die 399 `assembly_FAULTY.fasta` unter `raven_results_faulty_20260726/` sind Kopien von Hauptlauf-Outputs und werden nicht zusätzlich gezählt.
- **Jobstatus:** Retry-Job `2071721` ist nicht mehr aktiv; die Statusaufstellung enthält 20 `COMPLETED`, 83 `FAILED`, 1 `FAILED` mit Exit 11 und 1 `CANCELLED`. Die 27 nichtleeren FASTAs werden deshalb separat anhand ihres Inhalts und nicht nur anhand des Statusmarkers bewertet.

## 8. Cluster4-Raven-Erweiterung gestartet

**Bearbeitender Agent:** `Cluster4`

- **Input:** 1.510 eindeutige nichtleere Raven-Assemblies aus Hauptlauf und Retry; 190 davon überschneiden sich mit dem bisherigen 202er Cluster4-Datensatz.
- **Neue Menge:** 1.320 Raven-IDs werden neu gemappt; zusammen mit den bestehenden 202 IDs wird der kombinierte Datensatz 1.522 eindeutige Zeilen enthalten.
- **Methode:** Identisch zum Flye-Lauf: je ID zwei Minimap2-Aufrufe mit `-ax map-ont --secondary=yes -N 10000 -p 0.0`, normale und reverse-komplementäre vollständige Backbone-Insert-Referenz, alle Alignments erhalten, Parserfilter aligned Query-Basen >=50 und Identität >=70%.
- **Pfad:** `/work/project/becstr_013/cluster4_version2_raven_new/`; Manifest `manifest_new.tsv` enthält 1.320 Einträge plus Header.
- **SLURM:** Mapping-Array `2071864` (`1-1320%100`, 4 CPUs, 4G, 1h pro Task); abhängiger Finalizer `2072334`.
- **Technische Korrektur:** Raven speichert `assembly.fasta` direkt unter `<ID>/assembly.fasta`, anders als Flye unter `<ID>/assembly/assembly.fasta`; das Manifest-Skript wurde vor der Einreichung entsprechend korrigiert und anschließend mit 1.320 neuen IDs erfolgreich validiert.

## 9. Raven-Mapping und Main-Run-Vergleich abgeschlossen

**Bearbeitender Agent:** `Cluster4`

- **Mapping:** Alle 1.320 neuen Raven-Tasks aus Array `2071864` erzeugten vollständige Resultate; der direkte Finalizer `2073202` lief mit Exit-Code `0:0` erfolgreich.
- **Kombinierter Output:** `day4/workflows/cluster4_version2/raven_new_1320/results/cluster4_version2_first_202_plus_raven_new_summary.xlsx`; 1.522 eindeutige IDs, jeweils in `all_alignments` und `MAPQ_ge_20`.
- **Vergleichsmethode:** `counts_by_target.tsv` wurde pro ID über die höhere Read-Anzahl (`normal` vs. `revcomp`) in einen Main-Run-Richtungsaufruf umgewandelt. `revcomp` wurde als `reverse` verglichen; Main-Run-Ties wurden nicht als entscheidbare Vergleiche gewertet.
- **Übereinstimmung `all_alignments`:** 525 entscheidbare Vergleiche; 399 gleich, 126 verschieden = **76,00 %**.
- **Übereinstimmung `MAPQ_ge_20`:** 842 entscheidbare Vergleiche; 759 gleich, 83 verschieden = **90,14 %**.
- **Neue Raven-IDs allein:** `all_alignments` 367/479 = **76,62 %**; `MAPQ_ge_20` 697/772 = **90,28 %**.
- **Richtungsaufrufe im kombinierten Datensatz:** `all_alignments`: 307 normal, 228 reverse, 742 ambiguous, 245 no_call. `MAPQ_ge_20`: 438 normal, 410 reverse, 111 ambiguous, 563 no_call.
- **Interpretation:** Die Prozentwerte zeigen Übereinstimmung mit dem Readcount-basierten Main-Run, nicht automatisch biologische Wahrheit. Der MAPQ-Filter erhöht die Übereinstimmung deutlich, während viele zusätzliche Raven-Fälle weiterhin `ambiguous` oder `no_call` bleiben.
## 10. Zwischenstand der 16G-Retries

**Bearbeitender Agent:** `Cluster3`

- **Methode:** Read-only-Abfrage von `squeue`, Retry-Statusdateien, nichtleeren FASTA-Dateien und Outputgrößen; keine Jobs oder Ergebnisse verändert.
- **Raven-16G-Retry `2071721`:** Nicht mehr aktiv. Statusdateien: 20 `COMPLETED`, 84 `FAILED`, 1 alter `RUNNING`-Marker. Es liegen 27 nichtleere Retry-FASTAs vor; die zusätzlichen 7 stammen aus formal fehlgeschlagenen, aber outputerzeugenden Runs und werden separat bewertet.
- **Raven-Gesamtstand:** 1.483 eindeutige nichtleere FASTAs im Hauptlauf plus 27 nichtüberlappende Retry-FASTAs = 1.510 eindeutige Assemblies. Die 399 `FAULTY`-Kopien sind darin nicht zusätzlich zu zählen.
- **Flye-16G-Retry `2070896`:** Weiter aktiv mit 100 Tasks `RUNNING`; der Rest des Arrays ist `PENDING`. In `flye_relaxed_1588_v3` stehen aktuell 47 `FAILED` und 101 `RUNNING`-Statusdateien, aber noch keine fertige FASTA. Die Differenz von 101 zu 100 ist ein alter Statusmarker eines bereits beendeten Tasks.
- **Interpretation:** Die 801 zuvor bewahrten Flye-Assemblies bleiben die bisherige fertige Basis; der neue 16G-Lauf hat noch keine zusätzliche fertige Assembly geliefert. Die Parallel-Mappingauswertung der 1.510 Raven-Assemblies durch Cluster4 ist laut den nachfolgenden Einträgen abgeschlossen.

## 11. Nachtlauf-Bereitschaft des richtungsabhängigen Custom-Genome-Mappings

**Bearbeitender Agent:** `Codex (/root)`

- **Methode:** Read-only-Prüfung von `squeue`, `scontrol`, Mappinglogs und Cluster-Speicher am 26.07.2026; es wurden keine Jobs verändert.
- **Aktiver Stand:** Alle 16 Tasks des Mappingarrays `2073203` liefen im Status `RUNNING`. Zu diesem Kontrollzeitpunkt waren 24 vollständige Minimap2-Batches protokolliert; nichtleere Fehlerlogs des Arrays waren nicht vorhanden.
- **Automatische Kette:** Finalizerarray `2073204` wartet mit `afterok:2073203_*`; Auditjob `2073209` wartet mit `afterok:2073204_*`. Der Workflow ist damit unabhängig von SSH-Sitzung und Agentenaufsicht.
- **Ressourcen:** Mapping- und Finalizer-Zeitlimit jeweils 24 Stunden, Audit-Zeitlimit 8 Stunden. Auf `/work` waren 28 TB frei.
- **Abweichungs-/Fehlerverhalten:** Die Folgestufen starten nur bei erfolgreichem Abschluss aller jeweiligen Vorgänger. Bei einem Taskfehler bleibt die Kette daher sicher stehen, statt unvollständige Ergebnisse als final auszugeben.
- **Interpretation:** Die Prozentwerte zeigen Ãœbereinstimmung mit dem Readcount-basierten Main-Run, nicht automatisch biologische Wahrheit. Der MAPQ-Filter erhÃ¶ht die Ãœbereinstimmung deutlich, wÃ¤hrend viele zusÃ¤tzliche Raven-FÃ¤lle weiterhin `ambiguous` oder `no_call` bleiben.

## 11. Minimap2-Prüfung der sieben Mappingexamples

**Bearbeitender Agent:** `Codex`

- **Input:** Ausschließlich die sieben FASTQ-Dateien unter `mappingexamples/`; die zuvor gefundene Original-FASTQ wurde nicht verwendet.
- **Targets:** vollständige Multi-FASTA-Referenzen `pGP85.fasta` und `pGP95.fasta` sowie eine kombinierte Referenz aus `genome.fa` und `pGP564_backbone.fa`.
- **Methode:** 21 unabhängige parallele Prozesse, je ein Prozess pro Kombination aus sieben FASTQ-Examples und drei Mappingtargets; Minimap2 2.31, `-t 1 -ax map-ont --secondary=no`, Samtools 1.24.
- **Output:** `day5/minimap2_mappingexamples_20260726/` mit 21 BAMs, 21 Flagstat-Dateien, `metrics.tsv`, `mapping_report.html` und `minimap2_mappingexamples_results.xlsx`.
- **Ergebnisse über alle sieben Examples:** pGP85: 8/4.654 Reads = **0,171895 %**; pGP95: 8/4.654 = **0,171895 %**; Hefe + Backbone: 9/4.654 = **0,193382 %**. In der kombinierten Referenz erfüllten 7 Reads MAPQ ≥20 = **0,150408 %**.
- **Excel-Struktur:** `Übersicht` plus je ein Sheet für `pGP85`, `pGP95` und `Hefe + Backbone`; die zentrale Spalte ist `Mapped (%)` bezogen auf alle Reads des jeweiligen FASTQ-Examples.
- **HTML:** `mapping_report.html` enthält ein kleines Balkendiagramm und eine vollständige Tabelle der 21 Kombinationen.
- **Technische Abweichung:** Der vorgeschriebene `@oai/artifact-tool`-Lader war in der Sitzung nicht verfügbar; die ausdrücklich angeforderte Excel-Datei wurde deshalb mit `openpyxl` erzeugt und durch erneutes Einlesen auf Sheetnamen, Zeilenanzahl und zentrale Werte geprüft.
## 12. Flye-Array auf 10 parallele Tasks gedrosselt

**Bearbeitender Agent:** `Cluster3`

- **Methode:** Live-Änderung der SLURM-Array-Drosselung mit `scontrol update JobId=2070896 ArrayTaskThrottle=10`.
- **Job:** `2070896`, Flye-16G-Retry.
- **Bestätigte Konfiguration:** `ArrayTaskId=153-787%10`, 8 CPUs und 16G RAM je Task.
- **Verhalten:** Bereits laufende Tasks werden von SLURM nicht automatisch abgebrochen; sie laufen aus. Nach ihrem Ende werden höchstens 10 wartende Tasks gleichzeitig neu gestartet.
- **Output:** Keine Assemblydateien wurden verändert oder gelöscht.
## 13. Aktuell blockierte Flye-Ressourcen

**Bearbeitender Agent:** `Cluster3`

- **Methode:** Read-only-Abfrage mit `squeue` und `scontrol` für Job `2070896` sowie den aktiven Flye-Monitor.
- **Flye:** Aktuell 100 bereits laufende Tasks; je 8 CPUs und 16G RAM = zusammen 800 CPUs und 1.600G angeforderter RAM.
- **Throttle:** Neue Nachstarts sind auf maximal 10 parallel begrenzt; die bereits laufenden 100 Tasks werden nicht vorzeitig beendet.
- **Monitor:** Zusätzlich läuft `2057067` mit 1 CPU und 4G RAM.
- **Gesamt der aktuell aktiven Flye-bezogenen Jobs:** 801 CPUs und 1.604G angeforderter RAM. Pending-Tasks reservieren dabei keine laufenden Ressourcen.
- **Interpretation:** Die 801 zuvor bewahrten Flye-Assemblies bleiben die bisherige fertige Basis; der neue 16G-Lauf hat noch keine zusätzliche fertige Assembly geliefert. Die Parallel-Mappingauswertung der 1.510 Raven-Assemblies durch Cluster4 ist laut den nachfolgenden Einträgen abgeschlossen.

## 12. Zusatzmapping des großen Day2-Datensatzes mit MAPQ20

**Bearbeitender Agent:** `Codex`

- **Input:** `Day2/Pipeline2/dorado_reads.fastq`, 324.008 FASTQ-Reads. Andere FASTQ-Dateien wurden nicht verwendet.
- **Targets:** `pGP85.fasta`, `pGP95.fasta` sowie die kombinierte Referenz aus `genome.fa` und `pGP564_backbone.fa`.
- **Methode:** Drei parallele Minimap2-2.31-Laeufe mit `-t 1 -ax map-ont --secondary=no`; anschliessend wurden eindeutige Readnamen aus den BAMs mit MAPQ >=20 gezaehlt. Damit zaehlt der Nenner FASTQ-Reads und nicht Alignmentzeilen.
- **Ergebnisse:** pGP85: 5.454/324.008 = **1,6833 %**; pGP95: 5.289/324.008 = **1,6324 %**; Hefe + Backbone: 17.685/324.008 = **5,4582 %**.
- **Output:** `day5/day2_dorado_mapq20_20260726/` mit drei BAMs, Logs, Flagstats, `metrics.tsv`, `day2_dorado_mapq20_results.xlsx` und `day2_dorado_mapq20_report.html`.
- **Excel:** `Uebersicht` plus je ein Sheet fuer pGP85, pGP95 und Hefe + Backbone; die zentrale Spalte ist `Mapped MAPQ >=20 (%)`.
- **Technische Korrektur:** Die erste vorlaeufige Auswertung basierte auf `flagstat`-Alignmentzeilen. Sie wurde korrigiert auf eindeutige Readnamen und die tatsaechliche FASTQ-Readzahl 324.008.
- **Technische Korrektur:** Die erste vorlaeufige Auswertung basierte auf `flagstat`-Alignmentzeilen. Sie wurde korrigiert auf eindeutige Readnamen und die tatsaechliche FASTQ-Readzahl 324.008.

## 13. LRZ-Datensatz auf dem BMC-Cluster gefunden

**Bearbeitender Agent:** `Codex`

- **Methode:** Read-only-SSH-Pruefung auf `MBIOHW30.bio.med.uni-muenchen.de` mit `find`; keine Dateien oder Jobs veraendert.
- **Datensatz:** `20230920_DNA_Korber_Drin3plex` ist bereits unter `/work/project/becstr_013/` vorhanden.
- **Gefundene Dateien:** ZIP-Archiv mit 23.191.444.842 Byte; komprimierter FASTQ mit 23.184.412.941 Byte; entpackter `barcode48.fastq` mit 43.448.807.798 Byte.
- **Primaerer Pfad fuer Mapping:** `/work/project/becstr_013/unpacked_20230920_DNA_Korber_Drin3plex/20230920_DNA_Korber_Drin3plex/20230920_1625_2D_PAS00288_bab6ed79/fastq_pass/barcode48.fastq`.
- **Technischer Hinweis:** Eine zweite Kopie des komprimierten FASTQ liegt unter `cluster2_flye_work/unpacked_20230920_DNA_Korber_Drin3plex/`; fuer weitere Arbeiten soll der primaere Pfad verwendet werden.
- **Technischer Hinweis:** Eine zweite Kopie des komprimierten FASTQ liegt unter `cluster2_flye_work/unpacked_20230920_DNA_Korber_Drin3plex/`; fuer weitere Arbeiten soll der primaere Pfad verwendet werden.

## 14. Mapping des grossen LRZ-Datensatzes auf dem Cluster gestartet

**Bearbeitender Agent:** `Codex`

- **Input:** Entpackter FASTQ `.../fastq_pass/barcode48.fastq` unter `/work/project/becstr_013/unpacked_20230920_DNA_Korber_Drin3plex/`; die komprimierte Datei und das ZIP werden nicht als Mappinginput verwendet.
- **Targets:** pGP85, pGP95 und kombinierte Hefe-Backbone-Referenz.
- **Methode:** SLURM-Array mit drei Tasks, Minimap2 `-ax map-ont --secondary=no`, 16 CPUs und 64G RAM je Task; MAPQ-Filter `samtools view -q 20 -F 4` vor Sortierung. Die Auswertung zaehlt eindeutige Readnamen gegen die FASTQ-Gesamtzahl.
- **Job:** `2073228`, Array `0-2`, Partition `slim18`; zum Startzeitpunkt liefen alle drei Tasks auf `slim25` im Status `RUNNING`.
- **Output:** `/work/project/becstr_013/large_drin3plex_mapq20_20260726/` mit BAM/BAI, Logs und MAPQ20-Metriken.
- **Technische Korrektur:** Das Hefegenom wurde aus dem tatsaechlichen Clusterpfad `directional_ucsc_work/inputs/genome.fa` verwendet; die Referenzvorbereitung und alle drei Jobinputs wurden vor Einreichung mit `test -s` validiert.

## 15. Verkuerzte Zusammenfassung der Fortschritte aus Tag 4 und Tag 5

**Bearbeitender Agent:** `master2`

- **Input:** `day4.md` und `day5.md`.
- **Output:** [`day5/day4_day5_short_summary.md`](day5/day4_day5_short_summary.md).
- Das Dokument bündelt die grossen Meilensteine, Iterationen und neuen Daten des Reverse-Complement-Main-Workflows einschließlich finaler Read-Zahlen, Richtungsverteilung, Ausschlusskriterien und QC.
- Zusätzlich sind die Zustände und Vergleichsergebnisse der Flye- und Raven-Workflows, die Cluster4-Erweiterungen und Retries, der richtungsabhängige UCSC-Genome-Hub sowie die grossen gemeinsamen Mapping-Workflows dokumentiert.
- Die Originalprotokolle `day4.md` und `day5.md` wurden nicht gekürzt oder entfernt; die neue Datei ist eine reine Arbeitszusammenfassung.

## 16. Verlagerung des Arbeitsorts in das Git-Repository

**Bearbeitender Agent:** `Codex`

- **Methode:** Übertragung der bisherigen Projektdateien und Ergebnisordner aus dem übergeordneten Projektordner in `Sequenz-Analyse_Praktikum_James-Teo/`, das als Git-Repository erkannt wurde.
- **Output:** Repository-interne Kopien der Tagesordner, Methoden, Skripte, Referenzen, Ergebnisdateien und der Kurzfassung `day5/day4_day5_short_summary.md`.
- **Validierung:** Der zentrale `day5/`-Ordner wurde mit 3.627 Dateien vollständig übertragen; die entsprechenden Dateien aus `Day2` und `day3` sind ebenfalls im Repository vorhanden.
- **Technische Abweichung:** Einige alte Root-Duplikate konnten wegen temporärer OneDrive-Dateisperren nicht entfernt werden. Sie sind nicht mehr der Arbeitsort; `agents.md` legt verbindlich die Git-Repository-Wurzel als neuen Arbeitsort fest.
## 14. Gesamtberechnung der 891 Flye-IDs

**Bearbeitender Agent:** `Cluster3`

- **Input:** `day4/workflows/cluster4_version2/flye_new_689/results/cluster4_version2_first_202_plus_flye_new_summary.xlsx`; beide Sheets enthalten 891 IDs.
- **Wichtige Unterscheidung:** Die Werte 69,57 %/88,57 % für die alten 202 und 56,98 %/62,81 % für die neuen 689 messen die Übereinstimmung mit dem Readcount-Main-Run. Sie sind keine Mapping-Erfolgsquoten und dürfen nicht als einfache Mittelwerte kombiniert werden.
- **Sheet `all_alignments`:** 80 `normal` + 327 `reverse` = 407 eindeutige Richtungsaufrufe, also 45,68 % von 891. Nicht eindeutig: 350 `ambiguous` (39,28 %) und 134 `no_call` (15,04 %), zusammen 484 (54,32 %).
- **Sheet `MAPQ_ge_20`:** 129 `normal` + 346 `reverse` = 475 eindeutige Richtungsaufrufe, also 53,31 % von 891. Nicht eindeutig: 173 `ambiguous` (19,42 %) und 243 `no_call` (27,27 %), zusammen 416 (46,69 %).
- **Übereinstimmung mit dem Main-Run:** `all_alignments`: 232/397 entscheidbaren Vergleichen = 58,44 %. `MAPQ_ge_20`: 312/468 entscheidbaren Vergleichen = 66,67 %.
- **Interpretation:** Alle 891 IDs wurden technisch gemappt. `ambiguous` bedeutet konkurrierende Richtungsnachweise; `no_call` bedeutet keinen ausreichenden qualifizierenden Richtungsnachweis. `no_call` heißt daher nicht, dass der Versuch nicht gestartet wurde, sondern dass kein belastbarer Aufruf erzeugt werden konnte.

## 17. Rückverlagerung aus dem Git-Unterordner

**Bearbeitender Agent:** `Codex`

- **Methode:** Rückübertragung der Projektdateien aus `Sequenz-Analyse_Praktikum_James-Teo/` in den normalen Projektordner; der Unterordner `.git` blieb erhalten.
- **Output:** `day5/` mit 3.627 Dateien sowie die übrigen Skripte, Methoden, Tagesordner und Ergebnisse liegen wieder im normalen Oberordner.
- **Dokumentation:** `agents.md` wurde aktualisiert; ab sofort ist wieder `C:\Users\teohe\OneDrive\Desktop\.AAAA-Praktikum` der aktive Arbeitsort und `day5.md` dort das Hauptprotokoll.
- **Technische Abweichung:** Einzelne Duplikate können wegen OneDrive-Dateisperren noch im Git-Unterordner vorhanden sein. Sie sind nicht der aktive Arbeitsstand; neue Arbeiten dürfen ausschließlich im normalen Oberordner erfolgen.
