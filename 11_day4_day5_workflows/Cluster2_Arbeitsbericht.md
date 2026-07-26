# Cluster2 – ausführlicher Arbeitsbericht

**Projekt:** AAAA-Praktikum – Aufteilung künstlicher Insert-/Chromosom-Reads und Flye-Assemblies  
**Arbeitsname:** Cluster2  
**Stand:** 24.07.2026  
**Hauptprotokoll:** [day3.md](day3.md)

## 1. Auftrag

Aufgabe war, den großen Nanopore-Datensatz auf 1.588 künstliche Insertsequenzen und das gemeinsame pGP564-Backbone aufzuteilen. Für jedes Insert sollte eine eigene FASTA-Datei mit zugehörigen Reads entstehen. Zusätzlich sollten Reads erfasst werden, die ausschließlich auf das Backbone mappen und keinen qualifizierenden Insert-Treffer besitzen.

Danach sollte Flye zunächst für ein Insert getestet und anschließend für möglichst viele Inserts parallel gestartet werden. Die erwartete Plasmidlänge sollte individuell über Flye berücksichtigt werden. Fertige Assemblies sollten einzeln lokal gespeichert werden.

## 2. Einrichtung und Daten

- Die entpackte Read-Quelle unter /work/project/becstr_013/unpacked_20230920_DNA_Korber_Drin3plex/ wurde unverändert in den eigenen Clusterbereich /work/project/becstr_013/cluster2_flye_work/ kopiert.
- Die Kopie umfasste ungefähr 22 GB.
- Unter cluster2_flye_work/references/ wurden combined_1589.fa und die Insertreferenz abgelegt.
- Unter /work/project/becstr_013/miniforge3/ wurde eine eigene Umgebung eingerichtet.
- Installiert und geprüft wurden Flye 2.9.5-b1801, Minimap2 2.31, Samtools 1.24, Python 3.11 und OpenPyXL.
- Ein minimaler Flye-Test wurde erfolgreich durchgeführt.

## 3. Read-Mapping und Partitionierung

Für den vollständigen Split wurde gegen 1.589 Referenzen gemappt, mit:

    minimap2 -ax map-ont --secondary=yes -N 5000 -p 0.0

Qualifizierende Treffer benötigten mindestens 50 bp ausgerichtete Query und mindestens 70 Prozent Identität. Die Mappingausgabe wurde queryname-sortiert als BAM gespeichert.

Der zentrale intakte Zwischenstand war:

    /work/project/becstr_013/cluster2_flye_work/split_full/queryname.bam

Die erste FASTA-Partitionierung erzeugte zwar Insert- und Backbone-Dateien, später waren jedoch mehrere FASTAs technisch beschädigt und nur 2 Bytes groß. Deshalb wurde nicht mit diesen beschädigten Dateien weitergearbeitet.

Der intakte 27-GB-BAM wurde mit partition_reads.py neu partitioniert. Dabei entstanden:

- 1.585 nichtleere Insert-FASTAs
- drei Inserts ohne zugehörige Reads
- 36.507 globale Backbone-only-Reads
- 1.286.697 eindeutig zugewiesene Reads
- 14.560.182 Insert-Zuweisungen inklusive Mehrfachzuweisungen
- ungefähr 231 GB rekonstruierte Splitdaten

Die drei readlosen Inserts werden nicht mit leerem Input an Flye übergeben, sondern als SKIPPED_NO_READS dokumentiert.

## 4. Flye-Array

Für jedes Insert wird die erwartete Zielgröße berechnet als:

    erwartete Plasmidlänge = 7371 bp Backbone + Insertlänge

Diese Größe wird als genome-size an Flye übergeben. Sie dient der Parameterwahl und erzwingt weder eine bestimmte Assemblylänge noch einen einzelnen Contig.

Das Array verwendet:

    --nano-raw
    --genome-size <insert-spezifische Größe>
    --threads 64
    --mem 220G
    --array=1-1588%10

Der aktuelle korrigierte Array-Job ist 2056780. Maximal zehn Tasks laufen parallel; weitere Tasks warten auf freie Clusterressourcen.

Mehrere technische Fehler wurden korrigiert: falsche Python-Pfade, zu strenge Prüfung auf 1.588 nichtleere Dateien, fehlendes python3 im Batch-PATH und eine Prüfung des Outputverzeichnisses nach dessen eigener Erstellung.

## 5. Einzeltest YGPM-27o02

Für YGPM-27o02 wurden ungefähr 1.000 Insertreads zusammen mit der globalen Backbone-only-Datei an Flye übergeben. Die Insertreferenz selbst war kein Input.

