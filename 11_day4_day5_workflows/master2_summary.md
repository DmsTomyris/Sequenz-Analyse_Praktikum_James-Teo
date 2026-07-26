# master2 – Arbeitszusammenfassung und aktueller Clusterstatus

Stand: 24.07.2026, 18:50 Uhr (Europe/Berlin)

## Auftrag und Projektziel

Aus 1.588 Hefe-Insert-Sequenzen und einem konstanten Backbone wurde eine künstliche Referenzbibliothek mit 3.176 Sequenzen vorbereitet: je Insert eine normale und eine Reverse-Variante. Die Reverse-Variante enthält das Insert in umgekehrter Basenreihenfolge, nicht reverse-komplementiert. Die Insert-Position liegt zwischen Backbone-Base 5042 und 5043; die Target-IDs der Reverse-Varianten enden mit `-rev`.

## Durchgeführte Arbeiten

### Daten und Referenzen

- Cluster-Workspace geprüft und die Cluster-README bzw. die lokalen HPC-Dokumente verwendet.
- FASTQ-Datensatz vollständig entpackt und verarbeitet.
- Originaldatensatz: 1.495.785 Nanopore-Reads und 21.409.671.313 Basen.
- Referenzen verwendet: Hefegenom, pGP564-Backbone und die künstliche 3.176-Target-Bibliothek.
- Dateitransfers und lokale Kopien wurden getrennt gehalten; am Cluster wurden keine vorhandenen Ergebnisse überschrieben.

### Historische Mapping- und Kontrollläufe

- Minimap2-Mappings mit `map-ont` und `sr` gegen Hefegenom und Backbone ausgeführt bzw. dokumentiert.
- Adaptertrimming mit Cutadapt/SPLAT in mehreren Läufen geprüft; wiederholtes Trimming verbesserte die Trefferzahlen nicht wesentlich.
- BLAST-Kontrollen der Minimap-unmapped Reads durchgeführt; keine überzeugenden zusätzlichen starken Treffer.
- Identitätsschwellen und Cross-Species-Kontrollen dokumentiert.
- Positivkontrolle mit echtem Hefe-FASTQ: 97.561 von 100.000 Reads primär gegen das Hefegenom gemappt.

### Junction-spezifische Hauptworkflows

Auf Nutzerwunsch wurde die Mappingregel verschärft: Ein Read wird nur gezählt, wenn für dasselbe künstliche Target mindestens ein Alignment den Insertbereich und mindestens ein Alignment einen Backbonebereich abdeckt. Ein exakter Übergang an 5042/5043 ist nicht zwingend; reine Backbone- oder reine Insert-Reads werden nicht gezählt. Supplementary Alignments werden gemeinsam ausgewertet.

- **Getrimmt:** 1.000er-Pakete, bereits getrimmte Pakete werden einzeln durch einen separaten Junction-Worker analysiert.
- **Ungetrimmt:** vollständiger FASTQ in 1.496 Rohpakete geteilt; jedes Paket wird einzeln gemappt und mit eigenem Ergebnis abgeschlossen.
- Pro Paket werden `mapping.paf`, `best_hits.tsv`, `counts.tsv` und ein `DONE`-Marker erzeugt.
- Die Counts werden nach Normal- und Reverse-Target getrennt und als absolute Reads sowie Prozentanteile ausgewertet.
- Beste Zielzuordnung erfolgt nach qualifizierender Alignment-Basenmenge, MAPQ und Target-ID.

### Auswertungen und lokale Dateien

- `current_counts_trimmed.tsv`: aktueller Zwischenstand getrimmt.
- `current_counts_untrimmed.tsv`: aktueller Zwischenstand ungetrimmt.
- `junction_counts_getrimmt_ungetrimmt.xlsx`: lokale Excel-Datei mit den Sheets `getrimmt` und `ungetrimmt`; sie entspricht dem damaligen Zwischenstand und aktualisiert sich nicht automatisch.
- `normal_reverse_distribution_plotly.html`: interaktives Plotly-Diagramm mit zwei Panels und Tooltips pro Insert.
- `normal_reverse_distribution_plotly_offline.html`: vollständig offlinefähige Plotly-Version.
- `create_plotly_distribution.py`: reproduzierbares Plotly-Script.
- `day2.5.md`: fortlaufendes Arbeitsprotokoll ab Tag 2.5.

Die Plotly- und Excel-Auswertungen basieren auf Zwischenständen, solange noch Paketjobs laufen.

## Aktuell laufende bzw. überwachte Clusterjobs

Live-Abfrage zuletzt um 18:50 Uhr:

| Job | Zweck | Status | Ressourcen |
|---|---|---|---|
| `2054868` | getrimmter Junction-Worker | RUNNING | 64 CPUs, 64 GiB, `slim06` |
| `2055131_0` | ungetrimmtes Junction-Array, Teil 1 | RUNNING | 64 CPUs, 32 GiB, `slim08` |
| `2055131_1` | ungetrimmtes Junction-Array, Teil 2 | RUNNING | 64 CPUs, 32 GiB, `slim11` |
| `2056780_1`, `_16`, `_17`, `_18`, `_19` | separater Flye/Rebuild-Workflow | RUNNING | jeweils 64 CPUs, 220 GiB |
| `2057067` | Flye-Excel-/Nachlauf | RUNNING | 2 CPUs, 4 GiB |
| `2056780_[20-1588%1]` | weiterer Flye-Arrayteil | PENDING | wartet auf Ressourcen |

`2053244` ist ein alter Finalizer mit `DependencyNeverSatisfied` und wird nicht mehr sinnvoll fortgesetzt. Er gehört nicht zum aktiven Junction-Workflow.

Es läuft keine dauerhafte Hintergrundüberwachung durch diesen Agenten; der Status wird bei einer erneuten Abfrage live mit `squeue`, `sinfo` und `scontrol` geprüft.

## Aktuelle Clusterressourcen

Bei der letzten Abfrage waren ungefähr 1.206 CPUs und 4.959 GiB scheduler-zuteilbarer RAM frei. Partitionen:

- `slim16`: ca. 848 CPUs und 3.410 GiB
- `slim18`: ca. 252 CPUs und 837 GiB
- `fat`: ca. 66 CPUs und 712 GiB
- `gpu`: ca. 40 CPUs, aber nur etwa 0,4 GiB scheduler-freier RAM

## Noch offene Aufgaben

1. Die beiden Junction-Paketworkflows bis zum Abschluss aller 1.496 Pakete laufen lassen.
2. Nach Abschluss je Workflow alle `counts.tsv` zu einer vollständigen Tabelle zusammenführen.
3. Finale Excel-Datei mit getrennten Sheets für getrimmt und ungetrimmt erzeugen.
4. Finales Plotly-Diagramm aus den vollständigen Tabellen neu erzeugen.
5. Paketanzahl, Read-Summen, Normal-/Reverse-Verteilung und Jobparameter in `day2.5.md` dokumentieren.
6. Separate Flye-/Rebuild-Ergebnisse nur dann mit dem Junction-Ergebnis verbinden, wenn die Referenz- und Workflowzuordnung geprüft ist.

## Reproduzierbarkeit und Sicherheitsstatus

- Jeder Workflow verwendet eigene Outputverzeichnisse.
- Clusterdateien wurden bei den letzten Status- und Auswertungsschritten nicht verändert oder gelöscht.
- Jobparameter, Zwischenstände und technische Korrekturen werden in `day2.5.md` fortgeschrieben.
- Das SSH-Passwort ist nicht Bestandteil dieser Zusammenfassungsdatei.
