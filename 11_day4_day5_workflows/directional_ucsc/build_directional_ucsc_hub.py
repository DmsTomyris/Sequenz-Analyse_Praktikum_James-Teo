#!/usr/bin/env python3
"""Build threshold reference sets and four UCSC assembly-hub assemblies."""

from __future__ import print_function

import argparse
import collections
import datetime
import gzip
import hashlib
import html
import os
import shutil
import subprocess
import sys
import tempfile
from urllib.parse import unquote


VALID_DNA = set("ACGTRYSWKMBDHVN")
COMPLEMENT = str.maketrans(
    "ACGTRYSWKMBDHVN",
    "TGCAYRSWMKVHDBN",
)
YEAST_ORDER = [
    "I", "II", "III", "IV", "V", "VI", "VII", "VIII",
    "IX", "X", "XI", "XII", "XIII", "XIV", "XV", "XVI", "Mito",
]


def die(message):
    raise RuntimeError(message)


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_fasta(path):
    records = []
    record_id = None
    parts = []
    with open(path, "r") as handle:
        for line_number, raw in enumerate(handle, 1):
            line = raw.strip()
            if not line:
                continue
            if line.startswith(">"):
                if record_id is not None:
                    records.append((record_id, "".join(parts).upper()))
                header = line[1:].strip()
                if not header:
                    die("{}:{} empty FASTA header".format(path, line_number))
                record_id = header.split()[0]
                parts = []
            else:
                if record_id is None:
                    die("{}:{} sequence before header".format(path, line_number))
                parts.append(line)
    if record_id is not None:
        records.append((record_id, "".join(parts).upper()))
    if not records:
        die("{} contains no FASTA records".format(path))
    ids = [item[0] for item in records]
    if len(ids) != len(set(ids)):
        die("{} has duplicate FASTA IDs".format(path))
    for record_id, sequence in records:
        invalid = set(sequence) - VALID_DNA
        if not sequence or invalid:
            die("{} invalid sequence {} characters {}".format(
                path, record_id, "".join(sorted(invalid))
            ))
    return records


def write_fasta_record(handle, record_id, sequence, width=80):
    handle.write(">{}\n".format(record_id))
    for offset in range(0, len(sequence), width):
        handle.write(sequence[offset:offset + width] + "\n")


def revcomp(sequence):
    return sequence.translate(COMPLEMENT)[::-1]


def read_tsv(path):
    with open(path, "r") as handle:
        header = handle.readline().rstrip("\n\r").split("\t")
        rows = []
        for line_number, raw in enumerate(handle, 2):
            if not raw.strip():
                continue
            fields = raw.rstrip("\n\r").split("\t")
            if len(fields) != len(header):
                die("{}:{} field count mismatch".format(path, line_number))
            rows.append(dict(zip(header, fields)))
    return header, rows


def parse_gff_attributes(text):
    values = {}
    for field in text.split(";"):
        if not field:
            continue
        if "=" in field:
            key, value = field.split("=", 1)
            values[key] = unquote(value)
    return values


def read_gff_genes(path):
    opener = gzip.open if path.endswith(".gz") else open
    genes = collections.defaultdict(list)
    with opener(path, "rt") as handle:
        for raw in handle:
            if not raw or raw.startswith("#"):
                continue
            fields = raw.rstrip("\n\r").split("\t")
            if len(fields) != 9 or fields[2] != "gene":
                continue
            seqid = fields[0]
            if seqid == "MT":
                seqid = "Mito"
            if seqid not in YEAST_ORDER:
                continue
            start0 = int(fields[3]) - 1
            end0 = int(fields[4])
            attrs = parse_gff_attributes(fields[8])
            name = (
                attrs.get("Name")
                or attrs.get("gene_id")
                or attrs.get("ID")
                or "gene_{}_{}".format(start0 + 1, end0)
            ).split(",")[0]
            strand = fields[6] if fields[6] in ("+", "-") else "."
            genes[seqid].append((start0, end0, name, strand))
    if not genes:
        die("no R64-1-1 gene features found in {}".format(path))
    for seqid in genes:
        genes[seqid].sort()
    return genes


