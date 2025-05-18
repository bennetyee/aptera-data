#!/usr/bin/python3

import datetime
import json
import requests
import sys
import time

from typing import Any, Dict, Generator, Tuple

import cache
import investment_data

verbose = 0  # verbosity level

priority_program_start_date_iso = '2025-04-10'

issuance_url = 'https://api.issuance.com/api/investments/summary/'
issuance_params = {
    'processed_at__date__gte': priority_program_start_date_iso,
}

priority_slots_available = 1_000

def today_day_number():
    start_day = datetime.date.fromisoformat(priority_program_start_date_iso)
    today = datetime.date.today()
    elapsed = today - start_day
    return elapsed.days

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
    if verbose > 3:
        print(f'fetched from {url}, {params}: {data.ok} {data.content!r}')
    if not data.ok:
        raise IOError
    jdata = json.loads(data.content)
    return (jdata['total_amount_committed']['amount'], jdata['total_amount_committed']['count'])

def total_committed_amount_and_count(url: str, params: list[Dict[str, str]]) -> Tuple[float, int]:
    d = [fetch_amount_and_count(url, p) for p in params]
    amt, cnt = map(list, zip(*d))
    return (sum(amt), sum(cnt))

def total_committed_amount_and_count_at_threshold(threshold: int | None):
    return total_committed_amount_and_count(issuance_url, make_params(threshold))

class IssuanceInvestmentData(investment_data.InvestmentData):
    def __init__(self, slug: str):
        self._day_zero = datetime.date.fromisoformat(priority_program_start_date_iso)
        self._one_day = datetime.timedelta(days=1)
        self._slug = slug
        self._cache: cache.FuncCache | None = None

    def __call__(self, threshold: int | None, date: int | None) -> Tuple[int, int]:
        if self._cache is not None:
            return self._cache(threshold, date)
        return self.real_work(threshold, date)

    def real_work(self, threshold: int | None, date: int | None) -> Tuple[int, int]:
        params: Dict[str, str] = dict()

        params['slug'] = self._slug
        if threshold is not None:
            params['shares_amount__gte'] = f'{threshold / 100.0:.2f}'
        if date is not None:
            date_str = (self._day_zero + date * self._one_day).isoformat()
            params['processed_at__date__gte'] = date_str

        amount = 0
        count = 0
        if verbose > 2:
            sys.stderr.write(f'params {params}\n')

        data = requests.get(issuance_url, params=params)
        if not data.ok:
            raise IOError
        jdata = json.loads(data.content)
        a = jdata['total_amount_committed']['amount']
        c = jdata['total_amount_committed']['count']
        if verbose > 2:
            sys.stderr.write(f'slug = {self._slug}, a = {a:18f}, c = {c:18f}\n')
        amount += int(100 * a + 0.5)
        count += int(c)
        return (amount, count)

    def enable_cache(self):
        self._cache = cache.FuncCache(self.real_work)

    def flush_cache(self):
        if self._cache is not None:
            self._cache.flush_cache()

    def cache(self) -> cache.FuncCache | None:
        return self._cache

    def set_cache(self, c: Dict[Any, Any]) -> None:
        # throws if self._cache is None
        if self._cache is None:
            raise RuntimeError('caching not enabled')
        self._cache.set_cache(c)

    def set_progress_period(self, p: int) -> None:
        # throws if self._cache is None
        if self._cache is None:
            raise RuntimeError('caching not enabled')
        self._cache.set_show_progress_period(p)

# Use a day-specific query
class IssuanceInvestmentDataSpecific(investment_data.InvestmentData):
    def __init__(self, slug: str):
        self._day_zero = datetime.date.fromisoformat(priority_program_start_date_iso)
        self._one_day = datetime.timedelta(days=1)
        self._slug = slug
        self._cache: cache.FuncCache | None = None

    def __call__(self, threshold: int | None, date: int | None) -> Tuple[int, int]:
        if self._cache is not None:
            return self._cache(threshold, date)
        return self.real_work(threshold, date)

    def real_work(self, threshold: int | None, date: int) -> Tuple[int, int]:
        params: Dict[str, str] = dict()

        params['slug'] = self._slug
        if threshold is not None:
            params['shares_amount__gte'] = f'{threshold / 100.0:.2f}'

        date_str = (self._day_zero + date * self._one_day).isoformat()
        params['processed_at__date__gte'] = date_str
        params['processed_at__date__lte'] = date_str

        amount = 0
        count = 0
        if verbose > 2:
            sys.stderr.write(f'params {params}\n')

        data = requests.get(issuance_url, params=params)
        if not data.ok:
            raise IOError
        jdata = json.loads(data.content)
        a = jdata['total_amount_committed']['amount']
        c = jdata['total_amount_committed']['count']
        if verbose > 2:
            sys.stderr.write(f'slug = {self._slug}, a = {a:18f}, c = {c:18f}\n')
        amount += int(100 * a + 0.5)
        count += int(c)
        return (amount, count)

    def enable_cache(self):
        self._cache = cache.FuncCache(self.real_work)

    def flush_cache(self):
        if self._cache is not None:
            self._cache.flush_cache()

    def cache(self) -> cache.FuncCache | None:
        return self._cache

    def set_cache(self, c: Dict[Any, Any]) -> None:
        # throws if self._cache is None
        if self._cache is None:
            raise RuntimeError('caching not enabled')
        self._cache.set_cache(c)

    def set_progress_period(self, p: int) -> None:
        # throws if self._cache is None
        if self._cache is None:
            raise RuntimeError('caching not enabled')
        self._cache.set_show_progress_period(p)
