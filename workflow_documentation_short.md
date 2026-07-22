# Kurz-Dokumentation des Mapping-Workflows

## Hauptergebnisse

| Referenz | Gemappte Reads | Anteil aller Reads | Tool / Lauf |
|---|---:|---:|---|
| Hefe | 20 | 0,093 % | Minimap2 `map-ont`, Run 1/10 |
| Backbone | 15 | 0,070 % | Minimap2 `map-ont`, Run 1/10 |
| Mensch | 9 | 0,042 % | Minimap2 `map-ont`, Run 10 |
| Maus | 2 | 0,009 % | Minimap2 `map-ont`, Run 10 |
| Drosophila | 0 | 0,000 % | Minimap2 `map-ont`, Run 10 |
| Zebrafisch | 2 | 0,009 % | Minimap2 `map-ont`, Run 10 |
| *E. coli* | 20 | 0,093 % | Minimap2 `map-ont`, Run 10 |
| BLAST: zusätzliche starke Treffer | 0 | 0,000 % | BLAST-Kontrolle, Run 7 |

Die Hefe- und Backbone-Werte sind getrennte Referenzklassen. Die Werte sind primäre Read-Zuordnungen; ein Read kann bei getrennten Referenzläufen in mehreren Zeilen auftauchen. Die Prozentwerte beziehen sich auf ungefähr 21.500 Ausgangsreads.

---

## Run 1 – Ausgangsmapping Hefe und Backbone

- **Tool:** Minimap2, Samtools
- **Input:** `PBK89872_pass_barcode77_merged.fastq`; `genome.fa`; `pGP564_backbone.fa`
- **Parameter:** `minimap2 -ax map-ont`; primäre Alignments
- **Output:** `mapping_results/` mit BAM, Index, Flagstat und Coverage
- **Ergebnis:** Hefe 20 Reads (0,093 %), Backbone 15 (0,070 %), zusammen 35; 99,837 % unmapped.

## Run 2 – Short-Read-Diagnose

- **Tool:** Minimap2, Samtools
- **Input:** Original-FASTQ und dieselben Referenzen
- **Parameter:** `minimap2 -ax sr`
- **Output:** `mapping_results/short_preset/`
- **Ergebnis:** Hefe 44 Reads (0,205 %), Backbone 16 (0,075 %), 21.358 Reads unmapped.
- **Änderung:** Preset von `map-ont` auf `sr` geändert.

## Run 3 – erstes SPLAT-Trimming und Mapping

- **Tool:** Cutadapt/SPLAT, Minimap2, Samtools
- **Input:** Original-FASTQ
- **Parameter:** Adapter `ACACGACGCTCTTCCGATCT`, Mindestlänge 30 bp, Minimap2 `map-ont`
- **Output:** `mapping_results_splat_trimmed/trimmed.fastq` und Mappingordner
- **Ergebnis:** 19.611 Adaptertreffer, 379 verworfene Reads; Hefe 20, Backbone 15.
- **Änderung:** Erstes Adaptertrimming vor dem Mapping.

## Run 4 – zweites SPLAT-Trimming und Mapping

- **Tool:** Cutadapt/SPLAT, Minimap2, Samtools
- **Input:** `trimmed.fastq`
- **Parameter:** gleicher Adapter, Mindestlänge 30 bp, `map-ont`
- **Output:** zweites Trim-FASTQ und zweiter Mappingordner
- **Ergebnis:** 12.363 Adaptertreffer, 623 verworfene Reads; Hefe 20, Backbone 15.
- **Änderung:** Trimming erneut auf bereits getrimmte Reads angewendet.

## Run 5 – drittes SPLAT-Trimming und Mapping

- **Tool:** Cutadapt/SPLAT, Minimap2, Samtools
- **Input:** zweimal getrimmtes FASTQ
- **Parameter:** gleicher Adapter, Mindestlänge 30 bp, `map-ont`
- **Output:** drittes Trim-FASTQ und Mappingordner
- **Ergebnis:** 5.999 Adaptertreffer, 1.207 verworfene Reads; Hefe 20, Backbone 15.
- **Änderung:** weiterer identischer Trim-Durchlauf.

## Run 6 – viertes SPLAT-Trimming und Mapping

- **Tool:** Cutadapt/SPLAT, Minimap2, Samtools
- **Input:** dreimal getrimmtes FASTQ
- **Parameter:** gleicher Adapter, Mindestlänge 30 bp, `map-ont`
- **Output:** viertes Trim-FASTQ und Mappingordner
- **Ergebnis:** 2.983 Adaptertreffer, 919 verworfene Reads; Hefe 20, Backbone 15.
- **Änderung:** weiterer identischer Trim-Durchlauf; absolute Mappingtreffer unverändert.

