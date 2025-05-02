#!/usr/bin/python3

# Binary search: similar idea as the bisect module, except that we are
# doing bisection using an univariate monotonically non-decreasing (or
# non-increasing) function from integers to integers.

from typing import Callable

# range R = \left\[x0,x1\right\]

# Henceforth until otherwise indicated,
# f is monotonically non-decreasing; i.e.,
#   \forall x_1, x_2 \in R:  x_1 < x_2 \rightarrow f(x_1) \le f(x_2)

# returns x \in R such that f(x) \ge ythreshold
#   \wedge \forall x' \in R: f(x') \ge ythreshold \rightarrow x \le x'
def find_first_ge(f: Callable[[int], int],
                  ythreshold: int,
                  x0: int,
                  x1: int) -> int:
    assert(x0 <= x1)  # non-empty range
    assert f(x1) >= ythreshold
    if f(x0) >= ythreshold:
        return x0
    # f(x0) < ythreshold
    return find_first_ge_intern(f, ythreshold, x0, x1)

def find_first_ge_intern(f: Callable[[int], int],
                         ythreshold: int,
                         x0: int,
                         x1: int) -> int:

    if x0 + 1 == x1:
        return x1
    xmid = (x0 + x1) // 2  # python, no overflow
    if f(xmid) >= ythreshold:
        return find_first_ge_intern(f, ythreshold, x0, xmid)

    # f(xmid) < ythreshold
    return find_first_ge_intern(f, ythreshold, xmid, x1)

# returns x \in R such that f(x) \le ythreshold
#   \wedge \forall x' \in R: f(x') \le ythreshold \rightarrow x' \le x
def find_last_le(f: Callable[[int], int],
                 ythreshold: int,
                 x0: int,
                 x1: int) -> int:
    assert(x0 <= x1)  # non-empty range
    assert f(x0) <= ythreshold
    if f(x1) <= ythreshold:
        return x1
    # f(x1) > ythreshold
    return find_last_le_intern(f, ythreshold, x0, x1)

def find_last_le_intern(f: Callable[[int], int],
                        ythreshold: int,
                        x0: int,
                        x1: int) -> int:
    if x0 + 1 == x1:
        return x0
    xmid = (x0 + x1) // 2  # python, no overflow
    if f(xmid) <= ythreshold:
        return find_last_le_intern(f, ythreshold, xmid, x1)

    # f(xmid) > ythreshold
    return find_last_le_intern(f, ythreshold, x0, xmid)

# Henceforth until otherwise indicated,
# f is monotonically nonincreasing, i.e.,
#   \forall x_1, x_2 \in R:  x_1 < x_2 \rightarrow f(x_1) \ge f(x_2)

# returns x \in R such that f(x) \le ythreshold
#   \wedge \forall x' \in R: f(x') \le ythreshold \rightarrow x \le x'
def find_first_le(f: Callable[[int], int],
                  ythreshold: int,
                  x0: int,
                  x1: int) -> int:
    assert(x0 <= x1)  # non-empty range
    assert f(x1) <= ythreshold
    if f(x0) <= ythreshold:
        return x0
    # f(x0) > ythreshold
    return find_first_le_intern(f, ythreshold, x0, x1)

def find_first_le_intern(f: Callable[[int], int],
                         ythreshold: int,
                         x0: int,
                         x1: int) -> int:

    if x0 + 1 == x1:
        return x1
    xmid = (x0 + x1) // 2  # python, no overflow
    if f(xmid) <= ythreshold:
        return find_first_le_intern(f, ythreshold, x0, xmid)

    # f(xmid) > ythreshold
    return find_first_le_intern(f, ythreshold, xmid, x1)

# returns x \in R such that f(x) \ge ythreshold
#   \wedge \forall x' \in R: f(x') \ge ythreshold \rightarrow x' \le x
def find_last_ge(f: Callable[[int], int],
                 ythreshold: int,
                 x0: int,
                 x1: int) -> int:
    assert(x0 <= x1)  # non-empty range
    assert f(x0) >= ythreshold
    if f(x1) >= ythreshold:
        return x1
    # f(x1) < ythreshold
    return find_last_ge_intern(f, ythreshold, x0, x1)

def find_last_ge_intern(f: Callable[[int], int],
                        ythreshold: int,
                        x0: int,
                        x1: int) -> int:
    if x0 + 1 == x1:
        return x0
    xmid = (x0 + x1) // 2  # python, no overflow
    if f(xmid) >= ythreshold:
        return find_last_ge_intern(f, ythreshold, xmid, x1)

    # f(xmid) < ythreshold
    return find_last_ge_intern(f, ythreshold, x0, xmid)
