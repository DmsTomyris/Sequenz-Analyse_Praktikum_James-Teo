#!/usr/bin/env python3
import sys


def main():
    records = 0
    total_bases = 0
    while True:
        header = sys.stdin.buffer.readline()
        if not header:
            break
        sequence = sys.stdin.buffer.readline()
        plus = sys.stdin.buffer.readline()
        quality = sys.stdin.buffer.readline()
        if not sequence or not plus or not quality:
            raise ValueError("Truncated FASTQ record")
        if not header.startswith(b"@"):
            raise ValueError("FASTQ header does not start with @")
        if not plus.startswith(b"+"):
            raise ValueError("FASTQ separator does not start with +")
        sequence = sequence.rstrip(b"\r\n")
        quality = quality.rstrip(b"\r\n")
        if len(sequence) != len(quality):
            raise ValueError("Sequence and quality lengths differ")
        records += 1
        total_bases += len(sequence)
    print("status\tPASS")
    print("fastq_records\t{}".format(records))
    print("fastq_bases\t{}".format(total_bases))


if __name__ == "__main__":
    main()
