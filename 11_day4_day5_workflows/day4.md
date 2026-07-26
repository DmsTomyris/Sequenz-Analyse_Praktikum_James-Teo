# Day 4 – Hauptprotokoll

Dieses Dokument ist ab Tag 4 das verbindliche Arbeitsprotokoll für alle Agenten. Vor jedem Arbeitsschritt wird `day4.md` gelesen; nach jedem signifikanten Schritt wird der Eintrag hier fortgeführt.

## 1. Start von Tag 4 und Umstellung der Hauptablage

**Bearbeitender Agent:** `master2`

### Methode

- Der aktuelle Hauptstand wurde aus `day3.md` und `agents.md` geprüft.
- `agents.md` wurde auf den neuen Protokollort `day4.md` umgestellt.
- Der neue Arbeitsordner `day4/` wurde erstellt.

### Output

- Neues Hauptprotokoll: `day4.md`
- Neuer Hauptordner für alle Day-4-Skripte und -Ergebnisse: `day4/`

### Regel ab diesem Schritt

Alle neuen digitalen Arbeitsschritte, Skripte, Zwischenprodukte, Ergebnisdateien, Logs und Tabellen gehören ab jetzt in `day4/` und werden in `day4.md` dokumentiert. Die historischen Ordner und Protokolle `day2`, `day2.5` und `day3` bleiben unverändert erhalten.

## 2. Prüfung einer aktuellen PAF-Datei durch master3

**Bearbeitender Agent:** `master3`

- **Input:** `/work/project/becstr_013/mapping_main_filtered_junction_live/results/block_001320/mapping.paf`.
- **Methode:** Nur-Lese-SSH-Abfrage; Ausgabe der ersten vier PAF-Zeilen mit `sed -n 1,4p`.
- **Ergebnis:** Die Pflichtfelder enthalten Query-/Target-IDs und -Längen, Query-/Target-Koordinaten, Strand, Anzahl Matches, Alignment-Blocklänge und Mapping-Qualität. Die gezeigten optionalen Tags umfassen `tp`, `cm`, `s1`, `s2` und `dv`.
- **Bewertung:** Ein per-base-FASTQ-Q-Score ist nicht in diesen PAF-Zeilen gespeichert. Die Alignment-Matches und die Alignment-Blocklänge sind vorhanden; ein CIGAR-Tag (`cg:Z`) war in den gezeigten Zeilen nicht enthalten.

## 3. Reverse-Komplement-Bibliothek auf dem BMC-HPC

**Bearbeitender Agent:** `Codex (/root)`

### Methode

- Vor Beginn wurden dieses Hauptprotokoll, der lokale Dateiänderungsstand und das noch nicht vorhandene Clusterziel geprüft.
- Ein reproduzierbarer Python-Builder wurde lokal unter `day4/build_revcomp_library.py` erstellt, syntaktisch geprüft und gegen alle 1.588 lokalen Inserts getestet.
- Builder und Jobdatei wurden prüfsummengleich nach `/work/project/becstr_013/reversed_komplement/library/` übertragen. Die Übertragung erfolgte über eindeutige temporäre Namen; vor der Installation und vor dem Jobstart wurde geprüft, dass keine gleichnamigen Ziel- oder Ergebnisdateien vorhanden waren.
- Der eigentliche Lauf erfolgte auf einem Compute-Node als SLURM-Job `2062282` mit einer angeforderten CPU, 4 GB RAM und 30 Minuten Zeitlimit.
- Die erzeugte FASTA wurde nach dem Schreiben vollständig neu eingelesen. Für jedes Paar wurden Recordlänge, Insertkoordinaten, beide Backboneflanken, gültige IUPAC-DNA-Zeichen und die Rücktransformation des Reverse-Komplements mit dem Originalinsert verglichen.

### Input und Parameter

- Backbone: `/work/project/becstr_013/pGP564_backbone.fa`, 1 Record, 7.371 bp, SHA-256 `b3171c3568f405d16b4790ba9fb30c9509e74d34481430cfdb4f002e82a5f0f0`
- Inserts: `/work/project/becstr_013/minimal_inserts.fa`, 1.588 eindeutige Records, SHA-256 `132e4b9b6189d6889ded4a357248e8b48cbc733a70f3154654836a85b9220d95`
- Insertposition: zwischen Backboneposition 5042 und 5043
- Targets pro Insert: `<Insert-ID>` mit unverändertem Insert und `<Insert-ID>-revcomp` mit Reverse-Komplement ausschließlich des Inserts
- Der Backbone wurde nicht reverse-komplementiert.

### Output und Ergebnisse

- FASTA: `/work/project/becstr_013/reversed_komplement/library/yeast_backbone_insert_revcomp_3176.fasta`
- Validierung: `/work/project/becstr_013/reversed_komplement/library/validation.txt`
- Prüfsummen: `/work/project/becstr_013/reversed_komplement/library/checksums.sha256`
- Reproduktionsdateien: `build_revcomp_library.py` und `build_revcomp_library.slurm` im gleichen Clusterordner sowie lokal unter `day4/`
- Dateigröße der FASTA: 58.718.076 Byte
- Recordzahl: exakt 3.176, davon 1.588 normal und 1.588 mit Suffix `-revcomp`
- Eindeutige IDs: 3.176
- Recordlängen: 7.476 bis 26.515 bp
- SHA-256 der FASTA: `9475580d097a115d0ca4a606475084eaaae8ec0994264f1df4b4a2cd57baa00e`
- Validierungsstatus: `PASS`; gültige DNA-Zeichen, identische Backboneflanken, Insertkoordinaten und -längen sowie Reverse-Komplement-Roundtrip bestanden.
- SLURM-Status: `COMPLETED`, Exit-Code `0:0`, Laufzeit 7 Sekunden; Standardfehlerdatei leer.

