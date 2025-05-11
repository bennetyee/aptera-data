#!/usr/bin/python3

import argparse
import csv
import json
import os
import sys
from typing import Any, Dict

import cache
import extract_investments
import issuance

options: None | argparse.Namespace = None

def main(argv: list[str]) -> int:
    global options
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose', '-v', action='count',
                        default=0,
                        help='increment the verbosity level by 1')
    parser.add_argument('--cache', type=bool, default=True,
                        action=argparse.BooleanOptionalAction,
                        help='use a cache to reduce number of hits on the issuance web endpoint')
    parser.add_argument('--save-cache', type=str, default='',
                        help='save web API query cache contents to this file prior before quitting')
    parser.add_argument('--load-cache', type=str, default='',
                        help='pre-load query cache from this file')
    parser.add_argument('--show-cache-progress', type=int, default=0,
                        help='print indicator for every this many cache hits (.) and misses (,) (0 to disable)')
    parser.add_argument('--output-format', type=str, choices=['json', 'old', 'csv'],
                        default='old',
                        help='output style')

    options = parser.parse_args(argv[1:])

    if (options.save_cache != '' or options.load_cache != '') and not options.cache:
        sys.stderr.write(f'Without --cache option, neither --load-cache nor --save-cache makes sense\n')
        return 1

    issuance.verbose = options.verbose
    extract_investments.verbose = options.verbose
    # need a way to register all imported modules to automatically set
    # their verbosity, if they sign up for it.

    today = issuance.today_day_number()

    investments_json: Dict[str, Any] = dict()

    for slug in ['aptera-rega', 'aptera-regd']:
        data_src = issuance.IssuanceInvestmentData(slug)

        qf = data_src
        if options.cache:
            qf.enable_cache()
            qf.set_progress_period(options.show_cache_progress)

            if options.load_cache != '':
                cache_file = f'{options.load_cache}-{slug}'
                if os.path.isfile(cache_file):
                    with open(cache_file) as istr:
                        qf.set_cache(eval(istr.read()))  # potentially unsafe!
                    if options.verbose:
                        sys.stderr.write(f'Cache {cache_file} loaded.\n')
                else:
                    sys.stderr.write(f'Error: cache file {cache_file} does not exist.\n')
                    # we don't quit because we may have a cache file for one
                    # slug but not the other
    
        extractor = extract_investments.ExtractInvestment(
            qf,
            today + 1,
            0, 10_000_000 * 100)

        investments = extractor.extract_investments()
        if options.output_format == 'old':
            sys.stdout.write(f'investments[\'{slug}\'] = {investments}\n')
        elif options.output_format == 'json' or options.output_format == 'csv':
            investments_json[slug] = investments
        if options.save_cache != '':
            cache_file = f'{options.save_cache}-{slug}'
            with open(cache_file, 'w') as ostr:
                ostr.write(repr(qf.cache()))
            if options.verbose:
                sys.stderr.write(f'Cache {cache_file} written.\n')
    if options.output_format == 'json':
        sys.stdout.write(json.dumps(investments_json))
    elif options.output_format == 'csv':
        # no data should contain newlines, so newline='' vs None
        # should not be an issue
        for slug in investments_json.keys():
            out = csv.writer(sys.stdout)
            for day, amt in investments_json[slug]:
                out.writerow([slug, day, amt])
    sys.stdout.flush()
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
