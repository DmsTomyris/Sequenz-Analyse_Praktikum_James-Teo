# Kurzprotokoll Tag 4–5

Diese Zusammenfassung bündelt die großen Methoden, Meilensteine, Zwischenstände und finalen Daten aus `day4.md` und `day5.md`. Historische Zwischenstände bleiben in den vollständigen Tagesprotokollen erhalten.

## 1. Reverse-Komplement-Main-Workflow

### Referenzaufbau und Vorbereitung

- Aus `pGP564_backbone.fa` (7.371 bp) und 1.588 Inserts wurde eine Bibliothek mit 3.176 Records erzeugt: je Insert normal und Reverse-Komplement.
- Die Reverse-Komplement-Variante komplementiert tatsächlich und dreht die Insertsequenz um; der Backbone bleibt unverändert.
- Einfügestelle: zwischen Backboneposition 5042 und 5043.
- Library-Job `2062282`: `COMPLETED`, Validierung `PASS`.
- FASTA: 58.718.076 Byte; SHA-256 `9475580d097a115d0ca4a606475084eaaae8ec0994264f1df4b4a2cd57baa00e`.
- Paarweiser Referenzexport für `cluster4_version2`: Job `2062283`, 1.588 Insertordner mit je normaler und Reverse-Komplement-FASTA, vollständig validiert.

### Main-Run und Iterationen

1. Mappingarray `2063861`: vier Chunks, Minimap2 2.10-r761, `-x map-ont --secondary=no`, je 16 CPUs/32 GiB.
2. Der ursprüngliche Chunk 2 (`2063864`) überschritt mit 32 GiB die Speichergrenze und fiel mit Exit `9:0` aus.
3. Nur Chunk 2 wurde als Recovery `2065409` mit 64 GiB neu gestartet; die übrigen drei Chunks blieben unverändert.
4. Der erste Finalizer `2063865` wurde durch den erfolgreichen Ersatzfinalizer `2065492` ersetzt.
5. Mehrere Zwischen-Snapshots (`2065410`, `2065415`, `2067238`, `2068467`, `2069918`, `2069996`) wurden mit `PASS` validiert.
6. Der produktive Gesamtlauf und alle vier Chunk-Ausgaben wurden erfolgreich abgeschlossen.

### Finale Main-Ergebnisse

- Quellreads: **1.495.785**
- Reads mit mindestens einem PAF-Alignment: **1.288.094**
- Eindeutig qualifizierende Backbone-plus-Insert-Reads: **1.230.467 = 82,2623 %** aller Quellreads
- Anteil unter den PAF-Reads: **95,5262 %**
- Normal-Orientierung: **578.095 Reads = 46,9818 %** der gerichteten Reads
- Reverse-Komplement: **652.372 Reads = 53,0182 %**
- Mehrdeutige beste Reads: **0**
- Ohne PAF: **207.691**; PAF vorhanden, aber kein qualifizierendes Backbone-plus-Insert-Target: **57.627**
- Finaler Status: `PASS`; Checksummen vollständig geprüft.
- Primärdaten: `counts_by_target.tsv`, `direction_summary.tsv`, `run_summary.tsv`, `run_metadata.tsv` und `checksums.sha256`.

### Definition „eindeutig“

Ein Read/Target-Paar musste Insert und mindestens einen Backbonebereich abdecken. Die Auswahl erfolgte nach `aligned_matches`, danach Alignmentblocklänge und danach maximaler MAPQ. Exakte Score-Ties wurden als mehrdeutig ausgeschlossen. Es gab keine zusätzliche Mindestidentität oder Mindest-MAPQ im Main-Aggregator.

### Darstellung und Filterung

- Offline-Plotly-Diagramm und PNG wurden final erzeugt und visuell geprüft.
- 12 Inserts mit `normal_reads = 0` und `revcomp_reads = 0` wurden nur aus der Darstellung entfernt; die Rohdaten und die Summe 1.230.467 blieben unverändert.
- Darstellung: **1.576** Inserts mit mindestens einem gerichteten Read.

## 2. Flye-Workflows

### Früher `flye_all`-Lauf

- Job `2056780` arbeitete mit globalen Backbone-Reads aus verschiedenen Plasmidkonfigurationen und war daher methodisch nicht insert-spezifisch.
- Beim Stop: 21 fertige Assemblies, 5 fehlgeschlagene und 7 abgebrochene Arrayeinträge.
- Der Job wurde gestoppt; vorhandene 21 Assemblies und Logs blieben erhalten.