### Technische Korrekturen und Abweichungen

- Anders als bei der früheren Reverse-Variante, die nur die Basenreihenfolge umkehrte, wurde hier ausdrücklich das echte Reverse-Komplement des Inserts erzeugt.
- Die Bibliothek wurde unter dem neuen, getrennten Pfad `reversed_komplement/library/` abgelegt; bestehende Referenzbibliotheken wurden nicht verändert.
- Die auf dem Cluster installierte SLURM-Version expandierte `%x` im absoluten Logpfad nicht. Die beiden Joblogs heißen deshalb wörtlich `%x-2062282.out` und `%x-2062282.err`; Inhalt und Jobausführung sind davon nicht betroffen.
- Das für den Clusterzugang verwendete Passwort wurde weder in Skripten noch im Protokoll gespeichert.

## 4. Paarweiser Export der Referenzen für `cluster4_version2`

**Bearbeitender Agent:** `Codex (/root)`

### Methode

- Vor Beginn wurden `day4.md`, der lokale Änderungsstand und das Clusterziel `/work/project/becstr_013/cluster4_version2/input/references/` geprüft. Das Ziel existierte noch nicht.
- Die validierte kombinierte Bibliothek wurde mit `day4/export_cluster4_reference_pairs.py` in je einen Unterordner pro Insert aufgeteilt.
- Der Export wurde zunächst vollständig in einem temporären Nachbarordner aufgebaut. Erst nach erneutem Einlesen und Sequenzvergleich aller 3.176 FASTA-Dateien wurde der fertige Ordner atomisch als `references/` veröffentlicht.
- Ein exklusiver Lock und Existenzprüfungen verhinderten parallele Erzeugung und das Überschreiben vorhandener Dateien.

### Input und Parameter

- Input: `/work/project/becstr_013/reversed_komplement/library/yeast_backbone_insert_revcomp_3176.fasta`
- Inputgröße: 58.718.076 Byte
- Input-SHA-256: `9475580d097a115d0ca4a606475084eaaae8ec0994264f1df4b4a2cd57baa00e`
- Normale IDs: `<Insert-ID>`
- Reverse-Komplement-IDs: `<Insert-ID>-revcomp`
- Dateinamen pro Insertordner: `normal_backbone_insert.fasta` und `reverse_complement_backbone_insert.fasta`

### Output und Ergebnisse

- Ziel: `/work/project/becstr_013/cluster4_version2/input/references/<INSERT-ID>/`
- SLURM-Job: `2062283`, Status `COMPLETED`, Exit-Code `0:0`, Laufzeit 29 Sekunden
- Insertordner: exakt 1.588
- Normale FASTA-Dateien: exakt 1.588
- Reverse-Komplement-FASTA-Dateien: exakt 1.588
- FASTA-Dateien insgesamt: exakt 3.176 mit zusammen 58.718.076 Byte
- Jeder Insertordner enthält exakt die beiden vorgegebenen FASTA-Dateien.
- Beispielprüfung: `YGPM-8k09/normal_backbone_insert.fasta` hat den Header `>YGPM-8k09`; `YGPM-8k09/reverse_complement_backbone_insert.fasta` hat den Header `>YGPM-8k09-revcomp`.
- Gesamtvalidierung: `PASS`; Verzeichnis- und Dateinamensmenge, erneutes FASTA-Einlesen und vollständige Sequenzidentität zur kombinierten Quellbibliothek bestanden.
- Zusätzliche Metadaten im Wurzelordner: `validation.txt` und `checksums.sha256` mit 3.177 Prüfsummenzeilen für alle 3.176 FASTA-Dateien und den Validierungsbericht.
- Keine temporären Ordner oder Lockdateien blieben zurück; die Job-Standardfehlerdatei ist leer.

### Reproduktionsdateien und technische Hinweise

- Lokal: `day4/export_cluster4_reference_pairs.py` und `day4/export_cluster4_reference_pairs.slurm`
- Cluster: dieselben Dateien unter `/work/project/becstr_013/reversed_komplement/library/`
- Joblogs: `/work/project/becstr_013/reversed_komplement/library/logs/cluster4-reference-export-2062283.out` und `.err`
- Es wurden keine vorhandenen Referenzen überschrieben.
- Das für den Clusterzugang verwendete Passwort wurde weder in Skripten noch im Protokoll gespeichert.

## 5. Start des eigenen Reverse-Komplement-Hauptruns

**Bearbeitender Agent:** `Codex (/root)`

### Methode

