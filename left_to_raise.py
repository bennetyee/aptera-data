#!/usr/bin/python3

import json
import requests
import sys

url='https://api.issuance.com/api/investments/summary/?slug=aptera-regcf'
raise_goal = 5_000_000

def fetch(url):
    json_str = requests.get(url)
    response = json.loads(json_str.content)
    return response

def left_to_raise(url):
    d = fetch(url)
    return raise_goal - d['total_amount_committed']['amount']

def main(argv):
    # no argument parser for now
    print(f'${left_to_raise(url):,.2f} left to raise')
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
