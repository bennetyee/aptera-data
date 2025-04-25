#!/usr/bin/python3

import argparse
import datetime
import json
import requests
import sys

options = None

issuance_url = 'https://api.issuance.com/api/investments/summary/'
issuance_params = {
    'processed_at__date__gte': '2025-04-10',
}

priority_slots_available = 1_000

def make_params(priority_only):
    plist = []
    for reg in ['aptera-rega', 'aptera-regd']:
        params = issuance_params.copy()
        params['slug'] = reg
        if priority_only:
            params['shares_amount__gte'] = '5000'
        plist.append(params)
    return plist

def fetch_amount_and_count(url, params):
    data = requests.get(url, params=params)
    if options.verbose:
        print(f'fetched from {url}, {params}: {data.ok} {data.content}')
    if not data.ok:
        return -1
    jdata = json.loads(data.content)
    return (jdata['total_amount_committed']['amount'], jdata['total_amount_committed']['count'])

def total_committed_amount_and_count(url, params):
    d = [fetch_amount_and_count(url, p) for p in params]
    amt = [e[0] for e in d]
    cnt = [e[1] for e in d]
    return (sum(amt), sum(cnt))

def main(argv):
    global options
    parser = argparse.ArgumentParser()
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
    parser.add_argument('--verbose', '-v', action='count',
                        default=0,
                        help='increment the verbosity level by 1')
    options = parser.parse_args(argv[1:])
    if options.timestamp:
        ts = f'{datetime.datetime.now().isoformat()} '
    else:
        ts = ''

    if not options.priority_only and  options.remaining:
        print('Counting non-priority commitments and printing slots remaining are incompatible options', file=sys.stderr)
        return 1

    sums = total_committed_amount_and_count(issuance_url, make_params(options.priority_only))
    committed = sums[1]
    if options.remaining:
        committed = options.total_slots - committed
    if options.dollar:
        d = f'${sums[0]:,.2f} '
    else:
        d = ''
    print(f'{ts}{d}{committed:d}')
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))