### `flye_relaxed` und 16G-Restart

- Alter Job `2063866`: zunächst 799, während des kontrollierten Stopps schließlich **801 valide fertige Assemblies**.
- Viele Fehler waren OOM-bedingt: 9 GiB RAM, hohe Coverage, `--meta`, `--min-overlap 1000` und vollständiger Backbone als Input.
- Die übrigen **787 Inserts** wurden als Restartmenge bestimmt; 801 fertige Verzeichnisse wurden behalten.
- Neuer 16G-Workflow `2070896`, Output `flye_relaxed_1588_v3`, 8 CPUs und 16 GiB pro Task, 100er Arraylimit.
- Der Restart wurde später auf maximal 10 neu startende Tasks gedrosselt; bereits laufende Tasks wurden nicht abgebrochen.
- Zwischenstand: 100 Tasks liefen, weitere warteten; **noch keine zusätzliche fertige FASTA** aus dem 16G-Restart.
- Methodische Kernaussage: Mehr RAM behebt nicht das Grundproblem, dass ein vollständiger künstlicher Backbone ohne echte Backbone-Insert-Junction keine verlässliche plasmidspezifische Assembly garantiert.

### Flye-Assemblies für Cluster4

- 801 fertige Flye-Assemblies wurden gegen den bestehenden Cluster4-Satz von 202 IDs abgeglichen.
- 112 IDs überlappten; deshalb wurden **689 neue IDs** gemappt.
- Zusammen: **891 eindeutige IDs**.
- Cluster4-Array `2071026`, alle 689 Tasks erfolgreich; Finalizer `2071718` erfolgreich.
- Vergleich mit dem Main-Run:
  - `all_alignments`: 232/397 = **58,44 %** Übereinstimmung.
  - `MAPQ_ge_20`: 312/468 = **66,67 %**.
  - Alte 202 IDs: 69,57 % bzw. 88,57 %.
  - Neue 689 Flye-IDs: 56,98 % bzw. 62,81 %.
- Die Werte messen Übereinstimmung mit dem Readcount-basierten Main-Run, nicht automatisch biologische Wahrheit.

## 3. Raven-Workflows

### Hauptlauf und Fehlerklassifikation

- Raven-Version: **1.8.3**.
- Hauptlauf `raven_1588`: **1.483 eindeutige nichtleere Assembly-FASTAs**.
- Statusbestand des ursprünglichen Arrays: 1.084 `COMPLETED`, 500 `FAILED`; alte `RUNNING`-Marker waren nicht aktuell.
- Fehler: 475× Exit 1, 24× Exit 137/SIGKILL, 1× Exit 139/Segmentation Fault.
- Von 500 formal fehlgeschlagenen Runs enthielten 399 bereits verwertbare FASTA+GFA-Paare; 101 hatten keinen vollständigen verwertbaren FASTA/GFA-Satz.
- Die 399 verwertbaren Ergebnisse wurden sicher als `FAULTY`-Kopie abgelegt und nicht gelöscht.

### Raven-16G-Retry

- Neustartmenge: **105 Inserts** ohne verwertbaren FASTA+GFA-Satz.
- Job `2071721`, Raven 1.8.3, vollständiger Backbone plus ein Insert, 8 CPUs/16 GiB, `--identity 0`, `--kMaxNumOverlaps 64`, `--min-unitig-size 1000`, ein Polishing-Lauf.
- Zusätzlich entstanden **27 nichtleere Retry-FASTAs**.
- Gesamtbestand: **1.510 eindeutige Raven-Assemblies** = 1.483 Hauptlauf + 27 nichtüberlappende Retry-Outputs. `FAULTY`-Kopien werden nicht doppelt gezählt.

### Raven-Cluster4-Vergleich

- 1.320 neue Raven-IDs wurden zusätzlich zu den bestehenden 202 IDs gemappt; kombinierter Satz: **1.522 IDs**.
- Array `2071864`, alle Tasks erfolgreich; Finalizer `2073202` erfolgreich.
- `all_alignments`: 399/525 = **76,00 %** Übereinstimmung mit dem Main-Run.
- `MAPQ_ge_20`: 759/842 = **90,14 %**.
- Neue Raven-IDs allein: 76,62 % bzw. 90,28 %.
- Viele Fälle blieben `ambiguous` oder `no_call`; der MAPQ-Filter verbesserte die Übereinstimmung deutlich.

## 4. Richtungsabhängige UCSC-Referenzen und Genome Hub

