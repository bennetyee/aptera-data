#!/usr/bin/python3

import datetime
import json
import requests
import sys

from typing import Any, Dict, Generator, Tuple

verbose = 0  # verbosity level

issuance_url = 'https://api.issuance.com/api/investments/summary/'
issuance_params = {
    'processed_at__date__gte': '2025-04-10',
}

priority_slots_available = 1_000

# investment_threshold is in USD in cents
def make_params(investment_threshold_cents: int | None) -> list[Dict[str, str]]:
    plist = []
    for reg in ['aptera-rega', 'aptera-regd']:
        params = issuance_params.copy()
        params['slug'] = reg
        if investment_threshold_cents is not None:
            params['shares_amount__gte'] = f'{investment_threshold_cents / 100.0:.2f}'
        plist.append(params)
    return plist

def fetch_amount_and_count(url: str, params: Dict[str, str]) -> Tuple[float, float]:
    data = requests.get(url, params=params)
    if verbose:
        print(f'fetched from {url}, {params}: {data.ok} {data.content!r}')
    if not data.ok:
        raise IOError
    jdata = json.loads(data.content)
    return (jdata['total_amount_committed']['amount'], jdata['total_amount_committed']['count'])

def total_committed_amount_and_count(url: str, params: Dict[str, str]) -> Tuple[float, int]:
    d = [fetch_amount_and_count(url, p) for p in params]
    amt, cnt = map(list, zip(*d))
    return (sum(amt), sum(cnt))

def total_committed_amount_and_count_at_threshold(threshold: int):
    return total_committed_amount_and_count(issuance_url, make_params(threshold))