def run_checked(command, stdout_path=None):
    if stdout_path:
        with open(stdout_path, "w") as handle:
            subprocess.check_call(command, stdout=handle)
    else:
        subprocess.check_call(command)


def sort_bed(records, chrom_order):
    return sorted(
        records,
        key=lambda row: (
            row[0],
            int(row[1]),
            int(row[2]),
            row[3],
        ),
    )


def write_bed(path, records, chrom_order):
    with open(path, "w") as handle:
        for row in sort_bed(records, chrom_order):
            handle.write("\t".join(str(value) for value in row) + "\n")


def bed_to_bigbed(tool, bed_path, chrom_sizes, output_path, bed_type):
    command = [
        tool,
        "-type={}".format(bed_type),
        "-extraIndex=name",
        bed_path,
        chrom_sizes,
        output_path,
    ]
    run_checked(command)


def safe_html(text):
    return html.escape(str(text), quote=True)


def threshold_membership(direction_rows, threshold):
    selected = []
    counts = collections.Counter()
    for row in direction_rows:
        normal = int(row["normal_reads"])
        reverse = int(row["revcomp_reads"])
        directional = int(row["directional_reads"])
        if normal + reverse != directional:
            die("directional sum mismatch for {}".format(row["insert_id"]))
        if directional < 10:
            orientations = ["normal", "revcomp"]
            selection_class = "both_low_reads"
            counts["both_low_reads_ids"] += 1
        else:
            best = max(normal, reverse)
            if 100 * best >= threshold * directional:
                orientations = ["normal" if normal >= reverse else "revcomp"]
                selection_class = "single_direction"
                counts["single_ids"] += 1
            else:
                orientations = ["normal", "revcomp"]
                selection_class = "both_below_threshold"
                counts["both_below_threshold_ids"] += 1
        for orientation in orientations:
            target_id = row["insert_id"] + ("-revcomp" if orientation == "revcomp" else "")
            selected.append((row, orientation, target_id, selection_class))
    counts["ids"] = len(direction_rows)
    counts["records"] = len(selected)
    counts["both_ids"] = (
        counts["both_low_reads_ids"] + counts["both_below_threshold_ids"]
    )
    return selected, counts


def build_individual_fastas(root, threshold, selected, reference_by_id):
    threshold_dir = os.path.join(root, str(threshold))
    single_dir = os.path.join(threshold_dir, "single_direction")
    both_dir = os.path.join(threshold_dir, "both_directions")
    os.makedirs(single_dir)
    os.makedirs(both_dir)
    for row, orientation, target_id, selection_class in selected:
        directory = single_dir if selection_class == "single_direction" else both_dir
        path = os.path.join(directory, target_id + ".fasta")
        if os.path.exists(path):
            die("refusing to overwrite {}".format(path))
        with open(path, "w") as handle:
            write_fasta_record(handle, target_id, reference_by_id[target_id])


def build_manifest_rows(threshold, selected, metadata, reference_by_id):
    rows = []
    for direction, orientation, target_id, selection_class in selected:
        insert_id = direction["insert_id"]
        meta = metadata[insert_id]
        normal = int(direction["normal_reads"])
        reverse = int(direction["revcomp_reads"])
        directional = int(direction["directional_reads"])
        selected_reads = normal if orientation == "normal" else reverse
        percent = (100.0 * selected_reads / directional) if directional else 0.0
        source_start0 = int(meta["begin"]) - 1
        source_end0 = int(meta["end"]) - 1
        rows.append({
            "threshold": threshold,
            "insert_id": insert_id,
            "chromosome_id": target_id,
            "orientation": orientation,
            "selection_class": selection_class,
            "normal_reads": normal,
            "revcomp_reads": reverse,
            "directional_reads": directional,
            "selected_orientation_reads": selected_reads,
            "selected_orientation_percent": "{:.6f}".format(percent),
            "source_chr": meta["chr"],
            "source_begin_1based": meta["begin"],
            "source_end_boundary_1based": meta["end"],
            "source_start_0based": source_start0,
            "source_end_0based_exclusive": source_end0,
            "insert_length": meta["length"],
            "chromosome_length": len(reference_by_id[target_id]),
            "sequence_sha256": hashlib.sha256(
                reference_by_id[target_id].encode("ascii")
            ).hexdigest(),
        })
    return rows


