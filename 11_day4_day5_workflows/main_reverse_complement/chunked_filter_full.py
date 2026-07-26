#!/usr/bin/env python3
import argparse
import math
import os
import time

parser = argparse.ArgumentParser()
parser.add_argument('--input', required=True)
parser.add_argument('--output-dir', required=True)
parser.add_argument('--block-size', type=int, default=1000)
args = parser.parse_args()

root = args.output_dir
raw_dir = os.path.join(root, 'raw_blocks')
filtered_dir = os.path.join(root, 'filtered_blocks')
os.makedirs(raw_dir)
os.makedirs(filtered_dir)
progress_path = os.path.join(root, 'progress.tsv')
stats = []
total_bases = 0
records_in_block = 0
block_index = 0
block_handle = None
start = time.time()

def write_progress(stage, records, blocks):
    with open(progress_path, 'w') as out:
        out.write('stage\t{}\n'.format(stage))
        out.write('records_seen\t{}\n'.format(records))
        out.write('blocks_saved\t{}\n'.format(blocks))
        out.write('elapsed_seconds\t{:.1f}\n'.format(time.time() - start))

with open(args.input) as src:
    record_index = 0
    while True:
        rec = [src.readline() for _ in range(4)]
        if not rec[0]:
            break
        if len(rec) != 4 or any(not x for x in rec):
            raise ValueError('truncated FASTQ at record {}'.format(record_index + 1))
        if block_handle is None:
            block_handle = open(os.path.join(raw_dir, 'block_{:06d}.fastq'.format(block_index)), 'w')
        block_handle.writelines(rec)
        seq = rec[1].rstrip('\n')
        qual = rec[3].rstrip('\n')
        if len(seq) != len(qual):
            raise ValueError('sequence/quality length mismatch at record {}'.format(record_index + 1))
        mean_q = sum(ord(char) - 33 for char in qual) / float(len(qual)) if qual else 0.0
        stats.append((len(seq), mean_q, record_index, block_index))
        total_bases += len(seq)
        record_index += 1
        records_in_block += 1
        if records_in_block == args.block_size:
            block_handle.close()
            block_handle = None
            block_index += 1
            records_in_block = 0
            write_progress('saving_raw_blocks', record_index, block_index)
if block_handle is not None:
    block_handle.close()
    block_index += 1
write_progress('raw_blocks_complete', record_index, block_index)

remove_long_n = int(math.ceil(len(stats) * 0.10))
remove_long = set(item[2] for item in sorted(stats, key=lambda item: (-item[0], item[2]))[:remove_long_n])
remaining = [item for item in stats if item[2] not in remove_long]
remove_low_q_n = int(math.floor(len(remaining) * 0.50))
remove_low_q = set(item[2] for item in sorted(remaining, key=lambda item: (item[1], item[2]))[:remove_low_q_n])
keep = set(item[2] for item in remaining if item[2] not in remove_low_q)

filtered_records = 0
filtered_bases = 0
for b in range(block_index):
    src_path = os.path.join(raw_dir, 'block_{:06d}.fastq'.format(b))
    dst_path = os.path.join(filtered_dir, 'block_{:06d}.fastq'.format(b))
    with open(src_path) as src, open(dst_path, 'w') as dst:
        for offset in range(args.block_size):
            rec = [src.readline() for _ in range(4)]
            if not rec[0]:
                break
            global_index = b * args.block_size + offset
            if global_index in keep:
                dst.writelines(rec)
                filtered_records += 1
                filtered_bases += len(rec[1].rstrip('\n'))
    write_progress('filtering_blocks', min((b + 1) * args.block_size, record_index), b + 1)

with open(os.path.join(root, 'filter_stats.tsv'), 'w') as out:
    out.write('input_records\t{}\n'.format(len(stats)))
    out.write('input_bases\t{}\n'.format(total_bases))
    out.write('removed_longest_records\t{}\n'.format(len(remove_long)))
    out.write('removed_lowest_q_records\t{}\n'.format(len(remove_low_q)))
    out.write('kept_records\t{}\n'.format(len(keep)))
    out.write('kept_bases\t{}\n'.format(filtered_bases))
    out.write('length_rule\tremove longest 10 percent\n')
    out.write('quality_rule\tremove lowest 50 percent of remaining by mean Phred score\n')
write_progress('complete', record_index, block_index)