## Run 7 – BLAST-Kontrolle der Minimap-unmapped Reads

- **Tool:** BLASTN-short, Samtools
- **Input:** Minimap-unmapped Reads aus Run 6
- **Parameter:** `word_size 11`, E-Wert `1e-5`, mindestens 80 % Identität und 50 bp Query-Abdeckung
- **Output:** `fourth_blast_check/`
- **Ergebnis:** keine überzeugenden zusätzlichen Treffer; 0 Reads mit mindestens 30 bp und mindestens 90 % Identität.

## Run 8 – Identitätsschwellen 70/60/50 %

- **Tool:** Minimap2 und BLAST
- **Input:** Original-FASTQ ohne Adapter-Cut
- **Parameter:** 70 %, 60 % und 50 % Übereinstimmung; Mindestlängen 50, 75 und 100 bp
- **Output:** `raw_identity_test/`
- **Ergebnis:** Minimap2 und BLAST jeweils 35 Treffer pro Schwelle; Hefe 20, Backbone 15.
- **Änderung:** niedrigere Identitätsschwellen mit Mindestlängen getestet.

## Run 9 – Cross-Species-Mapping mit Short-Read-Preset

- **Tool:** Minimap2, Samtools
- **Input:** Original-FASTQ ohne Adapter-Cut; Hefe, Mensch, Maus, Drosophila, Zebrafisch und *E. coli*
- **Parameter:** `minimap2 -ax sr`; mindestens 70 % Identität und 50 bp
- **Output:** `cross_species_mapping/`
- **Ergebnis:** Mensch 11, Maus 2, Drosophila 4, Zebrafisch 2, *E. coli* 20 Reads.
- **Änderung:** Fremdorganismen und `sr`-Preset ergänzt.

## Run 10 – ursprünglicher `map-ont`-Workflow für Fremdorganismen

- **Tool:** Minimap2, Samtools
- **Input:** Original-FASTQ ohne Adapter-Cut; dieselben Referenzen wie Run 9
- **Parameter:** `minimap2 -ax map-ont`
- **Output:** `individual_mapont_comparison/`
- **Ergebnis:** Hefe 20, Backbone 15, Mensch 9, Maus 2, Drosophila 0, Zebrafisch 2, *E. coli* 20 Reads.
- **Änderung:** Preset von `sr` zurück auf `map-ont` gesetzt.

---

## Positivkontrollen

Der folgende Abschnitt wurde aus [`positive_controls/positive_control_report.md`](positive_controls/positive_control_report.md) übernommen.

# Positivkontrolle: Hefegenom-Mapping

## Methode

Öffentliche, nicht künstlich erzeugte *Saccharomyces cerevisiae*-Whole-Genome-Sequenzierungsreads wurden auf `genome.fa` gemappt. Die Kontrolle prüft, ob FASTQ-Verarbeitung, Referenz und Mapper grundsätzlich funktionieren.

## Input

- Quelle: NCBI Sequence Read Archive, Lauf **SRR8455574**
- Organismus: *Saccharomyces cerevisiae* SA1
- Datentyp: genomische DNA, Illumina Whole-Genome-Sequenzierung
- Verwendet: erste 100.000 Reads aus `SRR8455574_1.fastq.gz`
- Lokale Datei: `real_yeast_SRR8455574_100k.fastq`

Quelle: [NCBI SRA SRR8455574](https://www.ncbi.nlm.nih.gov/sra/SRR8455574)

## Parameter

- Referenz: `genome.fa`
- Mapper: Minimap2 2.31
- Preset: `-x sr` für kurze, genaue Reads
- Ausgabe: sortierte und indexierte BAM-Datei
- Auswertung: `samtools flagstat` und `samtools coverage`

## Output

- 100.000 Reads analysiert
- 97.561 primäre Alignments: **97,56 % gemappt**
- 588 zusätzliche supplementary Alignments
- 56,88 % der Hefegenomreferenz mindestens einmal abgedeckt

## Schlussfolgerung

Die Positivkontrolle zeigt, dass FASTQ-Verarbeitung, Hefegenomreferenz, Minimap2 und BAM-Auswertung grundsätzlich funktionieren. Die geringe Mappingrate der ursprünglichen Probe ist daher wahrscheinlich nicht durch einen generellen technischen Fehler des Mapping-Workflows verursacht.