- Vor dem Start wurden `day4.md`, der lokale Dateiänderungsstand, die kombinierte Referenz, die bereits validierten Full-Dataset-Chunks und die aktuelle SLURM-Queue geprüft.
- Der neue Lauf verwendet die kombinierte Bibliothek direkt und ignoriert die zusätzliche, insertweise Ablage unter `cluster4_version2/input/references/` vollständig.
- Gemappt werden alle vier validierten, ungetrimmten Full-Dataset-Chunks mit zusammen 1.495.785 Reads und 21.409.671.313 Basen.
- Minimap2 läuft mit `-x map-ont --secondary=no`. Ein Read/Target-Paar qualifiziert sich nur, wenn seine PAF-Alignments gemeinsam sowohl den Insertbereich als auch mindestens einen Backbonebereich abdecken.
- Pro Read wird nur ein eindeutig bestes qualifizierendes Target gezählt. Gleich gute Targets nach `aligned_matches`, `aligned_block_bases` und `max_mapq` werden als mehrdeutig protokolliert und von der Normal-/Reverse-Komplement-Zählung ausgeschlossen. Damit wird das frühere lexikographische Tie-Breaking vermieden, das eine Richtung künstlich bevorzugen konnte.

### Input und Parameter

- Referenz: `/work/project/becstr_013/reversed_komplement/library/yeast_backbone_insert_revcomp_3176.fasta`
- Referenz-SHA-256: `9475580d097a115d0ca4a606475084eaaae8ec0994264f1df4b4a2cd57baa00e`
- Referenzrecords: 3.176, davon 1.588 normal und 1.588 mit Suffix `-revcomp`
- Read-Chunks: `/work/project/becstr_013/mapping_main_full_paf_optimized/chunks/chunk_00.fastq` bis `chunk_03.fastq`; ausschließlich lesend wiederverwendet, um etwa 43 GB unnötige Datenduplikation zu vermeiden
- Tool: Minimap2 `2.10-r761`, Preset `map-ont`, keine Secondary Alignments
- Insertbeginn: Targetkoordinate 5042, entsprechend Einfügestelle zwischen Backboneposition 5042 und 5043
- Ressourcen Mapping: vier parallele Array-Tasks, je 16 CPUs, 32 GB RAM und 24 Stunden Zeitlimit auf `slim16`
- Ressourcen Finalisierung: 2 CPUs, 16 GB RAM und 4 Stunden

### Output, Jobs und aktueller Status

- Eigenes Outputverzeichnis: `/work/project/becstr_013/reversed_komplement/main_run/`
- Mapping-Array: SLURM-Job `2063861`, Tasks `_0` bis `_3`
- Abhängiger Finalizer: SLURM-Job `2063865` mit `afterok:2063861`
- Status bei der Startkontrolle: alle vier Mapping-Tasks `RUNNING` auf `slim09`, zusammen 64 CPUs und 128 GB; Finalizer korrekt `PENDING (Dependency)`.
- Alle vier Minimap2-Logs bestätigen den erfolgreichen Indexaufbau für 3.176 Targetsequenzen.
- Pro Chunk werden `mapping.paf`, `best_hits.tsv`, `ambiguous_hits.tsv`, `counts.tsv`, `stats.tsv`, Prüfsummen, Status und `DONE` separat geschrieben.
- Nach erfolgreichem Abschluss aller vier Tasks erzeugt der Finalizer `counts_by_target.tsv`, `direction_summary.tsv`, `run_summary.tsv`, Gesamtprüfsummen und den finalen `DONE`-Marker.

### Reproduktionsdateien und technische Korrekturen

- Lokal unter `day4/`: `aggregate_revcomp_junction_paf.py`, `combine_revcomp_main_counts.py`, `main_revcomp_array.slurm` und `main_revcomp_finalize.slurm`
- Clusterkopien: `/work/project/becstr_013/reversed_komplement/main_run/scripts/`
- Die lokalen und Remote-SHA-256-Prüfsummen aller vier Skripte stimmen überein; Python-3.6-Kompilierung, Bash-Syntax, synthetischer Junction-Test, Tie-Ausschluss, Count-Kombination und Überschreibschutz bestanden.
- Eine erste geplante Login-Node-Prüfung hätte die vier großen FASTQ-Dateien vollständig gescannt. Sie wurde sofort abgebrochen und durch Metadaten plus den bereits vorhandenen PASS-Validierungsbericht ersetzt; große Datenverarbeitung bleibt auf den Compute-Nodes.
- Der Run verwendet keine Dateien aus dem zu ignorierenden insertweisen Referenzbaum.
- Das für den Clusterzugang verwendete Passwort wurde weder in Skripten noch im Protokoll gespeichert.

## 6. Live-Ressourcensnapshot aller Projektjobs

**Bearbeitender Agent:** `Codex (/root)`

### Methode und Zeitpunkt

- Nur-Lese-Abfrage am 25.07.2026 zwischen 09:56:42 und 09:58:11 Uhr CEST.
- SLURM-Reservierungen wurden mit `squeue` und `scontrol`, tatsächliche CPU-/RAM-Telemetrie mit `sstat` für die physischen Batch-Schritte der Array-Tasks ermittelt.
- Speicherbelegung wurde mit `du -s -B1` für Projekt und aktive Outputbäume gemessen. Die Wachstumsrate basiert auf zwei 89 Sekunden auseinanderliegenden Snapshots und ist daher nur eine kurzfristige Momentabschätzung.

### Gesamtnutzung

- Laufende Tasks: 111
- Reservierte CPUs: 1.250; entsprechend 1.250 reservierte CPU-Stunden je weiterer Walltime-Stunde
- Tatsächlich gemessene mittlere CPU-Nutzung: ca. 605,2 Kerne bzw. 605,2 CPU-Stunden je Stunde; Gesamtauslastung der reservierten CPUs ca. 48,4 %
- Reservierter RAM: 2.352 GiB bzw. 2,297 TiB
- Aktuelle summierte RSS-Nutzung: ca. 579,0 GiB bzw. 0,565 TiB
- Summe der bisherigen per-Task-RSS-Spitzen: ca. 1.438,8 GiB; diese Peaks traten nicht zwingend gleichzeitig auf.
- GPUs: 0 reserviert und 0 genutzt; alle laufenden Jobs zeigen keine GPU-GRES-Zuweisung.

