#!/usr/bin/python3

import argparse
import os
import re
import sys

import aptera_csv

options=None

def get_accelerator_investment(fn):
    t = aptera_csv.read_csv_file(fn)
    return sum(r[aptera_csv.ACCELERATOR_INVESTMENT] for r in t)

def get_trend(dir):
    # google sheets does not like zone offset
    name_re = r'data\.(.*)[+-]\d\d:\d\d\.csv'
    nfa = re.compile(name_re)
    time_amount=[]
    for f in os.listdir(dir):
        if options.verbose > 1:
            sys.stderr.write(f'file {f}\n')
        m = nfa.match(f)
        if m is None:
            continue
        timestamp = m.group(1)
        if options.verbose > 0:
            sys.stderr.write(f'Matched: {timestamp}\n')
        investment = get_accelerator_investment(os.path.join(dir,f))
        time_amount.append([timestamp, investment])
    # ISO-8601 timestamps don't need parsing to sort
    time_amount.sort(key=lambda t: t[0])
    return time_amount

def generate_trend_csv(dir, ostr=sys.stdout):
    data = get_trend(dir)
    for ts, amt in data:
        ostr.write(f'"{ts.replace("T"," ")}", {amt}\n')

def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', '-d', type=str, default='history',
                        help='directory containing CSV data in timestamp named files')
    parser.add_argument('--output', '-o', type=str, default=None,
                        help='output file for CSV trend data')
    parser.add_argument('--verbose', '-v', action='count',
                        default=0,
                        help='increment the verbosity level by 1')
    global options
    options = parser.parse_args(argv[1:])
    if options.output is not None:
        with open(options.output, 'w') as ostr:
            generate_trend_csv(options.dir, ostr)
    else:
        generate_trend_csv(options.dir)


if __name__ == '__main__':
    sys.exit(main(sys.argv))

    
