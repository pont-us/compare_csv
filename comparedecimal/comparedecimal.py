#!/usr/bin/env python3

"""
comparedecimal: compare decimal representations of floating-point numbers

comparedecimal reads two files in CSV or another delimited format,
and reports on how similar their data fields are.

Copyright 2018, 2019 Pontus Lurcock.

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


import argparse
import csv
import math
import re
from collections import namedtuple
from enum import Enum
from typing import List, Optional


def main():
    """
    Compare two delimited files specified on the command line

    Run this module as a command-line utility with files and options
    specified as command-line arguments. The files will be read and
    compared using DecimalComparer.compare_line_lists, and the results
    of comparison written to the standard output in a human-readable
    format.

    :return: None
    """
    parser = argparse.ArgumentParser(
        description="Compare numbers in two delimited files",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-d", "--delimiter", type=str, required=False,
                        help="delimiter between fields", default=",")
    parser.add_argument("-t", "--threshold", type=float, required=False,
                        help="threshold for considering values \"close\", "
                             "as a decimal fraction of the smaller value",
                        default=0.01)
    parser.add_argument("FILE1", type=str)
    parser.add_argument("FILE2", type=str)
    args = parser.parse_args()

    with open(args.FILE1) as fh:
        lines0 = fh.readlines()

    with open(args.FILE2) as fh:
        lines1 = fh.readlines()

    separator = bytes(args.delimiter, "utf-8").decode("unicode_escape")
    comparer = DecimalComparer(separator=separator,
                               closeness_threshold=args.threshold)
    result = comparer.compare_line_lists(lines0, lines1)

    for level, count in sorted(list(comparer.totals.items()),
                               key=lambda x: x[0].value):
        print("{:10d} {}".format(count, level.description))

    if result is None:
        print("The files contain the same values.")
    else:
        print("First difference:", result)


class EqualityLevel(Enum):
    """
    Represents the degree of similarity between two strings.

    UNEQUAL
      The strings are unequal at the character level, and
      there is no float which could be formatted as both strings.
      (e.g. "foo" and "bar"; "1" and "2")

    CLOSE
      The strings represent numbers which are within 1% of each other.
      Specifically, abs(max(a, b)) <= abs(min(a, b)) * 1.01

    COMPATIBLE
      The strings are unequal at the character level, but
      the same float could be formatted as both strings.
      (e.g. "1.1" and "1")

    NUMERICALLY_EQUAL
      The strings are unequal at the character level, but
      they can be parsed to floats which have the same value.
      (e.g. "1" and "1.0")

    IDENTICAL
      The strings are identical at the character level.
      (e.g. "foo" and "foo"; "3.14" and "3.14")
    """

    UNEQUAL = (1, "unequal")
    CLOSE = (2, "close")
    COMPATIBLE = (3, "compatible")
    NUMERICALLY_EQUAL = (4, "numerically equal")
    IDENTICAL = (5, "identical")

    def __new__(cls, value, description):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        return obj


FieldDifference = namedtuple("FieldDifference", "field_index string0 string1")


class DecimalComparer:
    """
    A class to compare delimited string representations of numerical data.

    An instance of this class maintains a count of the total number
    of comparison results for each equality level, which can be helpful in
    providing an overview of the similarity between two files. This count is
    stored in the instance attribute ``totals``.
    """

    def __init__(self, separator: str = ",", closeness_threshold: float = 0.01):
        """
        Create a new comparer.

        :param separator: the field separator to use when comparing lines
        :param closeness_threshold: the threshold used to determine whether
               two values are close, as a fraction. Values a and b are regarded
               as close if they have the same sign and
               max(abs(a), abs(b)) <= (1 + closeness_threshold) *
               min(abs(a), abs(b)).
        """
        self.separator = separator  # type: str
        """the field separator to use when comparing lines"""
        self.totals = {level: 0 for level in EqualityLevel}  # type: dict
        """an accumulator to count comparison results for each equality level"""
        self.closeness_threshold = closeness_threshold  # type: float
        """the fractional threshold at which values are regarded as close"""

    def compare_strings(self, decimal0: str, decimal1: str) -> EqualityLevel:
        """
        Compare two strings, attempting to interpret them as decimal numbers.
        This object's ``totals`` attribute will be updated with the result
        of the comparison.

        :param decimal0: a string
        :param decimal1: another string
        :return: the level of equality which the two strings have when
           interpreted as decimal representations of real numbers
        """
        level = self._compare_strings(decimal0, decimal1)
        self.totals[level] += 1
        return level

    def _compare_strings(self, string0: str, string1: str) -> EqualityLevel:
        if string0 == string1:
            return EqualityLevel.IDENTICAL

        try:
            floats = [float(s) for s in (string0, string1)]
            sig_figs =\
                [DecimalComparer._sig_figs(s) for s in (string0, string1)]
        except ValueError:
            # If the strings are unequal and one or both can't be parsed
            # as floats, then they're clearly numerically unequal.
            return EqualityLevel.UNEQUAL

        if floats[0] == floats[1]:
            # This catches the case where we're comparing -0 with 0,
            # which would otherwise return an incorrect False result.
            # It should also catch most other "numerically equal" cases,
            # but if any slip through due to the uncertainties of
            # floating-point equality testing, they will be caught later.
            return EqualityLevel.NUMERICALLY_EQUAL

        if math.copysign(floats[0], floats[1]) != floats[0]:
            # opposite signs (and we know they're non-zero)
            return EqualityLevel.UNEQUAL

        positives = [abs(x) for x in floats]

        if positives[0] >= positives[1] * 10 or \
           positives[1] >= positives[0] * 10:
            return EqualityLevel.UNEQUAL
        # We've now established that they have the same order of magnitude.
        # Next step is to compare the digits.

        digits = [DecimalComparer._extract_mantissa_digits(s)
                  for s in (string0, string1)]
        digits_padded = \
            [digits[i] + ("0" * (max(sig_figs) - sig_figs[i])) for i in (0, 1)]
        max_diff = 10**(max(sig_figs) - min(sig_figs)) // 2

        ints = [int(d) for d in digits_padded]

        # This is a bit of a hack to account for the rare cases where
        # the two numbers straddle a power of ten (e.g. 9.9952E-8 vs. 1.00E-07).
        # In this case the sig. fig. counting technique puts us out by
        # an order of magnitude. We do a straightforward empirical check to
        # correct this, also checking the parsed float values to make sure
        # that we're not "correcting" a real difference in the original numbers.
        if ints[0] * 9 < ints[1] and positives[0] * 9 >= positives[1]:
            ints[0] *= 10
        if ints[1] * 9 < ints[0] and positives[1] * 9 >= positives[0]:
            ints[1] *= 10

        actual_diff = abs(ints[0] - ints[1])
        if actual_diff == 0:
            return EqualityLevel.NUMERICALLY_EQUAL
        elif actual_diff <= max_diff:
            return EqualityLevel.COMPATIBLE
        else:
            return self._unequal_or_close(positives[0], positives[1])

    def compare_string_lists(self, fields0: List[str], fields1: List[str]) ->\
            Optional[FieldDifference]:
        """
        Compare two lists of strings. If they're equal, return None. If not,
        return a FieldDifference object describing how they differ. Strings
        are considered equal if they have anything other than an
        EqualityLevel.UNEQUAL level of equality. "Equality" therefore
        includes the possibility that two strings are different decimal
        representations of the same number (e.g. "3.0" and "3.01").
        This object's ``totals`` attribute will be updated with the results
        of the comparisons.

        :param fields0: a list of strings
        :param fields1: another list of strings
        :return: None if lists equal, otherwise a FieldDifference object
        """

        if len(fields0) != len(fields1):
            return FieldDifference(field_index=-1,
                                   string0="{}".format(len(fields0)),
                                   string1="{}".format(len(fields1)))

        first_difference = None
        for i in range(len(fields0)):
            level = self.compare_strings(fields0[i], fields1[i])
            if level == EqualityLevel.UNEQUAL and \
                    first_difference is None:
                first_difference = FieldDifference(
                    field_index=i, string0=fields0[i], string1=fields1[i]
                )

        return first_difference

    def compare_line_lists(self, lines0: List[str], lines1: List[str]) ->\
            Optional[str]:
        """
        Compare two lists of lines, each containing multiple fields.
        This object's ``separator`` object will be used as the separator
        when splitting a line into fields.
        This object's ``totals`` attribute will be updated
        with the results of the comparisons.

        :param lines0: a list of lines
        :param lines1: another list of lines
        :return: a string describing the first difference, or ``None``
           if the lists are equal
        """

        if len(lines0) != len(lines1):
            return "Unequal numbers of lines ({}, {})".\
                format(len(lines0), len(lines1))

        fields = []
        for line_list in lines0, lines1:
            fields_list = []
            fields.append(fields_list)
            reader = csv.reader(line_list,
                                delimiter=self.separator,
                                skipinitialspace=True)
            for row in reader:
                fields_list.append(row)

        first_difference = None
        for line in range(len(fields[0])):
            result = self.compare_string_lists(fields[0][line], fields[1][line])
            if result is not None and first_difference is None:
                if result.field_index == -1:
                    first_difference = \
                        "Differing numbers of fields on line {}". \
                        format(line+1)
                else:
                    first_difference = \
                        "On line {}: field {} differs ({}, {})". \
                        format(line + 1, result.field_index + 1,
                               result.string0, result.string1)

        return first_difference

    def _unequal_or_close(self, a: float, b: float) -> EqualityLevel:
        if max(a, b) <= min(a, b) * (1 + self.closeness_threshold):
            return EqualityLevel.CLOSE
        else:
            return EqualityLevel.UNEQUAL

    @staticmethod
    def _extract_mantissa_digits(literal: str) -> Optional[str]:
        match = re.match(r"^[-+]?([0-9]*)\.?([0-9]+)([eE][-+]?[0-9]+)?$",
                         literal)
        if match is None:
            return None
        return (match.group(1) + match.group(2)).lstrip("0")

    @staticmethod
    def _sig_figs(literal: str) -> int:
        digits = DecimalComparer._extract_mantissa_digits(literal)
        return -1 if digits is None else len(digits)


if __name__ == "__main__":
    main()
