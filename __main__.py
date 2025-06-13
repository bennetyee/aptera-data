#!/usr/bin/python3

import sys

import aptera_data
import coupon_round
import extract_coupon_investments
import investment_trend
import left_to_raise
import priority_delivery_sanitizer

if __name__ == '__main__':
    entries = [
        ('aptera_data', aptera_data),
        ('coupon_round', coupon_round),
        ('extract_coupon_investments', extract_coupon_investments),
        ('investment_trend', investment_trend),
        ('left_to_raise', left_to_raise),
        ('priority_delivery_sanitizer', priority_delivery_sanitizer),
    ]
    for (name, mod) in entries:
        if sys.argv[0].endswith(name):
            sys.exit(mod.main(sys.argv))
    sys.stderr.write(f'python zip executable packaging/naming error.  Unknown entry point name {sys.argv[0]}\n')
    sys.exit(-1)
