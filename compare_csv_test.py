#!/usr/bin/env python3

import compare_csv
import unittest


class CompareCsvTest(unittest.TestCase):

    def test_compare_fields_equal(self):
        fields = ["one", "two", 3.5, -10.7]
        self.assertTrue(
            compare_csv.compare_fields(fields, fields)
        )
