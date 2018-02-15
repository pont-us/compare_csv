#!/usr/bin/env python3

import compare_csv
from compare_csv import CsvComparer
import unittest


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

    def test_are_equal_to_given_precision(self):
        def check(result, string0, string1):
            self.assertEqual(result, CsvComparer.
                             are_equal_to_given_precision(string0, string1))

        check(False, "1", "2")
        check(True, "1", "1")
        check(True, "1.000000", "1")
        check(True, "1.1", "1")
        check(True, "123.456", "123.46")
        check(False, "123.456", "123.460")
        check(False, "-123", "123")
        check(True, "+14.271e3", "1.427e4")
        check(False, "-8.912E-3", "-89.13E-4")
        check(True, "-8.912E-3", "-89.1E-4")
        check(True, "0", "0.000")
        check(True, "-0", "0")
        check(True, "-5.99e3", "-5994")
        check(False, "foo", "bar")
        check(True, "-1.8850E-6", "-1.89E-06")
        check(True, "4.3458E-5", "4.35E-05")
        check(True, "9.9952E-8", "1.00E-07")

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
