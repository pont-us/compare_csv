#!/usr/bin/env python3

import compare_csv
import unittest


class TestCompareCsv(unittest.TestCase):

    def test_compare_fields_equal(self):
        fields = ["one", "two", "3.5", "-10.7"]
        self.assertIsNone(
            compare_csv.compare_fields(fields, fields)
        )

    def test_compare_fields_unequal(self):
        self.assertTrue(
            isinstance(compare_csv.compare_fields(
                ["one", "two", "3.5", "-10.7"],
                ["one", "3.5", "-10.7"]), str))

    def test_compare_fields_numerically_equal(self):
        self.assertIsNone(compare_csv.compare_fields(
            ["wibble", "3.5", "-10.00000"], ["wibble", "3.500", "-10"]))

    def test_compare_fields_numerically_unequal(self):
        self.assertTrue(
            isinstance(compare_csv.compare_fields(
                ["wibble", "3.5", "-10.00000"],
                ["wibble", "3.500", "-10.00001"]), str))

    def test_compare_lines_equal(self):
        line0 = "one\ttwo\t3.5\t4.0"
        self.assertIsNone(compare_csv.compare_lines(line0, line0))

    def test_compare_lines_unequal(self):
        self.assertTrue(isinstance(
            compare_csv.compare_lines("Something", "Something else"), str))

    def test_compare_lines_numerically_equal(self):
        self.assertIsNone(
            compare_csv.compare_lines("one\ttwo\t3.5\t4.0",
                                      "one\ttwo\t3.500\t4", "\t"))

    def test_compare_lines_numerically_unequal(self):
        self.assertTrue(isinstance(
            compare_csv.compare_lines("one\ttwo\t3.5\t4.0",
                                      "one\ttwo\t3.500\t4.0001", "\t"), str))



if __name__ == "__main__":
    unittest.main()
