#!/usr/bin/env python3
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--records", type=int, required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    written = 0
    bases = 0
    with open(args.output, "w", encoding="ascii", newline="") as out:
        while written < args.records:
            record = [__import__("sys").stdin.readline() for _ in range(4)]
            if not record[0]:
                break
            if any(line == "" for line in record):
                raise RuntimeError("Truncated FASTQ record")
            if not record[0].startswith("@") or not record[2].startswith("+"):
                raise RuntimeError("Invalid FASTQ record")
            sequence = record[1].strip()
            quality = record[3].rstrip("\r\n")
            if len(sequence) != len(quality):
                raise RuntimeError("FASTQ sequence/quality length mismatch")
            out.writelines(record)
            written += 1
            bases += len(sequence)

    if written != args.records:
        raise RuntimeError("Input contains fewer records than requested")
    print("records_written\t{}".format(written))
    print("bases_written\t{}".format(bases))


if __name__ == "__main__":
    main()
