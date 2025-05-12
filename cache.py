#!/usr/bin/python3

import sys
from typing import Any, Callable, Dict

# Cache grows unbounded, so beware.  The set_cache method can be used
# to clear the cache.  The cache and set_cache methods are intended to
# allow writing the cache contents to a file to avoid the expense of
# repeated calls to f across executions.  If f represents a network
# query, the query results should not change over time during the
# usage (including saves and reloads) of a FuncCache object.

class FuncCache:
    def __init__(self, f: Callable[..., Any]):
        self._f = f
        self._cache: Dict[Any, Any] = dict()
        self._progress: int = 0
        self._hits: int = 0
        self._misses: int = 0

    def set_show_progress_period(self, p: int) -> None:
        self._progress = p

    def __call__(self, *args: Any) -> Any:
        if args in self._cache:
            self._hits += 1
            if self._progress > 0 and self._hits % self._progress == 0:
                sys.stderr.write('.')
                sys.stderr.flush()
            return self._cache[args]
        self._misses += 1
        if self._progress > 0 and self._misses % self._progress == 0:
            sys.stderr.write(',')
            sys.stderr.flush()
        y = self._f(*args)
        self._cache[args] = y
        return y

    def cache(self) -> Dict[Any, Any]:
        return self._cache

    def set_cache(self, cache: Dict[Any, Any]) -> None:
        self._cache = cache

    def flush_cache(self) -> None:
        self._cache = {}
        if self._progress != 0:
            sys.stderr.write('!')
            sys.stderr.flush()
