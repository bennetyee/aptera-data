#!/usr/bin/python3

# take CSV output of all investments in REG,daynum,cents format and output
# daynum,total-so-far format

import argparse
import csv
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

def main(argv: List[str]) -> int:
    global options
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose', '-v', action='count',
                        default=0,
                        help='increment verbosity level')
    parser.add_argument('--input', '-i', type=str, default='/dev/stdin',
                        help='input file')
    parser.add_argument('--output', '-o', type=str, default='/dev/stdout',
                        help='output file')
    options = parser.parse_args(argv[1:])
    data = read_investment_data(options.input)
    max_day = 0
    for _, day, _ in data:
        if max_day < day:
            max_day = day
    dailies = [0] * (max_day + 1)
    for _, day, cents in data:
        dailies[day] += cents
    output_data(options.output, dailies)
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
