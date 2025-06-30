#!/usr/bin/python3

# take CSV output of all investments in REG,daynum,cents format and output
# daynum,total-so-far format

import argparse
import csv
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import sys
from typing import List, Optional, Tuple

options: Optional[argparse.Namespace] = None

def read_investment_data(fn: str) -> List[Tuple[str, int, int]]:
    assert options is not None
    results=[]
    line = 0
    with open(fn, 'r', newline='') as infile:
        rcsv = csv.reader(infile, skipinitialspace=True)
        for row in rcsv:
            line += 1
            if options.verbose:
                print(repr(row))
            if len(row) != 3:
                sys.stderr.write(f'File {fn}, line {line}: format error: should be 3 fields, got: {','.join(row)}\n')
                sys.exit(1)
            results.append((row[0], int(row[1]), int(row[2])))
    return results

def output_data(fn: str, dailies: List[int]) -> None:
    with open(fn, 'w', newline='') as outfile:
        wcsv = csv.writer(outfile)
        for i in range(len(dailies)):
            wcsv.writerow([i, dailies[i]])

def output_plot(fn: str, dailies: List[int]) -> None:
    xs = np.array([ i for i in range(len(dailies))])
    ys = np.array([d / 100.0 for d in dailies])
    # figsize in inches, default 100dp, so 1024x768
    plot, ax = plt.subplots(figsize=(10.24, 7.68))
    color = 'tab:blue'
    ax.plot(xs,ys, color=color)
    ax.set_xlabel('days since start of PD program')
    ax.set_ylabel('investments', color=color)
    ax.get_yaxis().set_major_formatter(
        matplotlib.ticker.FuncFormatter(lambda x,p: format(int(x), ',')))
    ax2 = ax.twinx()
    color = 'tab:red'
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
                        help='plot output file')
    options = parser.parse_args(argv[1:])

    if options.output is None and options.plot_output is None:
        sys.stderr.write(f'at least one of --output or --plot-output should be chose; assuming --output /dev/stdout\n')
        options.output = '/dev/stdout'

    data = read_investment_data(options.input)
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
        output_plot(options.plot_output, dailies)
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
