# Day 2 – Kurzprotokoll

## Ausgangslage

- Neuer Datensatz `dorado_reads.fastq` mit 324.008 Reads.
- Referenzen: `genome.fa`, `pGP564_backbone.fa` und später `targeted_reference.fa`.
- Werkzeuge: Minimap2 2.31-r1302, Samtools 1.24, Cutadapt, Seqkit, BLAST+ und Python/Excel-Auswertung.
- Ausführung lokal unter WSL.

## 1. Mapping gegen Hefe und Backbone

- Minimap2 `-ax map-ont`, anschließend Samtools Sort, Index, Flagstat und Coverage.
- Output: `Tag1/mapping_results_dorado_run1/`.
- Hefe: 14.973 primär gemappte Reads (4,62 %); 20.713 Alignments insgesamt.
- Backbone: 7.081 primär gemappte Reads (2,19 %); 8.493 Alignments insgesamt.
- Backbone-Abdeckung: 97,79 %, mittlere Tiefe ungefähr 350×.
- Hefechromosomen: ungefähr 29–40 % Abdeckung.
- Eine fehlerhafte Wiederholung des Hefe-Mappings für den Backbone wurde verworfen und korrekt wiederholt.

## 2. Adaptertrimming

- Adapter: `ACACGACGCTCTTCCGATCT`; Mindestlänge 30 bp.
- Vier Trimming-/Mapping-Stufen wurden durchgeführt.
- Überlebende Reads: 316.647 (1×), 312.880 (2×), 312.004 (3×), 311.925 (4×).
- Hefe-Mapping blieb praktisch stabil: 14.967 → 14.918 primäre Reads.
- Backbone-Mapping blieb praktisch stabil: 7.077 → 7.056 primäre Reads.
- Fazit: Wiederholtes Trimming entfernt Reads, verbessert die absoluten Treffer aber kaum.

## 3. BLAST-Kontrolle

- Nicht gegen Hefe gemappte Reads wurden mit Samtools extrahiert; ein erster BLAST-Aufruf mit FASTQ war technisch falsch.
- Korrektur: FASTQ mit Seqkit in FASTA umwandeln; danach `blastn-short`, `word_size 11`, E-Wert `1e-5`.
- Starker Treffer: mindestens 90 % Identität, 30 bp Alignment und 80 % Query-Abdeckung.
- Hefe: 0 starke Treffer; Backbone: 840 starke Treffer.
- Alle 840 BLAST-Reads waren im separaten Backbone-Minimap2-Lauf bereits vorhanden.
- BLAST bestätigte somit vorhandene Treffer und fand keine neue Readmenge.

## 4. Cross-Species und Positivkontrolle

- `map-ont`: Mensch 9, Maus 2, Drosophila 0, Zebrafisch 2, *E. coli* 20 primäre Reads.
- Positivkontrolle: 100.000 echte *S. cerevisiae*-Reads aus SRA `SRR8455574`.
- Ergebnis: 97.561 primäre Alignments (97,56 %) und 56,88 % Referenzabdeckung.
- Schluss: FASTQ-Verarbeitung, Referenz, Minimap2 und BAM-Auswertung funktionieren grundsätzlich.

## 5. Read- und Plot-Auswertungen

- Ein 5.285-bp-Read mappt zu etwa 98,7 % auf Hefe und nicht auf den Backbone.
- Plotly-Scatterplot: Read-Länge gegen gemappten Read-Anteil; 14.973 Hefe- und 7.081 Backbone-Punkte.
- Der CIGAR-Operator `D` wurde korrekt aus der gemappten Read-Länge ausgeschlossen.
- Zusätzlich wurde ein Histogramm der gemappten Read-Längen erstellt.

## 6. Targeted Reference und Junction-Workflow

- `targeted_reference.fa`: 1 Backbone plus 1.588 Inserts.
- Unabhängige Prüfung: alle Inserts, Koordinaten, Längen und Sequenzen stimmen mit Tabelle und `genome.fa` überein; 0 Abweichungen.
- `targeted_reference.fa` und `dorado_reads.fastq` liegen jetzt in `Day2/Pipeline2/`.
- Mapping: Minimap2 `-ax map-ont --sam-hit-only`; primäre und supplementary, keine sekundären Alignments.
- Ergebnis: 525 eindeutige Reads mit Backbone- und Insert-Alignment; 596 Alignment-Paare.
- Die Excel-Tabelle enthält Read-, Referenz-, Insert-, Längen-, Gap- und MAPQ-Spalten.
- Hard-Clips und Reverse-Strand-Alignments wurden korrigiert und vollständig validiert.
- Aktuelle Ergebnisdatei: `Day2/Pipeline2/junction_mappings_corrected_grouped_mapq.xlsx`.
- Sheets: `near_5042` 469, `gap0_far` 90, `remaining` 37 Zeilen.

## 7. Heureka-Momente und Interpretation

### Gap

`gap_length` bezeichnet nicht ausgerichtete Read-Basen zwischen Backbone- und Insert-Intervall. Ein Gap kann potentiell einen nicht gemappten Abschnitt in der Mitte des Übergangs darstellen. Das kann erklären, warum die beobachtete Schnittstelle von 5042 bp abweicht oder warum ein Insert scheinbar später beginnt.

### Overlap und sticky ends

Backbone- und Insert-Alignment können sich auf dem Read geringfügig überlappen, wenn beide Sequenzen ähnliche oder identische Endsequenzen besitzen. Ein kleiner Overlap ist an einer gemeinsamen Schnittstelle erwartbar, etwa durch Sticky Ends, und ist nicht automatisch ein biologischer Widerspruch.

### Backbone-Treffer weit von 5042 bp entfernt

Backbone-Maps etwa im Bereich 2800–3200 bp, die gleichzeitig auf ein Insert mappen, können größtenteils durch Hefegene auf dem Backbone erklärt werden. Beispiel: `YGPM-22o22` ist mit `LEU2` verbunden. Ein solcher Treffer beweist allein keine Junction an 5042 bp.

### Kurze Reads und Multimapping

Kurze Reads, die auf den Backbone, aber auf die Mitte eines Inserts mappen, sind häufig durch Multimapping erklärbar. MAPQ 0 bedeutet, dass viele gleich gute Zuordnungen möglich sind. Wiederholte Sequenzen können auf verschiedenen Inserts vorkommen und dadurch unterschiedliche Mappings erzeugen.

Das Analyseziel ist eine eindeutige Zuordnung zu dem Insert, bei dem der Read an einem Insertende mappt. Dafür sollten Insert-Ende, erwarteter Backbone-Bereich, ausreichende MAPQ, nicht überlappende Readintervalle und die direkte Readsequenz gemeinsam geprüft werden.

## 8. Aktueller Stand

- Der Day-2-Workflow ist digital dokumentiert und die wichtigsten Ergebnisse sind gespeichert.
- Die Junction-Tabelle ist eine Kandidatenliste, kein endgültiger biologischer Beweis.
- Offene Validierung: Kandidaten mit Insert-Ende, hoher MAPQ und direkter Readsequenzprüfung priorisieren.
- Vollständige Details befinden sich in `day2.md`.