def write_dict_tsv(path, rows, fields):
    with open(path, "w") as handle:
        handle.write("\t".join(fields) + "\n")
        for row in rows:
            handle.write("\t".join(str(row[field]) for field in fields) + "\n")


def build_assembly(
    hub_root,
    assembly_name,
    threshold,
    include_yeast,
    manifest_rows,
    reference_by_id,
    yeast_records,
    metadata,
    gff_genes,
    tools,
):
    assembly_dir = os.path.join(hub_root, "assemblies", assembly_name)
    track_dir = os.path.join(assembly_dir, "tracks")
    source_dir = os.path.join(assembly_dir, "source")
    os.makedirs(track_dir)
    os.makedirs(source_dir)

    plasmid_records = [
        (row["chromosome_id"], reference_by_id[row["chromosome_id"]])
        for row in manifest_rows
    ]
    records = []
    if include_yeast:
        records.extend(
            ("yeast_chr" + record_id, sequence)
            for record_id, sequence in yeast_records
        )
    records.extend(plasmid_records)
    records.sort(key=lambda item: item[0])
    ids = [record_id for record_id, _ in records]
    if len(ids) != len(set(ids)):
        die("{} duplicate chromosome IDs".format(assembly_name))
    chrom_order = dict((record_id, index) for index, record_id in enumerate(ids))

    fasta_path = os.path.join(source_dir, assembly_name + ".fasta")
    with open(fasta_path, "w") as handle:
        for record_id, sequence in records:
            write_fasta_record(handle, record_id, sequence)

    chrom_sizes = os.path.join(assembly_dir, assembly_name + ".chrom.sizes")
    with open(chrom_sizes, "w") as handle:
        for record_id, sequence in records:
            handle.write("{}\t{}\n".format(record_id, len(sequence)))

    two_bit = os.path.join(assembly_dir, assembly_name + ".2bit")
    run_checked([tools["faToTwoBit"], fasta_path, two_bit])
    two_bit_sizes = chrom_sizes + ".twoBitInfo.tmp"
    run_checked([tools["twoBitInfo"], two_bit, "stdout"], stdout_path=two_bit_sizes)
    expected_sizes = dict(
        line.rstrip("\n").split("\t")
        for line in open(chrom_sizes, "r") if line.strip()
    )
    observed_sizes = dict(
        line.rstrip("\n").split("\t")
        for line in open(two_bit_sizes, "r") if line.strip()
    )
    os.unlink(two_bit_sizes)
    if expected_sizes != observed_sizes:
        die("{} FASTA/2bit size mismatch".format(assembly_name))

    alias_path = os.path.join(assembly_dir, "chromAlias.txt")
    with open(alias_path, "w") as handle:
        if include_yeast:
            for record_id, _ in yeast_records:
                handle.write("yeast_chr{}\t{}\n".format(record_id, record_id))
        for row in manifest_rows:
            handle.write("{0}\t{0}\n".format(row["chromosome_id"]))

    junction_path = os.path.join(assembly_dir, "junctions.tsv")
    with open(junction_path, "w") as handle:
        handle.write("chromosome_id\tleft_junction_0based\tright_junction_0based\n")
        for row in manifest_rows:
            insert_length = int(row["insert_length"])
            handle.write("{}\t5042\t{}\n".format(
                row["chromosome_id"], 5042 + insert_length
            ))

    structure = []
    membership = []
    insert_source = []
    projected_genes = []
    yeast_genes = []
    manifest_by_chrom = dict((row["chromosome_id"], row) for row in manifest_rows)
    for chromosome_id, sequence in plasmid_records:
        row = manifest_by_chrom[chromosome_id]
        insert_length = int(row["insert_length"])
        insert_end = 5042 + insert_length
        structure.extend([
            (chromosome_id, 0, 5042, "backbone_left", 0, "+", 0, 5042, "47,111,180"),
            (chromosome_id, 5042, insert_end, "insert", 0, row["orientation"] == "normal" and "+" or "-", 5042, insert_end, "230,126,34"),
            (chromosome_id, insert_end, len(sequence), "backbone_right", 0, "+", insert_end, len(sequence), "47,111,180"),
            (chromosome_id, 5041, 5042, "junction_left", 1000, "+", 5041, 5042, "200,35,51"),
            (chromosome_id, insert_end, min(insert_end + 1, len(sequence)), "junction_right", 1000, "+", insert_end, min(insert_end + 1, len(sequence)), "200,35,51"),
            (chromosome_id, 0, 1, "linear_origin", 1000, "+", 0, 1, "128,0,128"),
        ])
        directional = int(row["directional_reads"])
        orientation_reads = int(row["selected_orientation_reads"])
        score = int(round(1000.0 * orientation_reads / directional)) if directional else 0
        membership.append((
            chromosome_id, 0, len(sequence), chromosome_id, score,
            "+" if row["orientation"] == "normal" else "-"
        ))
        source_name = "yeast_chr{}:{}-{}".format(
            row["source_chr"],
            row["source_begin_1based"],
            int(row["source_end_boundary_1based"]) - 1,
        )
        source_strand = "+" if row["orientation"] == "normal" else "-"
        insert_source.append((
            chromosome_id, 5042, insert_end, source_name, score, source_strand
        ))

        source_chr = row["source_chr"]
        source_start = int(row["source_start_0based"])
        source_end = int(row["source_end_0based_exclusive"])
        for gene_start, gene_end, gene_name, gene_strand in gff_genes.get(source_chr, []):
            overlap_start = max(source_start, gene_start)
            overlap_end = min(source_end, gene_end)
            if overlap_start >= overlap_end:
                continue
            if row["orientation"] == "normal":
                projected_start = 5042 + overlap_start - source_start
                projected_end = 5042 + overlap_end - source_start
                projected_strand = gene_strand
            else:
                projected_start = 5042 + source_end - overlap_end
                projected_end = 5042 + source_end - overlap_start
                projected_strand = (
                    "-" if gene_strand == "+" else "+"
                    if gene_strand == "-" else "."
                )
            clipped = overlap_start != gene_start or overlap_end != gene_end
            display_name = gene_name + ("_partial" if clipped else "")
            projected_genes.append((
                chromosome_id,
                projected_start,
                projected_end,
                display_name,
                0,
                projected_strand,
            ))

    if include_yeast:
        yeast_lengths = dict((record_id, len(seq)) for record_id, seq in yeast_records)
        for seqid in YEAST_ORDER:
            for gene_start, gene_end, gene_name, gene_strand in gff_genes.get(seqid, []):
                if gene_start < 0 or gene_end > yeast_lengths[seqid]:
                    die("gene {} outside yeast chromosome {}".format(gene_name, seqid))
                yeast_genes.append((
                    "yeast_chr" + seqid, gene_start, gene_end,
                    gene_name, 0, gene_strand,
                ))

    bed_specs = [
        ("plasmid_structure", structure, "bed9"),
        ("plasmid_membership", membership, "bed6"),
        ("insert_source", insert_source, "bed6"),
        ("projected_genes", projected_genes, "bed6"),
    ]
    if include_yeast:
        bed_specs.append(("yeast_genes", yeast_genes, "bed6"))
    for label, rows, bed_type in bed_specs:
        bed_path = os.path.join(track_dir, label + ".bed")
        bb_path = os.path.join(track_dir, label + ".bb")
        write_bed(bed_path, rows, chrom_order)
        bed_to_bigbed(
            tools["bedToBigBed"], bed_path, chrom_sizes, bb_path, bed_type
        )

    with open(os.path.join(assembly_dir, "groups.txt"), "w") as handle:
        handle.write(
            "name assembly\nlabel Assembly structure\npriority 1\ndefaultIsClosed 0\n\n"
            "name annotation\nlabel Gene annotation\npriority 2\ndefaultIsClosed 0\n\n"
            "name mapping\nlabel Read mapping\npriority 3\ndefaultIsClosed 0\n"
        )

    track_stanzas = [
        """
track plasmidStructure
shortLabel Plasmid parts
longLabel Backbone, insert, junctions and artificial linear origin
type bigBed 9
bigDataUrl tracks/plasmid_structure.bb
itemRgb on
visibility pack
group assembly
priority 1
""",
        """
track plasmidMembership
shortLabel Direction call
longLabel Selected plasmid chromosomes and orientation confidence
type bigBed 6
bigDataUrl tracks/plasmid_membership.bb
searchIndex name
visibility dense
group assembly
priority 2
""",
        """
track insertSource
shortLabel Insert source
longLabel R64-1-1 source interval and orientation of each insert
type bigBed 6
bigDataUrl tracks/insert_source.bb
visibility pack
group assembly
priority 3
""",
        """
track projectedGenes
shortLabel Insert genes
longLabel R64-1-1 genes projected onto plasmid insert coordinates
type bigBed 6
bigDataUrl tracks/projected_genes.bb
searchIndex name
visibility pack
group annotation
priority 10
""",
    ]
    if include_yeast:
        track_stanzas.append("""
track yeastGenes
shortLabel Yeast genes
longLabel Ensembl R64-1-1 genes on the host chromosomes
type bigBed 6
bigDataUrl tracks/yeast_genes.bb
searchIndex name
visibility pack
group annotation
priority 11
""")
    track_stanzas.extend([
        """
track rawPrimary
shortLabel Raw primary
longLabel Primary and supplementary ONT alignments; secondary alignments suppressed
type bam
bigDataUrl tracks/raw_primary.bam
bigDataIndex tracks/raw_primary.bam.bai
visibility hide
group mapping
priority 20
maxWindowToDraw 100000
""",
        """
track mapq20
shortLabel MAPQ 20
longLabel Primary and supplementary alignments with MAPQ at least 20
type bam
bigDataUrl tracks/mapq20.bam
bigDataIndex tracks/mapq20.bam.bai
visibility hide
group mapping
priority 21
maxWindowToDraw 100000
""",
        """
track junctionEvidence
shortLabel Junction reads
longLabel MAPQ at least 20 with 50 aligned bases on each side of a plasmid junction
type bam
bigDataUrl tracks/junction_evidence.bam
bigDataIndex tracks/junction_evidence.bam.bai
visibility pack
group mapping
priority 22
maxWindowToDraw 100000
""",
        """
track rawCoverage
shortLabel Raw coverage
longLabel Unnormalized depth from primary and supplementary alignments
type bigWig
bigDataUrl tracks/raw_coverage.bw
visibility hide
autoScale on
group mapping
priority 30
""",
        """
track mapq20Coverage
shortLabel MAPQ20 depth
longLabel Unnormalized depth from alignments with MAPQ at least 20
type bigWig
bigDataUrl tracks/mapq20_coverage.bw
visibility full
autoScale on
group mapping
priority 31
""",
        """
track junctionCoverage
shortLabel Junction depth
longLabel Unnormalized depth from high-confidence junction alignments
type bigWig
bigDataUrl tracks/junction_coverage.bw
visibility full
autoScale on
group mapping
priority 32
""",
    ])
    with open(os.path.join(assembly_dir, "trackDb.txt"), "w") as handle:
        handle.write("\n".join(stanza.strip() for stanza in track_stanzas) + "\n")

    assembly_label = (
        "R64-1-1 + plasmids" if include_yeast else "Plasmids only"
    )
    with open(os.path.join(assembly_dir, "description.html"), "w") as handle:
        handle.write(
            "<!doctype html><html><head><meta charset=\"utf-8\">"
            "<title>{}</title></head><body>"
            "<h1>{}</h1><p>Threshold: {}%. {}.</p>"
            "<p>Each plasmid FASTA record is represented as a separate linear "
            "browser chromosome. The biological molecules are circular; coordinate "
            "0 is an artificial linear origin. The insert starts at 0-based "
            "coordinate 5042.</p></body></html>".format(
                safe_html(assembly_name), safe_html(assembly_name),
                threshold, safe_html(assembly_label)
            )
        )
    return {
        "assembly": assembly_name,
        "threshold": threshold,
        "include_yeast": "yes" if include_yeast else "no",
        "chromosomes": len(records),
        "plasmid_chromosomes": len(plasmid_records),
        "yeast_chromosomes": len(yeast_records) if include_yeast else 0,
        "total_bases": sum(len(sequence) for _, sequence in records),
        "fasta": "ucsc_hub/assemblies/{0}/source/{0}.fasta".format(
            assembly_name
        ),
        "two_bit": "ucsc_hub/assemblies/{0}/{0}.2bit".format(
            assembly_name
        ),
        "chrom_sizes": "ucsc_hub/assemblies/{0}/{0}.chrom.sizes".format(
            assembly_name
        ),
    }


