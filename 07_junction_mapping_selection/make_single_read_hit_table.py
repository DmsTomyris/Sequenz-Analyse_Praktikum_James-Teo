#!/usr/bin/env python3
import csv
import re
import sys
from openpyxl import Workbook
from openpyxl.styles import Font

CIGAR_RE = re.compile(r"(\d+)([MIDNSHP=X])")


def fasta_lengths(path):
    result = {}
    name = None
    length = 0
    with open(path, encoding="utf-8", errors="replace") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            if line.startswith(">"):
                if name is not None:
                    result[name] = length
                name = line[1:].split()[0]
                length = 0
            else:
                length += len(line)
    if name is not None:
        result[name] = length
    return result


def read_length(path, read_id):
    with open(path, encoding="utf-8", errors="replace") as handle:
        while True:
            header = handle.readline()
            if not header:
                break
            sequence = handle.readline().strip()
            handle.readline()
            handle.readline()
            if header[1:].split()[0] == read_id:
                return len(sequence)
    raise ValueError(f"Read not found: {read_id}")


def intervals(pos, cigar, read_len, flag):
    qpos = 0
    rpos = pos
    qs = qe = rs = reff = None
    for text, op in CIGAR_RE.findall(cigar):
        n = int(text)
        if op in "MIS=XH":
            if op in "M=X":
                if qs is None:
                    qs = qpos + 1
                qe = qpos + n
            qpos += n
        if op in "MDN=X":
            if op in "M=X":
                if rs is None:
                    rs = rpos
                reff = rpos + n - 1
            rpos += n
    if qs is None or rs is None:
        return None
    if flag & 16:
        qs, qe = read_len - qe + 1, read_len - qs + 1
    return qs, qe, rs, reff


def signed_gap(a, b, c, d):
    if b < c:
        return c - b - 1
    if d < a:
        return a - d - 1
    return -(min(b, d) - max(a, c) + 1)


def main():
    if len(sys.argv) != 5:
        raise SystemExit("usage: script.py SAM FASTQ REFERENCE OUTPUT.xlsx")
    sam_path, fastq_path, reference_path, output_path = sys.argv[1:]
    reference_lengths = fasta_lengths(reference_path)
    read_id = None
    read_len = None
    records = []
    with open(sam_path, encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if line.startswith("@"):
                continue
            fields = line.rstrip("\n").split("\t")
            if len(fields) < 6:
                continue
            rid, flag_text, ref, pos_text, mapq_text, cigar = fields[:6]
            if flag_text == "4" or ref == "*" or cigar == "*":
                continue
            if read_id is None:
                read_id = rid
                read_len = read_length(fastq_path, rid)
            if rid != read_id or int(flag_text) & 4:
                continue
            flag = int(flag_text)
            iv = intervals(int(pos_text), cigar, read_len, flag)
            if iv is None:
                continue
            records.append({
                "ref": ref, "mapq": int(mapq_text), "flag": flag,
                "qstart": iv[0], "qend": iv[1], "rstart": iv[2], "rend": iv[3],
            })
    backbones = [r for r in records if r["ref"] == "pGP564"]
    inserts = [r for r in records if r["ref"] != "pGP564"]
    rows = []
    for backbone in backbones:
        for insert in inserts:
            gap = signed_gap(backbone["qstart"], backbone["qend"], insert["qstart"], insert["qend"])
            rows.append([
                read_id, read_len,
                f"{backbone['qstart']}_{backbone['qend']}",
                f"{backbone['rstart']}_{backbone['rend']}",
                f"{insert['qstart']}_{insert['qend']}",
                insert["ref"],
                f"{insert['rstart']}_{insert['rend']}",
                reference_lengths[insert["ref"]],
                max(0, gap),
                "+" if gap > 0 else str(gap),
                backbone["mapq"], insert["mapq"],
            ])
    headers = [
        "read_id", "read_length", "read_on_backbone", "backbone_on_reference",
        "read_on_insert", "insert_name", "insert_on_reference", "insert_length",
        "gap_length", "gap_length_signed", "backbone_mapq", "insert_mapq",
    ]
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "All insert hits"
    sheet.append(headers)
    for row in rows:
        sheet.append(row)
    for cell in sheet[1]:
        cell.font = Font(bold=True)
    sheet.freeze_panes = "A2"
    sheet.auto_filter.ref = sheet.dimensions
    for col, width in {"A": 38, "B": 14, "C": 20, "D": 25, "E": 20, "F": 22, "G": 25, "H": 14, "I": 12, "J": 18, "K": 14, "L": 12}.items():
        sheet.column_dimensions[col].width = width
    workbook.save(output_path)
    print(f"read_id\t{read_id}")
    print(f"all_alignments\t{len(records)}")
    print(f"insert_hits\t{len(inserts)}")
    print(f"output_rows\t{len(rows)}")


if __name__ == "__main__":
    main()
