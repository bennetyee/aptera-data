#!/usr/bin/python3

# Program to (1) take CSV output of all investments in
# REG,daynum,cents format and output daynum,total-so-far format, (2)
# generate a investment vs time graph, and (3) generate an animation
# of investments with bar charts of the number (or amount) of
# investments at different price ranges, evolving over time.  For the
# animation, each frame is one day.  This program will generate a
# series of daily graphs and `ffmpeg` is used to generate the
# animation from them.

import argparse
import csv
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import os
import subprocess
import sys
import tempfile
from typing import List, Optional, Tuple

options: Optional[argparse.Namespace] = None

REGA='aptera-rega'
REGD='aptera-regd'

BAR_COLOR = {'aptera-rega': 'blue', 'aptera-regd': 'green'}

class CSVDataError(Exception):
    def __init__(self, message='CSV data error'):
        self.message = message
        super().__init__(self.message)

def read_investment_data(fn: str) -> List[Tuple[str, int, int]]:
    assert options is not None
    results=[]
    line = 0
    with open(fn, 'r', newline='') as infile:
        rcsv = csv.reader(infile, skipinitialspace=True)
        for row in rcsv:
            line += 1
            if options.verbose > 1:
                print(repr(row))
            if len(row) != 3:
                raise CSVDataError(f'File {fn}, line {line}: format error: should be 3 fields, got: {','.join(row)}\n')
            if row[0] != REGA and row[0] != REGD:
                raise CSVDataError(f'File {fn}, line {line}: first column should be {REGA} or {REGD}, got {row[0]} instead')
            try:
                daynum = int(row[1])
            except ValueError:
                raise CSVDataError(f'File {fn}, line {line}: second column should be the day number; got {row[1]} instead')
            if daynum < 0:
                raise CSVDataError(f'File {fn}, line {line}: negative day number? ({row[1]})')
            try:
                cents = int(row[2])
            except ValueError:
                raise CSVDataError(f'File {fn}, line {line}: third column should be the investment amount, in cents; got {row[2]} instead')
            if cents < 0:
                raise CSVDataError(f'File {fn}, line {line}: negative investment amount ({cents})?')
            results.append((row[0], daynum, cents))
    return results

def output_data(fn: str, dailies: List[int]) -> None:
    with open(fn, 'w', newline='') as outfile:
        wcsv = csv.writer(outfile)
        for i in range(len(dailies)):
            wcsv.writerow([i, dailies[i]])

def output_investment_vs_time_plot(fn: str, dailies: List[int]) -> None:
    assert options is not None
    xs = np.array([ i for i in range(len(dailies))])
    ys = np.array([d / 100.0 for d in dailies])
    # figsize in inches, default 100dp, so 1024x768
    _fig, ax = plt.subplots(figsize=(10.24, 7.68))
    color = 'blue'
    ax.plot(xs,ys, color=color)
    ax.set_xlabel('days since start of PD program')
    ax.set_ylabel('investments', color=color)
    ax.get_yaxis().set_major_formatter(
        matplotlib.ticker.FuncFormatter(lambda x,p: format(int(x), ',')))
    ax2 = ax.twinx()
    color = 'red'
    y2 = [0] * len(ys)
    y2[0] = ys[0]
    for ix in range(1, len(ys)):
        y2[ix] = y2[ix-1] + ys[ix]
    ax2.plot(xs,y2, color=color)
    ax2.set_ylabel('cumulative amount', color=color)
    ax2.get_yaxis().set_major_formatter(
        matplotlib.ticker.FuncFormatter(lambda x,p: format(int(x), ',')))
    plt.title('Coupon Round / Priority Delivery Investments')
    plt.tight_layout(pad = 1.5)
    plt.savefig(fn)