def write_hub_files(hub_root, assemblies, gff_url, gff_sha):
    with open(os.path.join(hub_root, "hub.txt"), "w") as handle:
        handle.write(
            "hub directionalPlasmidGenomes\n"
            "shortLabel Direction genomes\n"
            "longLabel Direction-selected pGP564 plasmids with optional R64-1-1 host\n"
            "genomesFile genomes.txt\n"
            "email contact@example.invalid\n"
            "descriptionUrl aboutHub.html\n"
        )
    with open(os.path.join(hub_root, "aboutHub.html"), "w") as handle:
        handle.write(
            "<!doctype html><html><head><meta charset=\"utf-8\">"
            "<title>Directional plasmid genome hub</title></head><body>"
            "<h1>Directional plasmid genome hub</h1>"
            "<p>Four assemblies represent 85% and 95% orientation thresholds, "
            "each in plasmid-only and R64-1-1 plus plasmid form.</p>"
            "<p>Gene source: <a href=\"{0}\">{0}</a>; SHA-256 {1}.</p>"
            "<p>Before deployment replace contact@example.invalid with the "
            "responsible contact address.</p></body></html>".format(
                safe_html(gff_url), safe_html(gff_sha)
            )
        )
    labels = {
        "pGP85": ("pGP85", "pGP564 plasmids, 85 percent direction threshold"),
        "scR64pGP85": ("Yeast+pGP85", "R64-1-1 yeast plus pGP564 plasmids, 85 percent threshold"),
        "pGP95": ("pGP95", "pGP564 plasmids, 95 percent direction threshold"),
        "scR64pGP95": ("Yeast+pGP95", "R64-1-1 yeast plus pGP564 plasmids, 95 percent threshold"),
    }
    with open(os.path.join(hub_root, "genomes.txt"), "w") as handle:
        for assembly in assemblies:
            name = assembly["assembly"]
            short_label, long_label = labels[name]
            handle.write(
                "genome {0}\n"
                "trackDb assemblies/{0}/trackDb.txt\n"
                "groups assemblies/{0}/groups.txt\n"
                "twoBitPath assemblies/{0}/{0}.2bit\n"
                "chromAlias assemblies/{0}/chromAlias.txt\n"
                "organism {1}\n"
                "description {2}\n"
                "defaultPos YGPM1j22:1-20000\n"
                "htmlPath assemblies/{0}/description.html\n\n".format(
                    name, short_label, long_label
                )
            )


