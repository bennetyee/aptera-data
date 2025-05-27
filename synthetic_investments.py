#!/usr/bin/python3

import functools
import random
from typing import Any, Callable, Dict, Tuple, Union

import cache
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

    def __call__(self, threshold: int | None, date: int) -> Tuple[int, int]:
        self._num_queries += 1
        d = self._investments
        if threshold is not None:
            d = [t for t in d if t[1] >= threshold]
        d = [t for t in d if t[0] >= date]

        dl = [t[1] for t in d]
        return (sum(dl), len(dl))

    def flush_cache(self):
        return  # no-op

    def cache(self) -> cache.FuncCache | None:
        return None

    def set_cache(self, c: Dict[Any, Any]) -> None:
        return

    def enable_cache(self) -> None:
        return

    def set_progress_period(self, p: int) -> None:
        return

    def reset_num_queries(self) -> None:
        self._num_queries = 0

    def num_queries(self) -> int:
        return self._num_queries
