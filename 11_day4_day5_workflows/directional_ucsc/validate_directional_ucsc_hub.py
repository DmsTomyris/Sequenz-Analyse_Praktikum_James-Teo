#!/usr/bin/env python3
"""End-to-end validation for completed directional UCSC hub tracks."""

from __future__ import print_function

import argparse
import collections
import datetime
import hashlib
import os
import subprocess
import sys


ASSEMBLIES = collections.OrderedDict([
    ("pGP85", 1680),
    ("scR64pGP85", 1697),
    ("pGP95", 1747),
    ("scR64pGP95", 1764),
])
TRACK_FILES = [
    "raw_primary.bam",
    "raw_primary.bam.bai",
    "mapq20.bam",
    "mapq20.bam.bai",
    "junction_evidence.bam",
    "junction_evidence.bam.bai",
    "raw_coverage.bw",
    "mapq20_coverage.bw",
    "junction_coverage.bw",
]


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def output(command):
    return subprocess.check_output(command, universal_newlines=True)


def read_chrom_sizes(path):
    result = collections.OrderedDict()
    with open(path, "r") as handle:
        for raw in handle:
            if raw.strip():
                chromosome, length = raw.rstrip("\n\r").split("\t")
                result[chromosome] = int(length)
    return result


def bam_header_sizes(samtools, bam):
    result = collections.OrderedDict()
    for line in output([samtools, "view", "-H", bam]).splitlines():
        if not line.startswith("@SQ\t"):
            continue
        fields = dict(field.split(":", 1) for field in line.split("\t")[1:])
        result[fields["SN"]] = int(fields["LN"])
    return result


def bam_count(samtools, bam):
    return int(output([samtools, "view", "-c", bam]).strip())