def output_investment_distribution_animation(fn: str, min_b: int, max_b: Optional[int], width: int, regatop: bool, values: bool, cumulative: bool, dps: int, data: List[Tuple[str, int, int]]) -> None:
    if max_b is None:
        # scan for max investment
        max_b = -1
        for _, _, amt in data:
            if amt > max_b:
                max_b = amt
    num_buckets = (max_b - min_b + width - 1) // width
    if options.verbose:
        print(f'max_b {max_b}, min_b {min_b}, width {width}, num_buckets {num_buckets}')
    max_b_ignore = min_b + width * num_buckets
    if options.verbose:
        print(f'max_b_ignore {max_b_ignore}')
    data.sort(key=lambda t: t[1])
    max_d = data[-1][1]
    if options.verbose:
        print(f'max day {max_d}')
    if regatop:
        selector = [REGA, REGD]
    else:
        selector = [REGD, REGA]
    # buckets is a num_buckets array of either investment counts or
    # investment dollars.
    # there are two sets of buckets per day, by selector.
    # bucketset = []
    # for d in range(max_d+1):
    #     ds = []
    #     for s in range(len(selector)):
    #         bs = [0] * num_buckets
    #         ds.append(bs)
    #     bucketset.append(ds)
    bucketset = [[[0] * num_buckets for _1 in range(len(selector))] for _2 in range(max_d+1)]
    for sel, d, amt in data:
        if options.verbose > 2:
            print(f'{sel}, {d}, {amt}')
        if amt < min_b or amt >= max_b_ignore:
            if options.verbose > 2:
                print('ignoring')
            continue
        selix = selector.index(sel)
        bucketix = (amt - min_b) // width
        if options.verbose > 2:
            print(f' [{d}][{selix}][{bucketix}]')
        if values:
            bucketset[d][selix][bucketix] += amt
        else:
            bucketset[d][selix][bucketix] += 1
    if options.verbose > 3:
        print(f'bucketset {bucketset}')
    if cumulative:
        for d in range(1, max_d+1):
            for s in range(len(selector)):
                for b in range(num_buckets):
                    bucketset[d][s][b] += bucketset[d-1][s][b]
        if options.verbose > 3:
            print(f'cumulative bucketset {bucketset}')
    max_height = 0
    for d in range(max_d + 1):
        for bucketix in range(num_buckets):
            total_height = sum(bucketset[d][selix][bucketix] for selix in range(len(selector)))
            if total_height > max_height:
                max_height = total_height
    xs = np.array([ f'{i}' for i in range(num_buckets) ])
    bar_width = 0.8
    with tempfile.TemporaryDirectory() as dir:
        for d in range(max_d + 1):
            fig, ax = plt.subplots(figsize=(20.48, 15.36))
            frame_fn = os.path.join(dir, f'frame_{d}.png')
            if options.verbose:
                print(f'frame_fn {frame_fn}')
            bottoms = np.zeros(num_buckets)
            for selix in range(len(selector)):
                ys = np.array(bucketset[d][selix])
                if values:
                    ys = ys / 100.0
                color = BAR_COLOR[selector[selix]]
                p = ax.bar(xs, ys, width=bar_width, label=selector[selix],
                           bottom=bottoms)
                bottoms += ys
                ax.bar_label(p, label_type='center')
            ax.set_title(f'Aptera Coupon/PD Investments, day {d}')
            if values:
                ymax = max_height/100
                ax.set_ylabel(f'Investment (dollars)')
            else:
                ymax = max_height
                ax.set_ylabel(f'Number of Investments')
            ax.set_ylim(0, ymax)
            ax.legend()
            ax.set_xlabel(f'Bucket 0 min value \\${min_b/100.0:.2f}, bucket width \\${width/100.0:.2f}')
            ax.tick_params(axis='x', labelrotation=90)
            plt.savefig(frame_fn)
            plt.close(fig)
        # generate animation
        subprocess.run(['rm', '-f', fn])
        subprocess.run(['ffmpeg', '-framerate', str(dps),
                        '-i', os.path.join(dir, 'frame_%d.png'),
                        '-start_number', '0', '-r', '30',
                        fn])

def main(argv: List[str]) -> int:
    global options
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose', '-v', action='count',
                        default=0,
                        help='increment verbosity level')
    parser.add_argument('--input', '-i', type=str, default='/dev/stdin',
                        help='input file')

    parser.add_argument('--output', '-o', type=str, default=None,
                        help='output file')

    parser.add_argument('--plot-output', '-p', type=str, default=None,
                        help='investment-vs time plot output file')

    parser.add_argument('--animation-output', '-a', type=str, default=None,
                        help='investment distribution over time animation output file')
    parser.add_argument('--cumulative-buckets', type=bool, default=True,
                        action=argparse.BooleanOptionalAction,
                        help='animation buckets show cumulative values')
    parser.add_argument('--bucket-height-values', type=bool, default=True,
                        action=argparse.BooleanOptionalAction,
                        help='buckets show number of investments or investment amount in that range')
    parser.add_argument('--min-bucket', '-m', type=int, default=1_000 * 100,
                        help='first bucket value (cents); investments below will be ignored')
    parser.add_argument('--max-bucket', '-M', type=int, default=None,
                        help='last bucket contains the max-bucket value (cents); investments above the bucket threshold will be ignored')
    parser.add_argument('--bucket-width', '-b', type=int, default=5_000 * 100,
                        help='investment distribution bucket width, in cents')
    parser.add_argument('--rega-above-regd', type=bool, default=False,
                        action=argparse.BooleanOptionalAction,
                        help='Reg-A investment go above Reg-D investments')
    parser.add_argument('--days-per-second', type=int, default=4,
                        help='animation rate')

    # When max_bucket is None means figure out max investment value
    # and that's in the last bucket.
    # 
    # Otherwise last bucket is one where min_bucket + k bucket_width
    # <= max_bucket < min_bucket + (k+1) bucket_width for some integer
    # k.
    options = parser.parse_args(argv[1:])

    if options.min_bucket < 0:
        sys.stderr.write(f'buckets are investment dollar amounts and should not be negative\n')
        return 1
    if options.max_bucket is not None and options.min_bucket >= options.max_bucket:
        sys.stderr.write(f'min-bucket value {options.min_bucket} should be less than max_bucket value {options.max_bucket}\n')
        return 1
    if options.bucket_width <= 0:
        sys.stderr.write(f'bucket-width value {options.bucket_width} should be positive\n')
        return 1
    if options.days_per_second <= 0:
        sys.stderr.write(f'days-per-second value {options.days_per_second} should be positive\n')
        return 1

    if options.output is None and options.plot_output is None and options.animation_output is None:
        sys.stderr.write(f'at least one of --output or --plot-output should be chose; assuming --output /dev/stdout\n')
        options.output = '/dev/stdout'

    try:
        data = read_investment_data(options.input)
    except CSVDataError as e:
        sys.stderr.write(f'CSV data format error: {e}\n')
        return 1
    max_day = 0
    for _, day, _ in data:
        if max_day < day:
            max_day = day
    dailies = [0] * (max_day + 1)
    for _, day, cents in data:
        dailies[day] += cents
    if options.output is not None:
        output_data(options.output, dailies)
    if options.plot_output is not None:
        output_investment_vs_time_plot(options.plot_output, dailies)
    if options.animation_output is not None:
        output_investment_distribution_animation(options.animation_output, options.min_bucket, options.max_bucket, options.bucket_width, options.rega_above_regd, options.bucket_height_values, options.cumulative_buckets, options.days_per_second, data)
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
