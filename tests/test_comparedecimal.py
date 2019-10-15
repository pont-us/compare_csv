#!/usr/bin/env python3

"""
This file is part of comparedecimal.

Copyright 2018 Pontus Lurcock.

comparedecimal is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

comparedecimal is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with comparedecimal.  If not, see <http://www.gnu.org/licenses/>.
"""

from comparedecimal import DecimalComparer, EqualityLevel, FieldDifference
import unittest
import random


class TestCompareCsv(unittest.TestCase):

    def setUp(self):
        self.comparer = DecimalComparer(separator="\t")

    def _check_totals_counts(self, *expected):
        self.assertEqual(expected[0],
                         self.comparer.totals[EqualityLevel.UNEQUAL])
        self.assertEqual(expected[1],
                         self.comparer.totals[EqualityLevel.CLOSE])
        self.assertEqual(expected[2],
                         self.comparer.totals[EqualityLevel.COMPATIBLE])
        self.assertEqual(expected[3],
                         self.comparer.totals[EqualityLevel.NUMERICALLY_EQUAL])
        self.assertEqual(expected[4],
                         self.comparer.totals[EqualityLevel.IDENTICAL])

    def test_compare_fields_equal(self):
        fields = ["one", "two", "3.5", "-10.7"]
        self.assertIsNone(
            self.comparer.compare_string_lists(fields, fields)
        )
        self._check_totals_counts(0, 0, 0, 0, 4)

    def test_compare_fields_unequal(self):
        self.assertIsInstance(self.comparer.compare_string_lists(
                ["one", "two", "3.5", "-10.7"],
                ["one", "3.5", "-10.7"]), FieldDifference)

    def test_compare_fields_numerically_equal(self):
        self.assertIsNone(self.comparer.compare_string_lists(
            ["wibble", "3.5", "-10.00000"], ["wibble", "3.500", "-10"]))
        self._check_totals_counts(0, 0, 0, 2, 1)

    def test_compare_fields_numerically_unequal(self):
        self.assertIsInstance(self.comparer.compare_string_lists(
                ["wibble", "3.5", "-10.00000"],
                ["wibble", "3.500", "-11.00000"]), FieldDifference)
        self._check_totals_counts(1, 0, 0, 1, 1)

    def test_compare_field(self):
        comparer = DecimalComparer(",", 0.01)

        def check(expected, string0, string1):
            actual = comparer.compare_strings(string0, string1)
            self.assertEqual(expected, actual)

        check(EqualityLevel.UNEQUAL, "1", "2")
        check(EqualityLevel.IDENTICAL, "1", "1")
        check(EqualityLevel.NUMERICALLY_EQUAL, "1.000000", "1")
        check(EqualityLevel.COMPATIBLE, "1.1", "1")
        check(EqualityLevel.COMPATIBLE, "123.456", "123.46")
        check(EqualityLevel.CLOSE, "123.456", "123.460")
        check(EqualityLevel.UNEQUAL, "-123", "123")
        check(EqualityLevel.COMPATIBLE, "+14.271e3", "1.427e4")
        check(EqualityLevel.CLOSE, "-8.912E-3", "-89.13E-4")
        check(EqualityLevel.COMPATIBLE, "-8.912E-3", "-89.1E-4")
        check(EqualityLevel.NUMERICALLY_EQUAL, "0", "0.000")
        check(EqualityLevel.NUMERICALLY_EQUAL, "-0", "0")
        check(EqualityLevel.COMPATIBLE, "-5.99e3", "-5994")
        check(EqualityLevel.UNEQUAL, "foo", "bar")
        check(EqualityLevel.IDENTICAL, "foo", "foo")
        check(EqualityLevel.COMPATIBLE, "-1.8850E-6", "-1.89E-06")
        check(EqualityLevel.COMPATIBLE, "4.3458E-5", "4.35E-05")
        check(EqualityLevel.COMPATIBLE, "9.9952E-8", "1.00E-07")
        check(EqualityLevel.CLOSE, "1.50", "1.49")
        check(EqualityLevel.UNEQUAL, "2.0", "1.94")
        check(EqualityLevel.COMPATIBLE, "1.99", "1.995")
        check(EqualityLevel.COMPATIBLE, "0.05", "5.40000014e-02")

        rnd = random.Random(42)
        for _ in range(10000):
            value = (rnd.random() - 0.5) * 10**rnd.randint(0, 10)
            formatted0 = "{:.{prec}g}".format(value, prec=rnd.randint(1, 7))
            formatted1 = "{:.{prec}g}".format(value, prec=rnd.randint(1, 7))
            comparer = DecimalComparer(",", 0.01)
            level = comparer.compare_strings(formatted0, formatted1)
            self.assertGreater(level.value, EqualityLevel.CLOSE.value)

    def test_sig_figs(self):
        self.assertEqual(5, DecimalComparer._sig_figs("12.345"))
        self.assertEqual(3, DecimalComparer._sig_figs("0.0123"))
        self.assertEqual(4, DecimalComparer._sig_figs("+1.234e-10"))
        self.assertEqual(3, DecimalComparer._sig_figs("1.23E+10"))
        self.assertEqual(7, DecimalComparer._sig_figs("-765.4321"))
        self.assertEqual(1, DecimalComparer._sig_figs("8"))
        self.assertEqual(10, DecimalComparer._sig_figs("-12345.12345e11"))
        self.assertEqual(-1, DecimalComparer._sig_figs("not a number"))
        self.assertEqual(-1, DecimalComparer._sig_figs("nan"))
        self.assertEqual(-1, DecimalComparer._sig_figs("inf"))

    def test_compare_linelists_numerically_equal(self):
        self.assertIsNone(
            self.comparer.compare_line_lists(
                ["same1", "same2\tsame2", "same\t3.00\t0", "same4\tsame4"],
                ["same1", "same2\tsame2", "same\t3.0\t0.0", "same4\tsame4"],
            ))
        self._check_totals_counts(0, 0, 0, 2, 6)

    def test_compare_linelists_numerically_unequal(self):
        self.assertIsInstance(self.comparer.compare_line_lists(
                ["same1", "same2\tsame2", "same\t3.1\t0", "same4\tsame4"],
                ["same1", "same2\tsame2", "same\t3.0\t0.0", "same4\tsame4"],
            ), str)
        self._check_totals_counts(1, 0, 0, 1, 6)

    def test_compare_linelists_modulo_quotation_marks(self):
        self.assertIsNone(
            self.comparer.compare_line_lists(
                ["one\ttwo\tthree"],
                ["one\t\"two\"\tthree"]
            ))


if __name__ == "__main__":
    unittest.main()