### Aufteilung nach Jobfamilie

| Jobfamilie | Laufende Tasks | reservierte CPUs | gemessene CPU-Kerne | reservierter RAM | aktuelle RSS |
|---|---:|---:|---:|---:|---:|
| `flye_all` | 6 | 384 | ca. 20,6 | 1.320 GiB | ca. 267,8 GiB |
| `flye_relaxed` | 100 | 800 | ca. 521,6 | 900 GiB | ca. 267,2 GiB |
| `revcomp_main` | 4 | 64 | ca. 63,0 | 128 GiB | ca. 43,9 GiB |
| `flye_excel` | 1 | 2 | ca. 0,006 | 4 GiB | ca. 0,03 GiB |

### Speicher

- Gesamter Projektordner: 807.499.212.288 Byte, entsprechend ca. 807,5 GB bzw. 752,0 GiB
- `cluster2_flye_work`: ca. 550,7 GB bzw. 512,9 GiB
- `cluster2_flye_work/flye_all`: ca. 1,028 GB
- Eigener `reversed_komplement/main_run`: zum Snapshot 47.104 Byte; die vier PAF-Ausgaben waren noch in der Initialphase.
- Kurzfristiges Wachstum des gesamten Projektordners: ca. 0,325 GB pro Stunde, hochgerechnet aus 8.029.696 zusätzlichen Byte in 89 Sekunden.
- Im gleichen kurzen Fenster wuchs `cluster2_flye_work` nur um ca. 5,1 MB/h und `flye_all` um ca. 2,0 MB/h; kurzfristige Dateipufferung und blockweise Allokation machen diese Einzelraten schwankungsanfällig.

### Einordnung und Abweichungen

- Seit dem Start des Reverse-Komplement-Hauptruns wurde durch einen anderen Agenten zusätzlich das Array `flye_relaxed` (`2063866`) gestartet. Es stellt mit 100 gleichzeitig laufenden Tasks den größten aktuellen CPU-Anteil.
- Pending-Jobs und zusammengefasste Pending-Arrayzeilen verbrauchen aktuell keine CPUs, GPUs oder RAM und sind deshalb nicht in den Nutzungssummen enthalten.
- Die gemessenen CPU-Kerne wurden aus kumulierter `AveCPU` geteilt durch aktuelle Walltime berechnet. Bei sehr jungen oder phasenweise I/O-lastigen Tasks ist dieser Wert eine Momentaufnahme, keine garantierte Dauerlast.

## 7. Prüfung großer Stopkandidaten

**Bearbeitender Agent:** `Codex (/root)`

### Methode

- Nur-Lese-Prüfung von Queue, `sacct`-Status, SLURM-Skripten, Outputzahlen, Statusdateien und Flye-Fehlerlogs.
- Es wurden keine Jobs gestoppt, verändert oder neu eingereicht.

### Sofortiger Stopkandidat `flye_all` – Job `2056780`

- Aktuell 6 laufende Tasks mit zusammen 384 CPUs und 1.320 GiB reserviertem RAM; weitere Array-Tasks bis Insert 1.588 stehen aus.
- Der Run verwendet `split_reconstructed/backbone_only.fasta` zusammen mit den Insertreads. Diese Backbone-Datei enthält globale Backbone-Reads aus verschiedenen Plasmidkonfigurationen und ist nicht insert-spezifisch.
- Das methodische Problem wurde bereits an den fragmentierten Assemblies diagnostiziert: Die Ergebnisse bilden keine verlässliche einzelne Backbone-Insert-Konfiguration.
- Nach dem aktuellen `sacct`-Stand existieren 21 abgeschlossene, 5 fehlgeschlagene und 6 laufende Tasks; der Großteil des Arrays ist weiterhin pending.
- Empfehlung: gesamten Job `2056780` stoppen. Bereits erzeugte Dateien bleiben dabei erhalten.

### Sofortiger Stopkandidat `flye_relaxed` – Job `2063866`

- Aktuell 100 laufende Tasks mit zusammen 800 CPUs und 900 GiB reserviertem RAM; das Array ist bis 1.588 vorgesehen.
- Aktueller Ergebnisstand: 0 abgeschlossene Assemblies, 17 fehlgeschlagene Tasks und 100 laufende Statusdateien.
- Alle fünf detailliert geprüften Fehler (`YGPM-11b02`, `YGPM-11f01`, `YGPM-23e09`, `YGPM-30m05`, `YGPM-3g11`) endeten mit `Looks like the system ran out of memory` und `SIGKILL`, da je Task nur 9 GiB reserviert sind.
- Die geschätzte Coverage lag in diesen Beispielen bei etwa 16.935× bis 55.249×. Die Konfiguration verarbeitet ohne `--asm-coverage`-Begrenzung alle Reads und erzeugt dadurch sehr hohe Speicherlast.
- Zusätzlich bleibt das methodische Grundproblem bestehen: Eine einzelne künstliche Backbone-Sequenz plus Insertreads ohne echte Backbone-Insert-Junction garantiert keine zusammenhängende plasmidspezifische Assembly. Eine reine RAM-Erhöhung behebt dieses biologische Verknüpfungsproblem nicht.
- Empfehlung: Job `2063866` sofort stoppen und vor einem Neustart Inputselektion und Junction-Konzept neu entwerfen.