- Für 85-%- und 95-%-Richtungsschwellen wurden vier Assemblyvarianten gebaut: `pGP85`, `scR64pGP85`, `pGP95`, `scR64pGP95`.
- Insgesamt entstanden 3.503 validierte Buildobjekte; `hubCheck -noTracks`: ohne Fehler.
- 85-%-Satz: 1.496 Einzel- und 92 Doppel-IDs, 1.680 Plasmidchromosomen.
- 95-%-Satz: 1.429 Einzel- und 159 Doppel-IDs, 1.747 Plasmidchromosomen.
- Kompositassemblies enthalten zusätzlich 17 R64-Chromosomen und 6.600 projizierte Gene.
- Buildjob `2071846`: `COMPLETED`, `PASS`.
- Frühe Builds scheiterten an C-/ASCII-Chromosomensortierung, temporären Manifestpfaden und inkompatiblen UCSC-Binaries; diese Punkte wurden korrigiert.
- Produktives Mappingarray `2073203`: 4 Assemblies × 4 FASTQ-Chunks, `-ax map-ont --secondary=no`, 16 CPUs/48 GiB je Task.
- Finalizer `2073204` erzeugt `raw_primary`, `MAPQ20`, `junction_evidence` und BigWigs; Junctionevidenz verlangt MAPQ ≥20 und mindestens 50 ausgerichtete Basen auf beiden Seiten.
- Auditjob `2073209` prüft Header, BAM/BAI, BigBed/BigWig, Hub und Checksummen.

## 5. Weitere große gemeinsame Workflows

### Mappingexamples und Day-2-Kontrolle

- Sieben FASTQ-Examples wurden gegen pGP85, pGP95 und Hefe+Backbone gemappt: 21 unabhängige Minimap2/Samtools-Läufe.
- Ergebnisse über 4.654 Reads pro Example: pGP85 **8 = 0,171895 %**, pGP95 **8 = 0,171895 %**, Hefe+Backbone **9 = 0,193382 %**; kombiniert MAPQ ≥20: **7 = 0,150408 %**.
- Output: `day5/minimap2_mappingexamples_20260726/` mit 21 BAMs, Metriken, HTML und Excel.

### Großer historischer Day-2-Datensatz

- 324.008 Reads aus `Day2/Pipeline2/dorado_reads.fastq` wurden mit MAPQ ≥20 ausgewertet.
- pGP85: **5.454 = 1,6833 %**; pGP95: **5.289 = 1,6324 %**; Hefe+Backbone: **17.685 = 5,4582 %**.
- Die erste Auswertung über Alignmentzeilen wurde korrigiert auf eindeutige Readnamen und die tatsächliche FASTQ-Readzahl.

### Neuer LRZ-Datensatz

- Auf dem Cluster gefunden: ZIP ca. 23,19 GB, komprimierter FASTQ ca. 23,18 GB, entpackter `barcode48.fastq` ca. 43,45 GB.
- Primärer Mappingpfad: `/work/project/becstr_013/unpacked_20230920_DNA_Korber_Drin3plex/.../fastq_pass/barcode48.fastq`.
- Mappingarray `2073228`: drei Targets, Minimap2 `-ax map-ont --secondary=no`, MAPQ ≥20, 16 CPUs/64 GiB je Task.
- Outputziel: `/work/project/becstr_013/large_drin3plex_mapq20_20260726/`.

## 6. Gesamtbewertung

- Der Reverse-Komplement-Main-Workflow ist vollständig, checksum-validiert und mit 1,23 Millionen eindeutig qualifizierenden Reads der wichtigste abgeschlossene Großlauf.
- Flye lieferte 801 verwertbare Assemblies; der 16G-Restart war zum letzten Stand noch ohne zusätzliche fertige Assemblies.
- Raven lieferte 1.510 inhaltlich sichtbare Assemblies; ein Teil der formalen Fehler enthielt trotzdem verwertbare FASTA/GFA-Ausgaben und wurde separat klassifiziert.
- Cluster4 bestätigt Main-Richtungen bei Raven deutlich besser als bei Flye; MAPQ ≥20 verbessert beide Vergleiche.
- Die UCSC-Hub- und richtungsabhängigen Referenzbuilds sind erfolgreich validiert; das nachgelagerte Custom-Genome-Mapping lief als abgesicherte SLURM-Kette.
- Alle Aussagen zu Richtungen und Assemblyqualität bleiben von der verwendeten Read-/Alignmentdefinition abhängig und sind nicht automatisch biologische Beweise.
