#!/usr/bin/python3

import sys
import json
import requests
import urllib

issuance_url1 = 'https://api.issuance.com/api/investments/summary/?slug=aptera-regd&shares_amount__gte=5000&processed_at__date__gte=2025-04-10'
issuance_url2 = 'https://api.issuance.com/api/investments/summary/?slug=aptera-rega&shares_amount__gte=5000&processed_at__date__gte=2025-04-10'

queries = [issuance_url1, issuance_url2]

options = None

def fetch_count(url):
    data = requests.get(url)
    if not data.ok:
        return -1
    jdata = json.loads(data.content)
    return jdata['total_amount_committed']['count']

def total_committed():
    return sum(fetch_count(u) for u in queries)

def main(argv):
    # parser = argparse.ArgumentParser()
    # ...
    # options = parser.parse_args(argv[1:])
    print(f'{total_committed():d}')
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))

