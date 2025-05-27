#!/usr/bin/python3

import unittest

import fbisect

class TestSimpleSearch(unittest.TestCase):

    def test_find1(self):
        data = [-2, -1, -1, 0, 0, 10, 20, 30]
        def f(ix):
            return data[ix]
        self.assertEqual(fbisect.find_first_ge(f, 0, 0, len(data)-1), 3)
        self.assertEqual(fbisect.find_first_ge(f, 10, 0, len(data)-1), 5)

    def test_find2(self):
        data = [-100, -2, -1, -1, 0, 0, 10, 20, 30]
        def f(ix):
            return data[ix]
        self.assertEqual(fbisect.find_first_ge(f, 0, 0, len(data)-1), 4)
        self.assertEqual(fbisect.find_first_ge(f, -2, 0, len(data)-1), 1)

    def test_find3(self):
        data = [-100, -20, -10, -5, -1, -1, 10, 20, 20, 30]
        def f(ix):
            return data[ix]
        self.assertEqual(fbisect.find_first_ge(f, 0, 0, len(data)-1), 6)
        self.assertEqual(fbisect.find_first_ge(f, 20, 0, len(data)-1), 7)

    def test_find4(self):
        data = [-100, 10, 20, 30] + [i + 31 for i in range(10000)]
        def f(ix):
            return data[ix]
        self.assertEqual(fbisect.find_first_ge(f, 0, 0, len(data)-1), 1)
        self.assertEqual(fbisect.find_first_ge(f, 32, 0, len(data)-1), 5)

    def test_find5(self):
        data = [-i - 200 for i in range(10000)] + [-100, 10, 20, 30]
        def f(ix):
            return data[ix]
        self.assertEqual(fbisect.find_first_ge(f, 0, 0, len(data)-1), 10001)
        self.assertEqual(fbisect.find_first_ge(f, 15, 0, len(data)-1), 10002)

    def test_func1(self):
        self.assertEqual(
            fbisect.find_first_ge(
                lambda x: int(x * 200 + 300), 0, -1000, 1000),
            -1)
        self.assertEqual(
            fbisect.find_first_ge(
                lambda x: int(x * 200 + 300), 123, -1000, 1000),
            0)

if __name__ == '__main__':
    unittest.main()
