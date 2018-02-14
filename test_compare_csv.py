#!/usr/bin/env python3

import compare_csv
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

    def test_compare_lines_equal(self):
        line0 = "one\ttwo\t3.5\t4.0"
        self.assertIsNone(self.comparer.compare_lines(line0, line0))

    def test_compare_lines_unequal(self):
        self.assertTrue(isinstance(
            self.comparer.compare_lines("Something", "Something else"), str))

    def test_compare_lines_numerically_equal(self):
        self.assertIsNone(
            self.comparer.compare_lines("one\ttwo\t3.5\t4.0",
                                      "one\ttwo\t3.500\t4", "\t"))

    def test_compare_lines_numerically_unequal(self):
        self.assertTrue(isinstance(
            self.comparer.compare_lines("one\ttwo\t3.5\t4.0",
                                      "one\ttwo\t3.500\t4.4", "\t"), str))

    def test_compare_linelists_numerically_equal(self):
        self.assertIsNone(
            self.comparer.compare_linelists(
                ["same1", "same2,same2", "same,3.00,0", "same4,same4"],
                ["same1", "same2,same2", "same,3.0,0.0", "same4,same4"],
            ))

    def test_compare_linelists_numerically_unequal(self):
        self.assertTrue(isinstance(
            self.comparer.compare_linelists(
                ["same1", "same2,same2", "same,3.1,0", "same4,same4"],
                ["same1", "same2,same2", "same,3.0,0.0", "same4,same4"],
            ), str))


if __name__ == "__main__":
    unittest.main()
