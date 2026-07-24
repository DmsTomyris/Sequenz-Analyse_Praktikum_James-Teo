from pathlib import Path
import re

ROOT = Path(r"C:\Users\teohe\OneDrive\Desktop\.AAAA-Praktikum\Day2\plasmid_assembly_workflow")
READ_ID = "7b83c260-caec-4224-9e60-bc5b095cf207"
FASTQ = ROOT / "read_7b83c260.fastq"
REFERENCE = ROOT / "targeted_reference.fa"
OUT = ROOT / "read_7b83c260_direct_alignment.md"

COMP = str.maketrans("ACGTNacgtn", "TGCANtgcan")


def read_fastq(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    return lines[1].strip()


def read_fasta(path):
    records = {}
    name = None
    parts = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith(">"):
            if name is not None:
                records[name] = "".join(parts)
            name = line[1:].split()[0]
            parts = []
        elif line.strip():
            parts.append(line.strip())
    if name is not None:
        records[name] = "".join(parts)
    return records


def parse_cigar(cigar):
    return [(int(n), op) for n, op in re.findall(r"(\d+)([MIDNSHP=X])", cigar)]


def reconstruct(query, reference, ref_start_1based, cigar):
    q = 0
    r = ref_start_1based - 1
    aligned_q = []
    aligned_r = []
    for n, op in parse_cigar(cigar):
        if op in "M=X":
            aligned_q.extend(query[q:q+n])
            aligned_r.extend(reference[r:r+n])
            q += n
            r += n
        elif op == "I":
            aligned_q.extend(query[q:q+n])
            aligned_r.extend("-" * n)
            q += n
        elif op in "DN":
            aligned_q.extend("-" * n)
            aligned_r.extend(reference[r:r+n])
            r += n
        elif op in "SH":
            q += n if op == "S" else 0
        else:
            raise ValueError(f"Unsupported CIGAR operation: {op}")
    return "".join(aligned_q), "".join(aligned_r)


def marker(query, reference):
    out = []
    for q, r in zip(query, reference):
        if q == r and q != "-":
            out.append("|")
        elif q == "-":
            out.append("-")
        elif r == "-":
            out.append("+")
        else:
            out.append(".")
    return "".join(out)


def wrapped(label, value, width=80):
    lines = []
    for i in range(0, len(value), width):
        lines.append(f"{label:<12}{value[i:i+width]}")
    return "\n".join(lines)


def one_line(label, value):
    return f"{label:<12}{value}"


read_original = read_fastq(FASTQ)
read_mapper_orientation = read_original.translate(COMP)[::-1]
refs = read_fasta(REFERENCE)

backbone_cigar = "9S42M1I26M1D3M3I1M1I121M1I125M3D25M1I4M1D149M1D12M1D170M1I76M310S"
insert_cigar = "771H213M97H"

bq = read_mapper_orientation[9:771]
br = refs["pGP564"]
bq, br = reconstruct(bq, br, 2517, backbone_cigar.replace("9S", "").replace("310S", ""))

iq = read_mapper_orientation[771:984]
ir = refs["YGPM-22o22"]
iq, ir = reconstruct(iq, ir, 4629, insert_cigar.replace("771H", "").replace("97H", ""))

lines = [
    f"# Direkte Alignmentdarstellung: {READ_ID}",
    "",
    "Die Read-Sequenz wird in Minimap2-Orientierung dargestellt, also als Reverse-Komplement der FASTQ-Sequenz, weil beide Alignments FLAG 16 tragen.",
    "`|` = identische Base, `.` = Mismatch, `+` = Read-Insertion, `-` = Referenz-Deletion.",
    "",
    "## 1. Backbone-Abschnitt",
    "",
    "Read-Orientierung: Query 10–771; pGP564:2517–3277; MAPQ 60; NM 24",
    "",
    wrapped("READ_RC", bq),
    wrapped("MATCH", marker(bq, br)),
    wrapped("BACKBONE", br),
    "",
    "## 2. Insert-Abschnitt",
    "",
    "Read-Orientierung: Query 772–984; YGPM-22o22:4629–4841; MAPQ 56; NM 0",
    "",
    wrapped("READ_RC", iq),
    wrapped("MATCH", marker(iq, ir)),
    wrapped("INSERT", ir),
    "",
    "## 3. Gemeinsame dreizeilige Junction-Ansicht",
    "",
    "Hier stehen Read, Backbone-Referenz und Insert-Referenz in einer gemeinsamen Query-Spalte. `-` bedeutet: Diese Referenz ist in diesem Abschnitt nicht die passende Referenz.",
    "",
    one_line("READ_RC", bq + iq),
    one_line("BACKBONE", br + "-" * len(iq)),
    one_line("INSERT", "-" * len(bq) + ir),
    "",
    "## Junction-Zusammenfassung",
    "",
    "Query 771 ist die letzte Backbone-Base; Query 772 ist die erste Insert-Base. Daher beträgt der Übergangsspalt 0 bp.",
    "Die 9 bp vor dem Backbone-Alignment und 97 bp nach dem Insert-Alignment sind nicht ausgerichtet.",
]
OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(OUT)
