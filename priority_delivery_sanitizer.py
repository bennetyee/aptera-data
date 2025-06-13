#!/usr/bin/python3

import json
import requests
import sys

import issuance

def fetch_and_sanitize():
    """Fetch number of priority delivery slots and strip everything
    but the number of slots taken.
    """
    threshold = 5000 * 100
    sums = issuance.total_committed_amount_and_count_at_threshold(threshold)
    return {'total_amount_committed': { 'count': sums[1] } }

def main(_):
    response = fetch_and_sanitize()
    print(json.dumps(response))
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