### Weitere bereinigbare Jobs

- `flye_excel` Job `2057067`: 2 CPUs und 4 GiB RAM; überwacht den alten Flye-Workflow. Nach Stop von `2056780` wird der Monitor nicht mehr benötigt und kann ebenfalls beendet werden.
- `mainfullfinal` Job `2053244`: dauerhaft `PENDING (DependencyNeverSatisfied)` nach abgebrochenem Mapping-Array. Kann zur Queue-Bereinigung entfernt werden, spart aktuell aber keine Ressourcen.
- `revcomp_main` Job `2063861` und Finalizer `2063865` werden weiterhin benötigt und sollten laufen bleiben.
- Der `cluster4_version2`-Mappingjob `2063968` war zum Prüfzeitpunkt bereits mit 202 Tasks abgeschlossen und verbrauchte keine laufenden Ressourcen mehr.

### Mögliche unmittelbare Einsparung

- Stop von `2056780` und `2063866`: 1.184 reservierte CPUs und 2.220 GiB RAM.
- Zusätzlicher Stop des Monitors `2057067`: Gesamteinsparung 1.186 CPUs und 2.224 GiB RAM, entsprechend etwa 2,172 TiB reserviertem RAM.
- Nach dem vorherigen Telemetriesnapshot entsprachen die beiden großen Arrays zusammen etwa 542 tatsächlich genutzten CPU-Kernen und ca. 535 GiB aktueller RSS. Die reservierte Einsparung ist größer, weil beide Workflows Ressourcen nur teilweise auslasten.

## 8. Stop des alten `flye_all`-Arrays

**Bearbeitender Agent:** `Codex (/root)`

### Methode und Input

- Auf ausdrückliche Nutzeranweisung wurde ausschließlich SLURM-Job `2056780` mit `scancel 2056780` gestoppt.
- Vor dem Stop wurden Jobname `flye_all`, sechs laufende Tasks, eine zusammengefasste Pending-Arrayzeile und 21 vorhandene `assembly.fasta`-Dateien bestätigt.
- Es wurden keine Dateien oder Outputverzeichnisse gelöscht.

### Ergebnis

- Finale Queueprüfung: 0 laufende, 0 completing und 0 pending Tasks von Job `2056780`.
- Finaler `sacct`-Stand: 21 `COMPLETED`, 5 `FAILED` und 7 `CANCELLED` Job-/Arrayeinträge.
- Die 21 bereits vorhandenen Assemblies unter `/work/project/becstr_013/cluster2_flye_work/flye_all/` sind weiterhin vorhanden.
- Unmittelbar freigegebene Reservierung gegenüber dem Zustand vor `scancel`: 384 CPUs und 1.320 GiB RAM.
- `flye_relaxed` (`2063866`), `flye_excel` (`2057067`), der Reverse-Komplement-Hauptrun (`2063861`) und dessen Finalizer (`2063865`) wurden nicht verändert.
- Das für den Clusterzugang verwendete Passwort wurde weder in Skripten noch im Protokoll gespeichert.

## 9. Aktueller Stand der neuen Hauptläufe

**Bearbeitender Agent:** `Codex (/root)`

### Reverse-Komplement-Full-Run

- Zeitpunkt der Nur-Lese-Abfrage: 25.07.2026, 10:58–10:59 Uhr CEST.
- Mapping-Array `2063861`: alle vier Tasks seit 1:05:27 Stunden `RUNNING`, je 16 CPUs und 32 GiB RAM auf `slim09`.
- CPU-Telemetrie: pro Task etwa 17:26 CPU-Stunden nach 1:05 Walltime, entsprechend nahezu vollständiger Nutzung der jeweils 16 reservierten CPUs.
- RAM: aktuelle RSS je Task etwa 27,5–28,7 GiB; bisherige MaxRSS etwa 28,8–29,5 GiB. Die 32-GiB-Grenze wurde nicht überschritten, der Abstand ist jedoch relativ knapp.
- Jeder Chunk hat einen abgeschlossenen Minimap2-Batch mit 35.185, 35.295, 35.277 beziehungsweise 35.237 protokollierten Sequenzen. Zusammen sind damit mindestens 140.994 Reads bzw. 9,4 % des Gesamtdatensatzes als abgeschlossene Batches bestätigt.
- Die vier jeweils nächsten Batches laufen bereits; die 9,4 % sind deshalb eine konservative bestätigte Untergrenze und kein exakter Echtzeitfortschritt.
- Aktuelle temporäre PAF-Größe: viermal 8.388.608 Byte, zusammen 33.554.432 Byte.
- Keine Fehlermeldung und kein abgebrochener Task. Finalizer `2063865` wartet korrekt mit `PENDING (Dependency)`.

### `cluster4_version2`-Einzellauf

