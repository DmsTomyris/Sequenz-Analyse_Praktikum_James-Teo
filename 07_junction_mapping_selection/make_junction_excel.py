#!/usr/bin/env python3
import csv
import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font


def main():
    if len(sys.argv) != 3:
        raise SystemExit(f"usage: {sys.argv[0]} INPUT.tsv OUTPUT.xlsx")
    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    with input_path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.reader(handle, delimiter="\t"))
    numeric_columns = {"read_length", "insert_length", "gap_length", "backbone_mapq", "insert_mapq"}
    for row in rows[1:]:
        for index, header in enumerate(rows[0]):
            if header in numeric_columns:
                row[index] = int(row[index])
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Junction mappings"
    for row in rows:
        sheet.append(row)
    for cell in sheet[1]:
        cell.font = Font(bold=True)
    sheet.freeze_panes = "A2"
    sheet.auto_filter.ref = sheet.dimensions
    widths = {1: 38, 2: 14, 3: 20, 4: 25, 5: 18, 6: 22, 7: 25, 8: 14, 9: 12, 10: 18, 11: 14, 12: 12}
    for column, width in widths.items():
        sheet.column_dimensions[chr(64 + column)].width = width
    workbook.save(output_path)
    print(f"wrote {output_path} ({len(rows) - 1} data rows)")


if __name__ == "__main__":
    main()
