#!/usr/bin/python3

import sys
from typing import Callable, Tuple

import fbisect
import investment_data

verbose: int = 0

class CountBisectFunc:
    def __init__(self,
                 src: Callable[[int|None, int|None], Tuple[int, int]],
                 day: int,
                 max_day: int):
        self._src = src
        self._day = day
        self._max_day = max_day

    def __call__(self, threshold: int) -> int:
        today_count = self._src(threshold, self._day)[1]

        if self._day + 1 == self._max_day:
            next_day_count = 0
        else:
            next_day_count = self._src(threshold, self._day + 1)[1]

        incr = today_count - next_day_count

        return incr

class ExtractInvestment:
    def __init__(self,
                 src: Callable[[int|None, int|None], Tuple[int, int]],
                 max_day: int,
                 min_investment: int,
                 max_investment: int) -> None:
        self._src = src
        self._max_day = max_day
        self._min_inv = min_investment
        self._max_inv = max_investment

        self._daily_data: list[Tuple[int, int]] = []
        self._daily_amt: list[int] = [ -1 ] * max_day
        self._daily_count: list[int] = [ 0 ] * max_day

    def extract_investments(self) -> list[Tuple[int, int]]:
        for day in range(self._max_day):
            self._daily_data.append(self._src(None, day))

        for day in range(0, self._max_day - 1):
            self._daily_amt[day] = self._daily_data[day][0] - self._daily_data[day+1][0]
        self._daily_amt[self._max_day - 1] = self._daily_data[self._max_day - 1][0]

        for day in range(0, self._max_day - 1):
            self._daily_count[day] = self._daily_data[day][1] - self._daily_data[day+1][1]
        self._daily_count[self._max_day - 1] = self._daily_data[self._max_day - 1][1]
        # daily_amt has total for a day, but we do not yet know what the
        # individual transaction amounts are yet.

        # we bisect min to max investment amounts to discover the
        # threshold dollar value at which the count decreases.  note
        # that the decrease could be by more than 1, since there could
        # be two transactions with the same amount.

        investments: list[Tuple[int, int]] = []
        # qf = cache.FuncCache(self._src)
        qf = self._src
        for day in range(self._max_day):
            count = self._daily_count[day]

            while count > 0:
                func = CountBisectFunc(qf, day, self._max_day)
                # find which threshold value will first cause returned
                # transaction count to equal count variable.  this
                # will be the lowest value first, as a higher
                # threshold decreases the number of transactions being
                # summed.
                value = fbisect.find_last_ge(func,
                                             count,
                                             self._min_inv,
                                             self._max_inv)
                if verbose > 1:
                    sys.stderr.write(f'{count} {func(value)} {func(value+1)}\n')
                # DEBUG
                if count != func(value):
                    # this occurs if there's live new data
                    sys.stderr.write(f'count ({count}) != func({value}) ({func(value)}): nearby: {func(value-1)} {func(value)} {func(value+1)}\n')
                    sys.stderr.write(f'qf({value},{day}) = {qf(value,day)}\n')
                    sys.stderr.write(f'qf({value+1},{day}) = {qf(value+1,day)}\n')
                    sys.stderr.write(f'qf({value},{day+1}) = {qf(value,day+1)}\n')
                    sys.stderr.write(f'qf({value+1},{day+1}) = {qf(value+1,day+1)}\n')
                # DEBUG
                assert(count == func(value))
                new_count = func(value+1)
                if verbose > 1:
                    sys.stderr.write(f'new_count = {new_count}, func({value+1}) = {func(value+1)}\n')
                count_changed = count - new_count
                assert(count_changed > 0)
                # investment totals at value and value+1 for today
                investment_diff = (self._src(value, day)[0] - self._src(value+1, day)[0]) - (self._src(value, day+1)[0] - self._src(value+1,day+1)[0])

                # Sometimes investment_diff is not evenly divisible by
                # count_changed.  My guess is that this represents
                # fees charged by issuance.

                if investment_diff % count_changed != 0:
                    sys.stderr.write(f'FEES? investment_diff = {investment_diff}, count_changed = {count_changed}\n')
                    sys.stderr.write(f'qf({value},{day}) = {qf(value,day)}\n')
                    sys.stderr.write(f'qf({value+1},{day}) = {qf(value+1,day)}\n')
                    sys.stderr.write(f'qf({value},{day+1}) = {qf(value,day+1)}\n')
                    sys.stderr.write(f'qf({value+1},{day+1}) = {qf(value+1,day+1)}\n')

                # investment = investment_diff // count_changed
                # investment > value due to fees
                for _ in range(count_changed):
                    investments.append((day, value))
                count = new_count
        return investments
