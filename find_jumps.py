#!/usr/bin/python3

# Find all jumps or input values x for an univariate monotonically
# non-increasing integer to integer function f where f(x) > f(x+1),
# where x0 \le x \le x1.

from typing import Callable

def find_lasts(f: Callable[[int], int],
               x0: int,
               x1: int) -> list[int]:
    y0 = f(x0)
    y1 = f(x1)
    if y0 == y1:
        return []
    assert y0 > y1, f'find_lasts: {y0} < {y1}: not monotonically non-increasing / no jumps exists in range'  # precondition check
    results = []
    def g(x):
        results.append(x)
    find_lasts_intern(f, x0, y0, x1, y1, g)
    return results

def find_lasts_intern(f: Callable[[int], int],
                      x0: int,
                      y0: int,
                      x1: int,
                      y1: int,
                      g: Callable[[int], None]) -> None:
    # preconditions:
    #  x0 < x1
    #  f(x0) > f(x1)
    if x0 + 1 == x1:
        g(x0)
        return
    # x0 + 1 < x1, so x0 + 2 \le x1, and (x0 + 2 + x1) \le 2 x1
    # and (x0 + x1) // 2 + 1 \le x1, so (x0 + x1) // 2 < x1.
    # similarly, x0 < x0 + 1 < x1, so x0 < x1 - 1, and
    # x0 + x0 < x0 + x1 - 1.  2 x0 \le x0 + x1 so x0 \le (x0 + x1) // 2
    xmid = (x0 + x1) // 2
    ymid = f(xmid)
    if y0 > ymid:
        find_lasts_intern(f, x0, y0, xmid, ymid, g)
    if ymid > y1:
        find_lasts_intern(f, xmid, ymid, x1, y1, g)
