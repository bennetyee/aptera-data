#!/usr/bin/python3

import argparse
import datetime
import json
import requests
import sys

issuance_url1 = 'https://api.issuance.com/api/investments/summary/?slug=aptera-regd&shares_amount__gte=5000&processed_at__date__gte=2025-04-10'
issuance_url2 = 'https://api.issuance.com/api/investments/summary/?slug=aptera-rega&shares_amount__gte=5000&processed_at__date__gte=2025-04-10'

queries = [issuance_url1, issuance_url2]

priority_slots_available = 1_000

options = None

def fetch_count(url):
    data = requests.get(url)
    if options.verbose:
        print(f'fetched from {url}: {data.ok} {data.content}')
    if not data.ok:
        return -1
    jdata = json.loads(data.content)
    return jdata['total_amount_committed']['count']

def total_committed():
    return sum(fetch_count(u) for u in queries)

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
    parser.add_argument('--verbose', '-v', action='count',
                        default=0,
                        help='increment the verbosity level by 1')
    options = parser.parse_args(argv[1:])
    if options.timestamp:
        ts = datetime.datetime.now().isoformat() + ' '
    else:
        ts = ''
    value = total_committed()
    if options.remaining:
        value = options.total_slots - value
    print(f'{ts}{value:d}')
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))

