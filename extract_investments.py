#!/usr/bin/python3

from abc import ABC, abstractmethod
import sys
from typing import Callable, Tuple

import fbisect
import find_jumps
import investment_data

verbose: int = 0

class BisectFunc(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def __call__(self, threshold: int) -> int:
        pass

class CumulativeCountBisectFunc(BisectFunc):
    def __init__(self,
                 src: Callable[[int|None, int], Tuple[int, int]],
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

class DailyCountBisectFunc(BisectFunc):
    def __init__(self,
                 src: Callable[[int|None, int], Tuple[int, int]],
                 day: int):
        self._src = src
        self._day = day

    def __call__(self, threshold: int) -> int:
        incr = self._src(threshold, self._day)[1]
        return incr


class ExtractInvestment:
    def __init__(self,
                 src: investment_data.InvestmentData,
                 max_day: int,
                 min_investment: int,
                 max_investment: int,
                 max_day_error: int = 8,
                 src_is_cumulative: bool = True) -> None:
        self._src = src
        self._max_day = max_day
        self._min_inv = min_investment
        self._max_inv = max_investment
        self._max_day_error = max_day_error
        self._src_is_cumulative = src_is_cumulative

        self._daily_data: list[Tuple[int, int]] = []
        self._daily_amt: list[int] = [ -1 ] * max_day
        self._daily_count: list[int] = [ 0 ] * max_day

    def compute_daily_data(self):
        for day in range(self._max_day):
            self._daily_data.append(self._src(None, day))

        if self._src_is_cumulative:
            for day in range(0, self._max_day - 1):
                self._daily_amt[day] = self._daily_data[day][0] - self._daily_data[day+1][0]
            self._daily_amt[self._max_day - 1] = self._daily_data[self._max_day - 1][0]

            for day in range(0, self._max_day - 1):
                self._daily_count[day] = self._daily_data[day][1] - self._daily_data[day+1][1]
            self._daily_count[self._max_day - 1] = self._daily_data[self._max_day - 1][1]
        else:
            for day in range(0, self._max_day):
                self._daily_amt[day] = self._daily_data[day][0]
                self._daily_count[day] = self._daily_data[day][1]

    def extract_investments(self) -> list[Tuple[int, int]]:
        self.compute_daily_data()
        # daily_amt has total for a day, but we do not yet know what the
        # individual transaction amounts are yet.

        # we bisect min to max investment amounts to discover the
        # threshold dollar value at which the count decreases.  note
        # that the decrease could be by more than 1, since there could
        # be two transactions with the same amount.

        investments: list[Tuple[int, int]] = []
        qf = self._src
        for day in range(self._max_day):
            day_column_done = False
            day_error_count = 0
            while not day_column_done:
                count = self._daily_count[day]
                if self._src_is_cumulative:
                    func: BisectFunc = CumulativeCountBisectFunc(qf, day, self._max_day)
                else:
                    func = DailyCountBisectFunc(qf, day)

                count_history = []
                while count > 0:
                    count_history.append(count)
                    try:
                        value = fbisect.find_last_ge(func,
                                                     count,
                                                     self._min_inv,
                                                     self._max_inv)
                    except AssertionError as e:
                        sys.stderr.write(f'bisection assertion error ({e}); retrying day {day}\n')
                        break
                    if verbose > 1:
                        sys.stderr.write(f'{count} {func(value)} {func(value+1)}\n')
                    if count != func(value):
                        # this occurs if there's live new data
                        sys.stderr.write(f'bisection count changed, history {count_history}; retrying day {day}\n')
                        sys.stderr.write(f'count ({count}) != func({value}) ({func(value)}): nearby: {func(value-1)} {func(value)} {func(value+1)}\n')
                        sys.stderr.write(f'qf({value},{day}) = {qf(value,day)}\n')
                        sys.stderr.write(f'qf({value+1},{day}) = {qf(value+1,day)}\n')
                        sys.stderr.write(f'qf({value},{day+1}) = {qf(value,day+1)}\n')
                        sys.stderr.write(f'qf({value+1},{day+1}) = {qf(value+1,day+1)}\n')
                        break

                    new_count = func(value+1)
                    count_changed = count - new_count
                    if verbose > 1:
                        sys.stderr.write(f'new_count = {new_count}, func({value+1}) = {func(value+1)}\n')
                        if count_changed <= 0:
                            sys.stderr.write(f'bisection count change ({count}-{new_count}={count_changed}) not positive, history {count_history}; retrying day {day}\n')
                            break
                    # investment totals at value and value+1 for today
                    investment_diff = (self._src(value, day)[0] - self._src(value+1, day)[0])

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
                # we may have exited early due to new data arriving,
                # in which case we re-extract the entire day's
                # investment
                day_column_done = count == 0
                if not day_column_done:
                    day_error_count += 1
                    if day_error_count >= self._max_day_error:
                        sys.stderr.write(f'max day error exceeded, aborting\n')
                        raise RuntimeError('Max day error exceeded')
                    sys.stderr.write('sanity check violation. likely new data incorporated.\n')
                    qf.flush_cache()
                    self.compute_daily_data()
            # redo column?
        return investments

    def fast_extraction(self) -> list[Tuple[int, int]]:
        investments: list[Tuple[int, int]] = []
        qf = self._src
        for day in range(self._max_day):
            day_column_done = False
            day_error_count = 0
            while not day_column_done:
                if self._src_is_cumulative:
                    func: BisectFunc = CumulativeCountBisectFunc(qf, day, self._max_day)
                else:
                    func = DailyCountBisectFunc(qf, day)
                day_list = []
                try:
                    day_investments = find_jumps.find_lasts(func, 0, self._max_inv)
                except AssertionError as e:
                    sys.stderr.write(f'bisection assertion error ({e}); retrying at day {day}\n')
                    day_error_count += 1
                    if day_error_count >= self._max_day_error:
                        break
                retry = False
                for x in day_investments:
                    count = func(x)
                    new_count = func(x + 1)
                    count_changed = count - new_count
                    if count_changed <= 0:
                        sys.stderr.write(f'count change not positive; retrying day {day}\n')
                        retry = True
                        break
                    for _ in range(count_changed):
                        day_list.append((day, x))
                if not retry:
                    day_column_done = True
                else:
                    day_error_count += 1
                    if day_error_count >= self._max_day_error:
                        break
            if not day_column_done:
                sys.stderr.write(f'max day error exceeded, aborting\n')
                raise RuntimeError('Max day error exceeded')
            investments += day_list
        return investments