Das Ergebnis umfasste 8 Contigs, zusammen 115.201 bp, N50 31.333 bp, größtes Fragment 31.574 bp und mittlere Coverage ungefähr 293×. Die erwartete Plasmidlänge betrug ungefähr 18.935 bp. Das Ergebnis war deshalb keine einzelne korrekte Plasmidassembly.

Die fertige Datei liegt lokal unter:

    day3/cluster2_flye/YGPM-27o02_assembly/assembly.fasta

## 6. Methodische Einschränkung der globalen Backbone-only-Reads

Die globale Backbone-only-Datei enthält Backbone-Reads aus vielen verschiedenen Plasmidkonfigurationen. Ein solcher Read zeigt zwar, dass er zum gemeinsamen Backbone passt, aber nicht, zu welchem Insert er gehört.

Für eine eindeutige Zielassembly müsste der Graph den Weg

    Backbone → Zielinsert → Backbone

durch passende Junction-Reads unterstützen. Globale Backbone-only-Reads enthalten diese Zielübergänge nicht. Zusammen mit einem Insert können sie daher mehrere mögliche Graphpfade erzeugen. Das führt zu Verzweigungen, alternativen Contigs und fehlender eindeutiger Circularität.

Die globalen Backbone-only-Reads verhindern Circularität nicht grundsätzlich, sind aber für die Zuordnung zu einem bestimmten Insert mehrdeutig. Für eine belastbare Einzelplasmidassembly sollten Zielinsertreads, Junction-Reads und eindeutig derselben Konfiguration zuordenbare Backbone-Reads verwendet werden.

## 7. Automatische Ergebnisverwaltung

Ein Excel-Monitor wurde eingerichtet und soll die Flye-Statistik fortlaufend unter folgendem Clusterpfad aktualisieren:

    /work/project/becstr_013/cluster2_flye_work/flye_all_progress.xlsx

Zusätzlich wurde ein lokaler Downloader eingerichtet. Jede fertige Assembly wird separat abgelegt unter:

    day3/cluster2_flye/flye_assemblies/<Insert-ID>/

Pro Insert werden assembly.fasta, assembly_info.txt und run_metadata.tsv übertragen, sofern vorhanden. Zum kontrollierten Stand waren bereits YGPM-22c24, YGPM-24d14 und YGPM-14k08 lokal vorhanden.

Der Downloader liegt unter:

    day3/cluster2_flye/download_completed_flye.ps1

## 8. Graphprüfung YGPM-14k08

Für YGPM-14k08 beträgt die erwartete Länge:

    7371 bp + 11152 bp = 18523 bp

Flye erzeugte 9 in assembly_info.txt aufgeführte Contigs mit zusammen 142.184 bp. Kein Contig wurde als zirkulär markiert (circ.=N). Der Graph enthält verzweigte Pfade, darunter eine gemeinsame Anfangsroute für contig_3 und contig_4 sowie getrennte Pfade für contig_21 und contig_22. Ein geschlossener Pfad zum Ausgangsknoten ist nicht erkennbar.

Der Graph wurde lokal gesichert unter:

    day3/cluster2_flye/flye_assemblies/YGPM-14k08/assembly_graph.gfa

Auch dieses Ergebnis ist keine einzelne zirkuläre 18,5-kb-Plasmidassembly.

## 9. Fachliche Schlussfolgerung

Die naive Flye-Serie ist technisch gestartet und erzeugt Assemblies. Die verwendete globale Backbone-only-Datei ist jedoch nicht ausreichend, um für jedes Insert eine beweiskräftige Einzelplasmidassembly zu erhalten.

Ein gutes Ergebnis für ein erwartetes 18,5–18,9-kb-Plasmid wäre ein einzelner Contig dieser Größenordnung mit gleichmäßiger Coverage, unterstützten Insert-Backbone-Junctions und einer im Graphen belegten Kreisroute. genome-size oder ein künstliches Zusammenkleben von Contigenden ersetzt diese Evidenz nicht.

## 10. Relevante Dateien

- Hauptprotokoll: day3.md
- Clusterarbeitsbereich: /work/project/becstr_013/cluster2_flye_work/
- Rekonstruktionsskript: day3/cluster2_flye/rebuild_split_from_bam.slurm
- Flye-Array: day3/cluster2_flye/flye_all_array.slurm
- Excel-Monitor: day3/cluster2_flye/monitor_flye_progress.py
- Lokaler Downloader: day3/cluster2_flye/download_completed_flye.ps1
- Lokale fertige Assemblies: day3/cluster2_flye/flye_assemblies/
- Read-Verteilung: day3/cluster2_flye/insert_read_distribution_sorted.xlsx
