#!/usr/bin/python3

import datetime
import os
import random
import sys
import unittest

import extract_investments
import issuance
import synthetic_investments

from typing import Callable, Dict

SEEDENV = 'EXTRACT_SEED'

seed: int = 0

class TestExtraction(unittest.TestCase):
    def test_synth(self) -> None:
        assert(seed != 0)
        rng = random.Random(seed)
        num_entries = 20
        num_days = 10
        min_inv = 500
        max_inv = 550
        si = synthetic_investments.SyntheticInvestmentData(
            num_entries, num_days, min_inv, max_inv, rng.randrange)
        extractor = extract_investments.ExtractInvestment(
            si, num_days, min_inv, max_inv)

        investments = extractor.extract_investments()
        daily: Dict[int, int] = dict()
        for day in range(num_days):
            daily[day] = 0
        for day, value in si._investments:
            daily[day] += value
        daily_totals = set(daily.items())
        extracted_totals = set((d, extractor._daily_amt[d]) for d in range(num_days))
        self.assertEqual(daily_totals, extracted_totals)

        iset = set(investments)
        siset = set(si._investments)
        self.assertEqual(iset, siset)
        sys.stdout.write(f'si.num_queries() = {si.num_queries()}\n')

    def test_synth_actual_days(self) -> None:
        assert(seed != 0)
        rng = random.Random(seed + 1)
        num_entries = 400
        start_day = datetime.date.fromisoformat(issuance.priority_program_start_date_iso)
        today = datetime.date.today()
        num_days = (today - start_day).days
        min_inv = 500
        max_inv = 10_000
        si = synthetic_investments.SyntheticInvestmentData(
            num_entries, num_days, min_inv, max_inv, rng.randrange)
        extractor = extract_investments.ExtractInvestment(
            si, num_days, min_inv, max_inv)

        investments = extractor.extract_investments()
        daily: Dict[int, int] = dict()
        for day in range(num_days):
            daily[day] = 0
        for day, value in si._investments:
            daily[day] += value
        daily_totals = set(daily.items())
        extracted_totals = set((d, extractor._daily_amt[d]) for d in range(num_days))
        self.assertEqual(daily_totals, extracted_totals)

        iset = set(investments)
        siset = set(si._investments)
        self.assertEqual(iset, siset)
        sys.stdout.write(f'si.num_queries() = {si.num_queries()}\n')

if __name__ == '__main__':
    if SEEDENV in os.environ:
        seed = int(os.environ[SEEDENV], 16)
        sys.stdout.write(f'extracted fixed seed from environment {SEEDENV}={seed:x}\n')
    if seed is None or seed == 0:
        seed = random.getrandbits(64)
    sys.stdout.write(f'{SEEDENV}={seed:x}\n')
    unittest.main()