- Mapping-Array `2063968`: alle 202 Tasks `COMPLETED`, Exit-Code `0:0`.
- Vorhandene Einzeloutputs: 202 Ergebnisordner, 202 `direction_summary.tsv`, 202 `insert_direction_results.xlsx` und 202 `checksums.sha256`.
- Gesamtgröße von `cluster4_version2`: 85.974.016 Byte.
- Finalizer `2063969`: `FAILED`, Exit-Code `2:0`, Laufzeit 1 Sekunde.
- Ursache: Die Jobdatei ruft die nicht vorhandene Datei `aggregate_cluster4_version2.py` auf; tatsächlich vorhanden ist `cluster4_version2_aggregate.py`. Die 202 Einzelergebnisse sind davon nicht betroffen, aber die gemeinsame Summary wurde nicht erzeugt.
- In dieser Statusprüfung wurde der Finalizer nicht korrigiert oder neu gestartet.

### Separater neuer `flye_relaxed`-Run

- Job `2063866`: 11 `COMPLETED`, 18 `FAILED`, 100 `RUNNING`; der Rest des 1.588er-Arrays steht aus.
- Vorhandene Assemblies: 11.
- Der Run bleibt getrennt von den beiden Mapping-Hauptläufen und verbraucht weiterhin bis zu 800 CPUs und 900 GiB reservierten RAM.
- Die frühere Stopempfehlung wegen OOM-Fehlern, hoher Coverage und fehlender echter Backbone-Insert-Junction bleibt bestehen.

## 10. Regelmäßige Zwischenstände des Reverse-Komplement-Hauptruns

**Bearbeitender Agent:** `Codex (/root)`

### Methode

- Vor Beginn wurden `day4.md`, der lokale Dateiänderungsstand, die laufenden SLURM-Jobs und die wachsenden PAF-Dateien erneut geprüft.
- Mit `day4/main_revcomp_interim_snapshot.py` wird pro Chunk zunächst die aktuelle PAF-Dateigröße fixiert. Es werden nur vollständige Zeilen bis zu dieser Grenze gelesen; zusätzlich wird die letzte Read-Gruppe jedes Chunks verworfen, weil zu ihr noch weitere, nicht gepufferte Alignments folgen könnten.
- Die Auswahlregel ist identisch zum Hauptrun: Ein Ziel muss Backbone und Insert unterstützen; pro Read wird nur der nach `aligned_matches`, `aligned_block_bases` und `max_mapq` eindeutig beste Treffer gezählt. Exakte Gleichstände werden ausgeschlossen.
- Die Snapshot-Auswertung läuft ausschließlich auf Compute-Nodes. Der SLURM-Job `2065410` erzeugte den ersten erfolgreichen Snapshot. Eine selbst nachplanende Kette erstellt stündlich einen neuen Snapshot, solange `interim/recurring.enabled` vorhanden und der finale `DONE`-Marker des Hauptruns noch nicht geschrieben ist. Der nächste Job ist `2065415` mit Status `PENDING (BeginTime)`.

### Entdeckter Speicherfehler und technische Korrektur

- Der erste Snapshot-Versuch `2065378` machte sichtbar, dass der ursprüngliche Chunk-2-Task `2063864` nach 1:41:31 Stunden mit Exit-Code `9:0` und `Exceeded step memory limit` fehlgeschlagen war. MaxRSS lag bei 33.386.112 KiB bei einer Reservierung von 32 GiB.
- Der fehlgeschlagene Chunkordner wurde ohne Löschung unter `/work/project/becstr_013/reversed_komplement/main_run/failed_attempts/chunk_02.job2063864/` gesichert.
- Ausschließlich Chunk 2 wurde als Recovery-Job `2065409_2` mit 16 CPUs und 64 GiB RAM neu gestartet. Die anderen drei Chunks laufen unverändert weiter.
- Der nicht mehr erfüllbare ursprüngliche Finalizer `2063865` wurde beendet. Ersatz-Finalizer `2065492` wartet mit einer UND-Abhängigkeit auf das Ende des ursprünglichen Arrays und den erfolgreichen Recovery-Job.
- Der Snapshot-Code wurde so erweitert, dass ein fehlender oder gerade neu gestarteter PAF-Chunk transparent mit null verfügbaren Treffern im Manifest erscheint, statt den gesamten Zwischenbericht abzubrechen. Die vorherigen Skriptversionen wurden unter `main_run/scripts/history/` archiviert.

### Erster erfolgreicher Zwischenstand

- Clusterpfad: `/work/project/becstr_013/reversed_komplement/main_run/interim/snapshots/20260725T095650Z/`
- Snapshotzeit: 25.07.2026, 09:56:56 UTC beziehungsweise 11:56:56 CEST
- Validierung: `status PASS`; alle fünf gespeicherten Quelldatei-Prüfsummen wurden auf Cluster und lokal bestätigt.
- Referenz: 3.176 Targets beziehungsweise 1.588 Normal-/Reverse-Komplement-Paare; Referenz-SHA-256 unverändert `9475580d097a115d0ca4a606475084eaaae8ec0994264f1df4b4a2cd57baa00e`.
- Aus den Minimap2-Logs bestätigte verarbeitete Reads: 320.690 von 1.495.785, entsprechend 21,439579 %.
- Erfasste PAF-Daten: 78.643.200 Byte und 548.692 vollständige PAF-Zeilen. Chunk 2 war zum Snapshotzeitpunkt gerade neu gestartet und hatte noch 0 PAF-Byte.
- Eindeutig zugeordnete Reads: 259.347; davon 121.965 normal (47,0277 %) und 137.382 Reverse-Komplement (52,9723 %).
- Mehrdeutige beste Reads: 0. Die Zahlen sind ausdrücklich vorläufig und enthalten nur vollständig geschriebene Read-Gruppen.

