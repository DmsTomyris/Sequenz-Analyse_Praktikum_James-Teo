#!/usr/bin/env python3
import csv
import re
import sys
from pathlib import Path

from openpyxl import Workbook


FIELDS = [
    "read_id", "read_length", "read_on_backbone", "backbone_on_reference",
    "read_on_insert", "insert_name", "insert_on_reference", "insert_length",
    "gap_length", "gap_length_signed", "backbone_mapq", "insert_mapq",
]


def numbers(value):
    return [int(x) for x in re.findall(r"\d+", value)]


def group(row):
    coords = numbers(row["backbone_on_reference"])
    near = any(abs(coord - 5042) <= 10 for coord in coords)
    if near:
        return "near_5042"
    if int(row["gap_length"]) == 0:
        return "gap0_far"
    return "remaining"


def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage: make_day2_style_excel.py INPUT.tsv OUTPUT.xlsx")
    input_path, output_path = map(Path, sys.argv[1:])
    rows = []
    with input_path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            rows.append(row)

    wb = Workbook()
    wb.remove(wb.active)
    grouped = {name: [] for name in ("near_5042", "gap0_far", "remaining")}
    for row in rows:
        grouped[group(row)].append(row)
    for name in grouped:
        ws = wb.create_sheet(name)
        ws.append(FIELDS)
        for row in grouped[name]:
            ws.append([row[field] for field in FIELDS])
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions

    wb.save(output_path)
    print("near_5042\t{}".format(len(grouped["near_5042"])))
    print("gap0_far\t{}".format(len(grouped["gap0_far"])))
    print("remaining\t{}".format(len(grouped["remaining"])))
    print("total\t{}".format(len(rows)))


if __name__ == "__main__":
    main()
