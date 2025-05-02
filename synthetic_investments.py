#!/usr/bin/python3

import functools
import random
from typing import Any, Callable, Tuple, Union

import investment_data

class SyntheticInvestmentData(investment_data.InvestmentData):
    def __init__(self, num_entries: int, num_days: int,
                 min_invest: int, max_invest: int,
                 rng: Callable[..., int]) -> None:
        # rng should be something like random.randrange, and take one
        # or two integer arguments
        self._investments = [
            (rng(num_days),
             rng(min_invest, max_invest))
            for _ in range(num_entries)]
        self._num_queries = 0

    def filter_and_summarize(self, threshold: int | None, date: int | None) -> Tuple[int, int]:
        self._num_queries += 1
        d = self._investments
        if threshold is not None:
            d = [t for t in d if t[1] >= threshold]
        if date is not None:
            d = [t for t in d if t[0] >= date]

        dl = [t[1] for t in d]
        return (sum(dl), len(dl))

    def reset_num_queries(self) -> None:
        self._num_queries = 0

    def num_queries(self) -> int:
        return self._num_queries