### Lokale Dateien

- Lokaler Snapshotordner: `day4/outputs/revcomp_main_interim_20260725T095650Z/`
- Interaktiver Graph: `revcomp_direction_graph.html`, 144.014 Byte, SHA-256 `b1e36ec0c218b87947999e6927d62fdfe870f062efdf4f06b18b30b0bcda01a2`.
- Roh- und Auditdaten: `direction_summary.tsv`, `counts_by_target.tsv`, `run_summary.tsv`, `snapshot_manifest.tsv`, `validation.txt` und `checksums.sha256`.
- Der Graph zeigt die Gesamtverteilung sowie wahlweise die 10, 20, 30 oder 50 Inserts mit den meisten gerichteten Reads.

### Offener Excel-Blocker

- Vor diesem Arbeitsschritt existierten lokal weder ein Graph noch eine Excel-Datei für diesen Reverse-Komplement-Hauptrun.
- Die vorgeschriebene Spreadsheet-Laufzeit war in dieser Sitzung nicht verfügbar: Der Dependency-Loader fehlt und `@oai/artifact-tool` konnte nicht geladen werden. Nach den geltenden Spreadsheet-Regeln wurde deshalb keine Ersatzbibliothek verwendet und keine nicht verifizierbare `.xlsx` erzeugt.
- Die vollständige Excel-taugliche Primärtabelle liegt bis zur Verfügbarkeit der vorgeschriebenen Laufzeit als `direction_summary.tsv` lokal vor.
- Eine visuelle Browserprüfung des HTML-Graphs konnte nicht ausgeführt werden, weil in dieser Sitzung kein Browser verbunden war. Dateistruktur, eingebettete 1.588 Datensätze, Interaktionshandler, Quelldatensummen und Prüfsummen wurden stattdessen programmgesteuert geprüft.

## 11. Plotly-Verteilungsdiagramm für den Main-Run-Zwischenstand

**Bearbeitender Agent:** `Codex (/root)`

### Methode und Input

- Vor Beginn wurden `day4.md`, der lokale Änderungsstand und die vorhandene Vorlage `normal_reverse_distribution_plotly_offline.html` einschließlich ihres Erzeugungsskripts `create_plotly_distribution.py` geprüft.
- Das neue Skript `day4/create_revcomp_plotly_distribution.py` übernimmt den Diagrammtyp der Vorlage: zwei komplementäre Linien für Normal und Reverse-Komplement, sortiert nach absteigendem Reverse-Komplement-Anteil.
- Input: `day4/outputs/revcomp_main_interim_20260725T095650Z/direction_summary.tsv` und `run_summary.tsv`.
- Hover-Informationen: Rang, Insert-ID, Normal-Reads, Reverse-Komplement-Reads und gerichtete Reads.
- Das Diagramm enthält Plotly vollständig eingebettet, funktioniert ohne Internetverbindung, unterstützt Zoom und kann über die Plotly-Leiste als PNG exportiert werden.

### Output und Validierung

- Output: `day4/outputs/revcomp_main_interim_20260725T095650Z/normal_reverse_distribution_plotly_offline.html`
- Dateigröße: 4.985.480 Byte
- SHA-256: `87791ee20945f31350cfe298a6571ef907d61750365894fa4a268ef0ba4fe944`
- Datensätze: exakt 1.588 eindeutige Inserts; die Richtungssummen wurden vor dem Export gegen 259.347 eindeutig gerichtete Reads aus `run_summary.tsv` abgeglichen.
- Technische Prüfung: eingebettete Plotly-Laufzeit vorhanden, `Plotly.newPlot` vorhanden, beide Traces vorhanden und keine externe CDN-Skriptquelle.
- Die bestehende Vorlage im Projektwurzelordner wurde nicht überschrieben.

## 12. Live-Fortschritt des Reverse-Komplement-Hauptruns

**Bearbeitender Agent:** `Codex (/root)`

- Zeitpunkt der Nur-Lese-Abfrage: 25.07.2026, 12:18:39 Uhr CEST.
- Methode: vollständige, von Minimap2 in den vier aktuellen Chunk-Logs bestätigte Batchzahlen wurden summiert und durch die 1.495.785 Quellreads geteilt.
- Bestätigt verarbeitet: 426.429 Reads, entsprechend 28,508709 %.
- Chunkstände: Chunk 0 = 142.022 Reads, Chunk 1 = 142.242 Reads, Chunk 2 Recovery = noch kein vollständig protokollierter Batch, Chunk 3 = 142.165 Reads.
- Alle drei ursprünglichen überlebenden Tasks und Recovery-Task `2065409_2` laufen. Ersatz-Finalizer `2065492` wartet korrekt auf die Abhängigkeiten.
- Die 28,51 % sind eine konservative Untergrenze; aktuell laufende, noch nicht abgeschlossene Minimap2-Batches sind darin nicht enthalten.

## 13. Reproduzierbares Workflow-Audit-Paket

**Bearbeitender Agent:** `Codex (/root)`

### Methode und Umfang

