#!/usr/bin/env python3

import compare_csv
from compare_csv import CsvComparer, EqualityLevel
import unittest
import random


class TestCompareCsv(unittest.TestCase):

    def setUp(self):
        self.comparer = compare_csv.CsvComparer(separator="\t")

    def test_compare_fields_equal(self):
        fields = ["one", "two", "3.5", "-10.7"]
        self.assertIsNone(
            self.comparer.compare_fields(fields, fields)
        )

    def test_compare_fields_unequal(self):
        self.assertTrue(
            isinstance(self.comparer.compare_fields(
                ["one", "two", "3.5", "-10.7"],
                ["one", "3.5", "-10.7"]), str))

    def test_compare_fields_numerically_equal(self):
        self.assertIsNone(self.comparer.compare_fields(
            ["wibble", "3.5", "-10.00000"], ["wibble", "3.500", "-10"]))

    def test_compare_fields_numerically_unequal(self):
        self.assertTrue(
            isinstance(self.comparer.compare_fields(
                ["wibble", "3.5", "-10.00000"],
                ["wibble", "3.500", "-11.00000"]), str))

    def test_compare_field(self):
        def check(expected, string0, string1):
            actual = CsvComparer.compare_field(string0, string1)
            self.assertEqual(expected, actual)

        check(EqualityLevel.UNEQUAL, "1", "2")
        check(EqualityLevel.IDENTICAL, "1", "1")
        check(EqualityLevel.NUMERICALLY_EQUAL, "1.000000", "1")
        check(EqualityLevel.COMPATIBLE, "1.1", "1")
        check(EqualityLevel.COMPATIBLE, "123.456", "123.46")
        check(EqualityLevel.UNEQUAL, "123.456", "123.460")
        check(EqualityLevel.UNEQUAL, "-123", "123")
        check(EqualityLevel.COMPATIBLE, "+14.271e3", "1.427e4")
        check(EqualityLevel.UNEQUAL, "-8.912E-3", "-89.13E-4")
        check(EqualityLevel.COMPATIBLE, "-8.912E-3", "-89.1E-4")
        check(EqualityLevel.NUMERICALLY_EQUAL, "0", "0.000")
        check(EqualityLevel.NUMERICALLY_EQUAL, "-0", "0")
        check(EqualityLevel.COMPATIBLE, "-5.99e3", "-5994")
        check(EqualityLevel.UNEQUAL, "foo", "bar")
        check(EqualityLevel.IDENTICAL, "foo", "foo")
        check(EqualityLevel.COMPATIBLE, "-1.8850E-6", "-1.89E-06")
        check(EqualityLevel.COMPATIBLE, "4.3458E-5", "4.35E-05")
        check(EqualityLevel.COMPATIBLE, "9.9952E-8", "1.00E-07")
        check(EqualityLevel.UNEQUAL, "1.50", "1.49")
        check(EqualityLevel.UNEQUAL, "2.0", "1.94")

        rnd = random.Random(42)
        for _ in range(10000):
            value = (rnd.random() - 0.5) * 10**rnd.randint(0, 10)
            string0 = "{:.{prec}g}".format(value, prec=rnd.randint(1, 7))
            string1 = "{:.{prec}g}".format(value, prec=rnd.randint(1, 7))
            level = CsvComparer.compare_field(string0, string1)
            self.assertGreater(level, EqualityLevel.UNEQUAL)

    def test_sig_figs(self):
        self.assertEqual(5, CsvComparer.sig_figs("12.345"))
        self.assertEqual(4, CsvComparer.sig_figs("+1.234e-10"))
        self.assertEqual(3, CsvComparer.sig_figs("1.23E+10"))
        self.assertEqual(7, CsvComparer.sig_figs("-765.4321"))
        self.assertEqual(1, CsvComparer.sig_figs("8"))
        self.assertEqual(10, CsvComparer.sig_figs("-12345.12345e11"))
        self.assertEqual(-1, CsvComparer.sig_figs("not a number"))
        self.assertEqual(-1, CsvComparer.sig_figs("nan"))
        self.assertEqual(-1, CsvComparer.sig_figs("inf"))

    def test_compare_linelists_numerically_equal(self):
        self.assertIsNone(
            self.comparer.compare_linelists(
                ["same1", "same2\tsame2", "same\t3.00\t0", "same4\tsame4"],
                ["same1", "same2\tsame2", "same\t3.0\t0.0", "same4\tsame4"],
            ))

    def test_compare_linelists_numerically_unequal(self):
        self.assertTrue(isinstance(
            self.comparer.compare_linelists(
                ["same1", "same2\tsame2", "same\t3.1\t0", "same4\tsame4"],
                ["same1", "same2\tsame2", "same\t3.0\t0.0", "same4\tsame4"],
            ), str))

    def test_compare_linelists_modulo_quotation_marks(self):
        self.assertIsNone(
            self.comparer.compare_linelists(
                ["one\ttwo\tthree"],
                ["one\t\"two\"\tthree"]
            ))


if __name__ == "__main__":
    unittest.main()
