#!/usr/bin/python3

import argparse
import datetime
import json
import requests
import sys

from typing import Any, Dict, Generator, Tuple

import issuance

options: Any = None  # argparse.Namespace

priority_slots_available = 1_000

def main(argv: list[str]) -> int:
    global options
    parser = argparse.ArgumentParser()
    parser.add_argument('--csv', type=bool, default=False,
                        action=argparse.BooleanOptionalAction,
                        help='output CSV separated values instead of human-readable data')
    # timestamp string and numbers, and CSV quoting is needed only for
    # amounts with thousand separators (e.g., dollar figures)
    parser.add_argument('--timestamp', '-t', type=bool, default=True,
                        action=argparse.BooleanOptionalAction,
                        help='output a timestamp with the committed count')
    parser.add_argument('--remaining', type=bool, default=False,
                        action=argparse.BooleanOptionalAction,
                        help='output priority slots remaining rather than number of qualifying commitments')
    parser.add_argument('--total-slots', type=int,
                        default=priority_slots_available,
                        help='change the number of priority slots available')
    parser.add_argument('--dollar', '-d', type=bool, default=False,
                        action=argparse.BooleanOptionalAction,
                        help='print total dollar amount committed')
    parser.add_argument('--priority-only', type=bool, default=True,
                        action=argparse.BooleanOptionalAction,
                        help='only count number of commitments that qualify for priority delivery')
    parser.add_argument('--average-investment', type=bool, default=False,
                        action=argparse.BooleanOptionalAction,
                        help='print average investment amount for current investment category selected')
    parser.add_argument('--verbose', '-v', action='count',
                        default=0,
                        help='increment the verbosity level by 1')
    options = parser.parse_args(argv[1:])

    issuance.verbose = options.verbose

    if not options.priority_only and options.remaining:
        print('Counting non-priority commitments and printing slots remaining are incompatible options', file=sys.stderr)
        return 1

    if options.timestamp:
        ts = f'{datetime.datetime.now().isoformat()}'
    else:
        ts = ''

    try:
        if options.priority_only:
            investment_threshold = 5000 * 100
        else:
            investment_threshold = None
        sums = issuance.total_committed_amount_and_count_at_threshold(investment_threshold)
    except IOError:
        print('Error while fetching data', file=sys.stderr)
        return 1
    slots = sums[1]

    if options.remaining:
        slots = options.total_slots - slots

    output_control = [
        [ options.timestamp,
          '',
          lambda : f'{datetime.datetime.now().isoformat()}' ],
        [ options.dollar,
          'dollar total: ',
          lambda: f'${sums[0]:,.2f}' ],
        [ True,
          'slots: ',
          lambda: f'{slots:d}' ],
        [ options.average_investment,
          'average: ',
          lambda: f'${sums[0]/sums[1]:,.2f}' ],
    ]

    def comma_quote(v: str) -> str:
        if ',' in v:
            return f'"{v}"'
        else:
            return v

    def sepgen_csv() -> Generator[str, None, None]:
        yield ''
        while True:
            yield ', '

    def sepgen_human() -> Generator[str, None, None]:
        yield ''
        if options.timestamp:
            yield ' '
        while True:
            yield ', '

    if options.csv:
        sep = sepgen_csv()
    else:
        sep = sepgen_human()

    for (p, l, vf) in output_control:
        if p:
            if options.csv:
                sys.stdout.write(next(sep))
                sys.stdout.write(comma_quote(vf()))
            else:
                sys.stdout.write(next(sep))
                sys.stdout.write(l)
                sys.stdout.write(vf())

    sys.stdout.write('\n')
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