- Vor Beginn wurden `day4.md`, alle lokalen Day-4-Skripte, der aktuelle Clusterstand und die vorhandenen Remote-Dateien erneut inventarisiert.
- Mit `day4/collect_revcomp_workflow_audit.sh` wurde auf dem Cluster ein atomarer Evidenzsnapshot unter `/work/project/becstr_013/reversed_komplement/main_run/audit/workflow_audit_20260725T102500Z/` erzeugt.
- Heruntergeladen wurden die tatsächlich verwendeten Python- und SLURM-Skripte, frühere Skriptversionen, Softwareversionen, Inputmanifest, SLURM-Jobdefinitionen und -Telemetrie, Runmetadaten, Bibliotheksvalidierung, Snapshotdaten, Statusdateien sowie Erfolgs- und Fehlerlogs.
- Große FASTQ-, PAF- und Referenzdateien wurden nicht dupliziert. Sie sind mit Rolle, absolutem Clusterpfad, Dateigröße und vorhandener validierter SHA-256-Prüfsumme im Inputmanifest referenziert.
- Der Remote-Snapshot enthält 76 Dateien. Alle 75 Nutzdateien sind durch die oberste `checksums.sha256` abgedeckt; die lokale Kontrolle nach dem Download ergab 0 fehlende oder abweichende Dateien.

### Dokumentation

- Lokaler Paketordner: `day4/workflow_audit/revcomp_main_20260725T102500Z/`
- `WORKFLOW.md`: vollständiger Datenfluss, exakte Kommandos, Koordinatenlogik, Score- und Tie-Regel, Outputs, Snapshots, Finalisierung und Audit.
- `workflow_settings.tsv`: maschinenlesbare Liste aller wesentlichen Inputs, Pfade, Versionen, Parameter, Ressourcen und Regeln.
- `DECISION_RATIONALE.md`: fachliche und technische Entscheidungen mit Begründung und verworfenen Alternativen.
- `DATA_DICTIONARY.md`: Bedeutung aller PAF-Felder und erzeugten Tabellen-/Statusspalten.
- `REPRODUCTION.md`: sichere Reproduktions- und Validierungskommandos.
- `WORKFLOW_STATE.md`: Jobzustand, Fortschritt, OOM-Fehler und Recoverychronik zum Capture.
- `local_evidence/`: lokale Skripte, historische Tagesprotokolle, Snapshotdaten und Offline-Diagramme.
- `remote_evidence/`: unveränderter heruntergeladener Cluster-Evidenzsnapshot.

### Zustand zum Capture

- Capturezeit: 25.07.2026, 12:25:27 Uhr CEST.
- Bestätigt verarbeitete Reads: 461.706 von 1.495.785, entsprechend 30,867137 %.
- Drei ursprüngliche Mappingtasks und der mit 64 GiB neu gestartete Chunk-2-Recovery-Task liefen.
- Ersatz-Finalizer `2065492` und der nächste stündliche Snapshot `2065415` warteten korrekt.

### Reasoning- und Sicherheitsgrenze

- Das Paket enthält überprüfbare Entscheidungsbegründungen und Evidenz für jede Workfloweinstellung, jedoch keine privaten internen Gedankengänge oder verborgenen Chain-of-Thought-Protokolle.
- Es wurden keine Passwörter, privaten Schlüssel oder Cluster-Credentials in Skripten, Dokumentation oder Evidenzdateien gespeichert.
- Das Paket wird mit `day4/build_workflow_audit_package.py` auf potenzielle Credentialmuster geprüft, vollständig manifestiert, per SHA-256 abgesichert und als ZIP getestet.

### Finale Paketvalidierung

- ZIP: `day4/workflow_audit/revcomp_main_20260725T102500Z.zip`
- ZIP-Größe: 1.798.983 Byte
- ZIP-SHA-256: `c389b83991fc40cb68c8cad90950efaf9a603cceb8844bb6ab867208ef1484be`
- Payloaddateien vor Manifest/Validierung: 103
- Dateien in der abschließenden Paket-Prüfsummenliste: 109
- Manifest, vollständige SHA-256-Kontrolle, Credentialmustertest und ZIP-CRC-Test: `PASS`.
- Vier zunächst kopierte historische Day-2/Day-3-Protokolle wurden wegen darin erkannter alter `-pw`-Kommandozeilen aus dem auszuliefernden Paket entfernt. Die Originalprotokolle im Projekt wurden nicht verändert; `agents.md` und das aktuelle `day4.md` bleiben enthalten.

## 14. Ablage des Workflow-Audits im zentralen Workflowordner

**Bearbeitender Agent:** `Codex (/root)`

- Auf Nutzeranweisung wurde das Reverse-Komplement-Audit in den neuen Unterordner `day4/workflows/reverse_complement_main_run/` verschoben.
- Neuer entpackter Pfad: `day4/workflows/reverse_complement_main_run/revcomp_main_20260725T102500Z/`
- Neuer ZIP-Pfad: `day4/workflows/reverse_complement_main_run/revcomp_main_20260725T102500Z.zip`
- ZIP-Prüfsumme: `day4/workflows/reverse_complement_main_run/revcomp_main_20260725T102500Z.zip.sha256`
- Die bisherigen Audit-Originale unter `day4/workflow_audit/` wurden an den neuen Ort verschoben, nicht dupliziert. Die separat ausgeschlossenen historischen Protokollkopien wurden nicht in den Zielordner aufgenommen.
- Nach dem Verschieben wurden alle 109 Payload-Prüfsummen erneut kontrolliert: 0 fehlende und 0 abweichende Dateien.
- ZIP-Größe und SHA-256 blieben unverändert: 1.798.983 Byte und `c389b83991fc40cb68c8cad90950efaf9a603cceb8844bb6ab867208ef1484be`.