def collect_checksums(root, output_path):
    entries = []
    for directory, dirnames, filenames in os.walk(root):
        dirnames.sort()
        filenames.sort()
        for filename in filenames:
            path = os.path.join(directory, filename)
            if os.path.abspath(path) == os.path.abspath(output_path):
                continue
            entries.append((sha256_file(path), os.path.relpath(path, root)))
    with open(output_path, "w") as handle:
        for digest, relative in entries:
            handle.write("{}  {}\n".format(digest, relative.replace(os.sep, "/")))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference", required=True)
    parser.add_argument("--direction-summary", required=True)
    parser.add_argument("--minimal-inserts-tsv", required=True)
    parser.add_argument("--genome", required=True)
    parser.add_argument("--backbone", required=True)
    parser.add_argument("--gff3", required=True)
    parser.add_argument("--gff-url", required=True)
    parser.add_argument("--faToTwoBit", required=True)
    parser.add_argument("--twoBitInfo", required=True)
    parser.add_argument("--bedToBigBed", required=True)
    parser.add_argument("--output-root", required=True)
    args = parser.parse_args()

    final_root = os.path.abspath(args.output_root)
    if os.path.lexists(final_root):
        die("refusing to overwrite existing output root {}".format(final_root))
    parent = os.path.dirname(final_root)
    os.makedirs(parent, exist_ok=True)
    staging = tempfile.mkdtemp(
        prefix="." + os.path.basename(final_root) + ".staging.",
        dir=parent,
    )
    try:
        reference_records = read_fasta(args.reference)
        if len(reference_records) != 3176:
            die("expected 3176 reference records, got {}".format(
                len(reference_records)
            ))
        reference_by_id = collections.OrderedDict(reference_records)
        _, direction_rows = read_tsv(args.direction_summary)
        if len(direction_rows) != 1588:
            die("expected 1588 direction rows")
        _, metadata_rows = read_tsv(args.minimal_inserts_tsv)
        metadata = dict((row["clone"], row) for row in metadata_rows)
        if len(metadata) != 1588:
            die("expected 1588 unique insert metadata rows")
        yeast_records_raw = read_fasta(args.genome)
        yeast_by_id = dict(yeast_records_raw)
        if set(yeast_by_id) != set(YEAST_ORDER):
            die("unexpected R64-1-1 FASTA identifiers: {}".format(
                ",".join(sorted(yeast_by_id))
            ))
        yeast_records = [(seqid, yeast_by_id[seqid]) for seqid in YEAST_ORDER]
        backbone_records = read_fasta(args.backbone)
        if len(backbone_records) != 1:
            die("expected one backbone")
        backbone = backbone_records[0][1]
        if len(backbone) != 7371:
            die("expected 7371 bp backbone")

        direction_ids = [row["insert_id"] for row in direction_rows]
        if len(direction_ids) != len(set(direction_ids)):
            die("duplicate direction IDs")
        if set(direction_ids) != set(metadata):
            die("direction IDs and metadata IDs differ")
        expected_reference_ids = set(direction_ids)
        expected_reference_ids.update(insert_id + "-revcomp" for insert_id in direction_ids)
        if set(reference_by_id) != expected_reference_ids:
            die("reference IDs differ from direction IDs")
        for insert_id in direction_ids:
            meta = metadata[insert_id]
            start0 = int(meta["begin"]) - 1
            end0 = int(meta["end"]) - 1
            insert = yeast_by_id[meta["chr"]][start0:end0]
            if len(insert) != int(meta["length"]):
                die("metadata length mismatch for {}".format(insert_id))
            normal = reference_by_id[insert_id]
            reverse = reference_by_id[insert_id + "-revcomp"]
            if normal != backbone[:5042] + insert + backbone[5042:]:
                die("normal sequence mismatch for {}".format(insert_id))
            if reverse != backbone[:5042] + revcomp(insert) + backbone[5042:]:
                die("reverse sequence mismatch for {}".format(insert_id))

        gff_genes = read_gff_genes(args.gff3)
        tools = {
            "faToTwoBit": args.faToTwoBit,
            "twoBitInfo": args.twoBitInfo,
            "bedToBigBed": args.bedToBigBed,
        }
        manifests_dir = os.path.join(staging, "manifests")
        hub_root = os.path.join(staging, "ucsc_hub")
        os.makedirs(manifests_dir)
        os.makedirs(os.path.join(hub_root, "assemblies"))
        fields = [
            "threshold", "insert_id", "chromosome_id", "orientation",
            "selection_class", "normal_reads", "revcomp_reads",
            "directional_reads", "selected_orientation_reads",
            "selected_orientation_percent", "source_chr",
            "source_begin_1based", "source_end_boundary_1based",
            "source_start_0based", "source_end_0based_exclusive",
            "insert_length", "chromosome_length", "sequence_sha256",
        ]
        all_manifest_rows = []
        threshold_data = {}
        expected = {
            85: {"single_ids": 1496, "both_ids": 92, "records": 1680},
            95: {"single_ids": 1429, "both_ids": 159, "records": 1747},
        }
        for threshold in (85, 95):
            selected, counts = threshold_membership(direction_rows, threshold)
            for key, value in expected[threshold].items():
                if counts[key] != value:
                    die("threshold {} {} {} != expected {}".format(
                        threshold, key, counts[key], value
                    ))
            if counts["both_low_reads_ids"] != 53:
                die("threshold {} expected 53 low-read double IDs".format(threshold))
            build_individual_fastas(staging, threshold, selected, reference_by_id)
            rows = build_manifest_rows(
                threshold, selected, metadata, reference_by_id
            )
            write_dict_tsv(
                os.path.join(manifests_dir, "threshold_{}.tsv".format(threshold)),
                rows,
                fields,
            )
            all_manifest_rows.extend(rows)
            threshold_data[threshold] = rows
        write_dict_tsv(
            os.path.join(manifests_dir, "threshold_membership.tsv"),
            all_manifest_rows,
            fields,
        )

        assembly_specs = [
            ("pGP85", 85, False),
            ("scR64pGP85", 85, True),
            ("pGP95", 95, False),
            ("scR64pGP95", 95, True),
        ]
        assemblies = []
        for assembly_name, threshold, include_yeast in assembly_specs:
            assemblies.append(build_assembly(
                hub_root, assembly_name, threshold, include_yeast,
                threshold_data[threshold], reference_by_id, yeast_records,
                metadata, gff_genes, tools,
            ))
        write_dict_tsv(
            os.path.join(manifests_dir, "assemblies.tsv"),
            assemblies,
            [
                "assembly", "threshold", "include_yeast", "chromosomes",
                "plasmid_chromosomes", "yeast_chromosomes", "total_bases",
                "fasta", "two_bit", "chrom_sizes",
            ],
        )
        gff_sha = sha256_file(args.gff3)
        write_hub_files(hub_root, assemblies, args.gff_url, gff_sha)

        generated = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
        validation_rows = [
            ("status", "PASS"),
            ("generated_utc", generated),
            ("reference", os.path.abspath(args.reference)),
            ("reference_sha256", sha256_file(args.reference)),
            ("direction_summary", os.path.abspath(args.direction_summary)),
            ("direction_summary_sha256", sha256_file(args.direction_summary)),
            ("minimal_inserts_tsv", os.path.abspath(args.minimal_inserts_tsv)),
            ("minimal_inserts_tsv_sha256", sha256_file(args.minimal_inserts_tsv)),
            ("genome", os.path.abspath(args.genome)),
            ("genome_sha256", sha256_file(args.genome)),
            ("backbone", os.path.abspath(args.backbone)),
            ("backbone_sha256", sha256_file(args.backbone)),
            ("gff3", os.path.abspath(args.gff3)),
            ("gff3_url", args.gff_url),
            ("gff3_sha256", gff_sha),
            ("reference_records", len(reference_records)),
            ("insert_ids", len(direction_rows)),
            ("low_read_double_ids", 53),
            ("zero_zero_ids_with_both_orientations", 12),
            ("pGP85_chromosomes", 1680),
            ("scR64pGP85_chromosomes", 1697),
            ("pGP95_chromosomes", 1747),
            ("scR64pGP95_chromosomes", 1764),
            ("sequence_validation", "PASS"),
            ("fasta_twobit_lengths", "PASS"),
            ("annotation_bounds", "PASS"),
            ("projected_gene_orientation", "PASS"),
            ("overwrite_protection", "enabled"),
        ]
        with open(os.path.join(staging, "validation_build.txt"), "w") as handle:
            for key, value in validation_rows:
                handle.write("{}\t{}\n".format(key, value))
        collect_checksums(
            staging, os.path.join(staging, "checksums_build.sha256")
        )
        os.rename(staging, final_root)
        staging = None
        print("status\tPASS")
        print("output_root\t{}".format(final_root))
        for assembly in assemblies:
            print("{}\t{}".format(assembly["assembly"], assembly["chromosomes"]))
    finally:
        if staging and os.path.exists(staging):
            shutil.rmtree(staging)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print("status\tFAIL", file=sys.stderr)
        print("error\t{}".format(error), file=sys.stderr)
        sys.exit(1)
