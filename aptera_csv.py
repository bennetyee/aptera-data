#!/usr/bin/python3

import csv
import sys

RANK=0
INITIALIS=1
STATE=2
COUNTRY=3
INVESTMENT_ID=4
TIMESTAMP=5
ACCELERATOR_INVESTMENT=6
ALL_TIME_INVESTMENT=7
NUM_COLUMNS=8

def read_csv_stream(istr):
    dialect = csv.Sniffer().sniff(istr.read(1024))
    istr.seek(0)
    r = csv.reader(istr, dialect)
    return [row for row in r]

def read_csv_file(fn):
    with open(fn) as istr:
        table = read_csv_stream(istr)
    for ix, row in enumerate(table):
        if len(row) != NUM_COLUMNS:
            sys.stderr.write(f'File {fn} format error on line {ix}: wrong number of columns.\n')
            return None
        if not row[ACCELERATOR_INVESTMENT].startswith('$'):
            sys.stderr.write(f'File {fn} format error on line {ix}: no dollar amount\n')
            return None
        if not row[ALL_TIME_INVESTMENT].startswith('$'):
            sys.stderr.write(f'File {fn} format error on line {ix}: no dollar amount\n')
            return None

        row[RANK] = int(row[RANK])
        row[ACCELERATOR_INVESTMENT] = float(row[ACCELERATOR_INVESTMENT].replace('$','').replace(',',''))
        row[ALL_TIME_INVESTMENT] = float(row[ALL_TIME_INVESTMENT].replace('$','').replace(',',''))
    return table