def check_trackdb_files(assembly_dir):
    missing = []
    with open(os.path.join(assembly_dir, "trackDb.txt"), "r") as handle:
        for raw in handle:
            fields = raw.strip().split(None, 1)
            if len(fields) == 2 and fields[0] in ("bigDataUrl", "bigDataIndex"):
                path = os.path.join(assembly_dir, fields[1])
                if not os.path.isfile(path) or os.path.getsize(path) == 0:
                    missing.append(fields[1])
    return missing


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--samtools", default="samtools")
    parser.add_argument("--bigBedInfo", required=True)
    parser.add_argument("--bigWigInfo", required=True)
    parser.add_argument("--hubCheck", required=True)
    args = parser.parse_args()
    root = os.path.abspath(args.root)
    if os.path.exists(os.path.join(root, "FINAL_DONE")):
        raise RuntimeError("refusing to overwrite completed validation")
    subprocess.check_call(
        ["sha256sum", "-c", "checksums_build.sha256"],
        cwd=root,
        stdout=subprocess.DEVNULL,
    )
    validation_build = open(
        os.path.join(root, "validation_build.txt"), "r"
    ).read()
    if not validation_build.startswith("status\tPASS\n"):
        raise RuntimeError("build validation is not PASS")

    rows = []
    total_track_bytes = 0
    total_raw_records = 0
    total_mapq20_records = 0
    total_junction_records = 0
    for assembly, expected_chromosomes in ASSEMBLIES.items():
        assembly_dir = os.path.join(root, "ucsc_hub", "assemblies", assembly)
        mapping_dir = os.path.join(root, "mapping_work", assembly)
        if not os.path.exists(os.path.join(mapping_dir, "FINAL_DONE")):
            raise RuntimeError("{} finalizer marker missing".format(assembly))
        chrom_sizes = read_chrom_sizes(
            os.path.join(assembly_dir, assembly + ".chrom.sizes")
        )
        if len(chrom_sizes) != expected_chromosomes:
            raise RuntimeError("{} chromosome count mismatch".format(assembly))
        missing = check_trackdb_files(assembly_dir)
        if missing:
            raise RuntimeError("{} missing trackDb files {}".format(
                assembly, ",".join(missing)
            ))
        tracks = os.path.join(assembly_dir, "tracks")
        for filename in TRACK_FILES:
            path = os.path.join(tracks, filename)
            if not os.path.isfile(path) or os.path.getsize(path) == 0:
                raise RuntimeError("missing or empty {}".format(path))
            rows.append((
                assembly,
                filename,
                os.path.getsize(path),
                sha256_file(path),
                os.path.relpath(path, root).replace(os.sep, "/"),
            ))
            total_track_bytes += os.path.getsize(path)
        raw_bam = os.path.join(tracks, "raw_primary.bam")
        mapq_bam = os.path.join(tracks, "mapq20.bam")
        junction_bam = os.path.join(tracks, "junction_evidence.bam")
        subprocess.check_call([args.samtools, "quickcheck", "-v", raw_bam])
        subprocess.check_call([args.samtools, "quickcheck", "-v", mapq_bam])
        subprocess.check_call([args.samtools, "quickcheck", "-v", junction_bam])
        if bam_header_sizes(args.samtools, raw_bam) != chrom_sizes:
            raise RuntimeError("{} BAM/chrom.sizes mismatch".format(assembly))
        raw_records = bam_count(args.samtools, raw_bam)
        mapq_records = bam_count(args.samtools, mapq_bam)
        junction_records = bam_count(args.samtools, junction_bam)
        if not (0 <= junction_records <= mapq_records <= raw_records):
            raise RuntimeError("{} invalid BAM count ordering".format(assembly))
        total_raw_records += raw_records
        total_mapq20_records += mapq_records
        total_junction_records += junction_records
        for label in ("raw_coverage", "mapq20_coverage", "junction_coverage"):
            subprocess.check_call(
                [args.bigWigInfo, os.path.join(tracks, label + ".bw")],
                stdout=subprocess.DEVNULL,
            )
        for label in (
            "plasmid_structure",
            "plasmid_membership",
            "insert_source",
            "projected_genes",
        ):
            subprocess.check_call(
                [args.bigBedInfo, os.path.join(tracks, label + ".bb")],
                stdout=subprocess.DEVNULL,
            )
        yeast_genes = os.path.join(tracks, "yeast_genes.bb")
        if assembly.startswith("scR64"):
            subprocess.check_call(
                [args.bigBedInfo, yeast_genes],
                stdout=subprocess.DEVNULL,
            )
        elif os.path.exists(yeast_genes):
            raise RuntimeError("{} unexpected yeast gene track".format(assembly))

    subprocess.check_call([
        args.hubCheck,
        "-noTracks",
        os.path.join(root, "ucsc_hub", "hub.txt"),
    ])
    track_manifest = os.path.join(root, "manifests", "mapping_tracks.tsv")
    with open(track_manifest, "w") as handle:
        handle.write("assembly\tfile\tsize_bytes\tsha256\trelative_path\n")
        for row in rows:
            handle.write("\t".join(str(value) for value in row) + "\n")

    generated = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    validation_path = os.path.join(root, "validation.txt")
    values = [
        ("status", "PASS"),
        ("generated_utc", generated),
        ("assemblies", 4),
        ("pGP85_chromosomes", 1680),
        ("scR64pGP85_chromosomes", 1697),
        ("pGP95_chromosomes", 1747),
        ("scR64pGP95_chromosomes", 1764),
        ("mapping_source_reads_per_assembly", 1495785),
        ("raw_alignment_records_all_assemblies", total_raw_records),
        ("mapq20_alignment_records_all_assemblies", total_mapq20_records),
        ("junction_alignment_records_all_assemblies", total_junction_records),
        ("track_files", len(rows)),
        ("track_bytes", total_track_bytes),
        ("build_checksums", "PASS"),
        ("bam_quickcheck", "PASS"),
        ("bam_headers_match_chrom_sizes", "PASS"),
        ("bigbed_bigwig_info", "PASS"),
        ("hubcheck_no_tracks", "PASS"),
        ("circularity_policy", "linear_reference_with_annotated_origin"),
        ("hosting_status", "PENDING_PUBLIC_HTTPS_URL"),
        ("deployment_contact", "PENDING_REPLACE_contact@example.invalid"),
    ]
    with open(validation_path, "w") as handle:
        for key, value in values:
            handle.write("{}\t{}\n".format(key, value))

    checksum_targets = [
        os.path.join(root, "checksums_build.sha256"),
        os.path.join(root, "validation_build.txt"),
        validation_path,
        os.path.join(root, "submission.tsv"),
        track_manifest,
    ]
    for subdir in ("scripts", os.path.join("ucsc_hub")):
        directory = os.path.join(root, subdir)
        for current, dirnames, filenames in os.walk(directory):
            dirnames.sort()
            filenames.sort()
            for filename in filenames:
                checksum_targets.append(os.path.join(current, filename))
    checksum_targets = sorted(set(checksum_targets))
    final_checksum_path = os.path.join(root, "checksums.sha256")
    with open(final_checksum_path, "w") as handle:
        for path in checksum_targets:
            handle.write("{}  {}\n".format(
                sha256_file(path),
                os.path.relpath(path, root).replace(os.sep, "/"),
            ))

    with open(os.path.join(root, "FINAL_DONE"), "w") as handle:
        handle.write("status\tPASS\n")
    print("status\tPASS")
    print("raw_alignment_records\t{}".format(total_raw_records))
    print("mapq20_alignment_records\t{}".format(total_mapq20_records))
    print("junction_alignment_records\t{}".format(total_junction_records))
    print("track_bytes\t{}".format(total_track_bytes))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print("status\tFAIL", file=sys.stderr)
        print("error\t{}".format(error), file=sys.stderr)
        sys.exit(1)
