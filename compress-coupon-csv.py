#!/usr/bin/python3
import argparse
import csv
import sys
from typing import Optional

options: Optional[argparse.Namespace] = None

def main(argv: list[str]) -> int:
    global options
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose', '-v', action='count',
                        default=0,
                        help='increment the verbosity level by 1')
    parser.add_argument('--dollar', '-d', type=bool, default=False,
                        action=argparse.BooleanOptionalAction,
                        help='input includes total dollar amount and average investment amount')
    parser.add_argument('infile', type=str, help='input file')
    parser.add_argument('outfile', type=str, help='output file')
    options = parser.parse_args(argv[1:])

    last_value = -1
    if options.dollar:
        count_column = 2
        expected_columns = 4
    else:
        count_column = 1
        expected_columns = 2
    with open(options.infile, 'r', newline='') as infile:
        rcsv = csv.reader(infile, skipinitialspace=True)
        with open(options.outfile, 'w', newline='') as outfile:
            wcsv = csv.writer(outfile)
            linenum = 0
            for row in rcsv:
                linenum += 1
                if options.verbose:
                    print(repr(row))
                if len(row) != expected_columns:
                    sys.stderr.write(f'compress-coupon-csv: Malformed input on line {linenum}: {len(row)} entries\n')
                    return 1
                count = int(row[count_column])
                if count != last_value:
                    wcsv.writerow(row)
                    last_value = count
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
