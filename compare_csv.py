#!/usr/bin/env python3

"""
compare_csv: determine similarity of data in delimited text files

compare_csv reads two files in CSV or another delimited format,
and reports on how similar their data fields are.

Copyright 2018 Pontus Lurcock.

compare_csv is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

compare_csv is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with compare_csv.  If not, see <http://www.gnu.org/licenses/>.
"""


from typing import List, Optional
import argparse
import csv
import re
import math
from enum import IntEnum, Enum
from collections import namedtuple


class EqualityLevel(Enum):
    UNEQUAL = (1, "unequal")     # there is no number which formats as both strings
    COMPATIBLE = (2, "compatible")  # the same float could be formatted as both strings
    NUMERICALLY_EQUAL = (3, "numerically equal")        # strings can be parsed to equal floats
    IDENTICAL = (4, "identical")   # the strings themselves are identical

    def __new__(cls, value, description):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        return obj


FieldDifference = namedtuple("FieldDifference", "field_index string0 string1")


class CsvComparer:

    def __init__(self, separator=","):
        self.separator = separator
        self.totals = {level: 0 for level in EqualityLevel}
        self.first_difference_field = None

    @staticmethod
    def compare_field(string0: str, string1: str) -> EqualityLevel:
        if string0 == string1:
            return EqualityLevel.IDENTICAL

        try:
            floats = [float(s) for s in (string0, string1)]
            sig_figs = [CsvComparer.sig_figs(s) for s in (string0, string1)]
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
        # Next step is to compare_field the digits.

        digits = [CsvComparer.extract_mantissa_digits(s)
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
            return EqualityLevel.UNEQUAL

    @staticmethod
    def extract_mantissa_digits(literal: str) -> Optional[str]:
        match = re.match(r"^[-+]?([0-9]*)\.?([0-9]+)([eE][-+]?[0-9]+)?$",
                         literal)
        if match is None:
            return None
        return match.group(1) + match.group(2)

    @staticmethod
    def sig_figs(literal: str) -> int:
        match = re.match(r"^[-+]?([0-9]*)\.?([0-9]+)([eE][-+]?[0-9]+)?$",
                         literal)
        if match is None:
            return -1
        return sum([len(match.group(i)) for i in (1, 2)])

    def compare_fields(self, fields0: List[str], fields1: List[str]) ->\
            Optional[FieldDifference]:
        """
        Compare two lists of strings. If they're equal, return none.
        If not, return a string describing how they differ. The definition
        of equality includes the possibility that two strings are different
        decimal representations of the same number (e.g. "3" and "3.00").
        It also includes the possibility that the strings are representations
        of two sufficiently close numbers. ("Sufficiently close" is not
        yet well-defined but will be made configurable.)

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
            level = self.compare_field(fields0[i], fields1[i])
            self.totals[level] += 1
            if level == EqualityLevel.UNEQUAL and \
                    first_difference is None:
                first_difference = FieldDifference(
                    field_index=i, string0=fields0[i], string1=fields1[i]
                )

        return first_difference

    def compare_linelists(self, list0: List[str], list1: List[str]) ->\
            Optional[str]:

        if len(list0) != len(list1):
            return "Unequal numbers of lines ({}, {})".\
                format(len(list0), len(list1))

        fields = []
        for line_list in list0, list1:
            fields_list = []
            fields.append(fields_list)
            reader = csv.reader(line_list,
                                delimiter=self.separator,
                                skipinitialspace=True,)
            for row in reader:
                fields_list.append(row)

        first_difference = None
        for line in range(len(fields[0])):
            result = self.compare_fields(fields[0][line], fields[1][line])
            if result is not None and first_difference is None:
                if result.field_index == -1:
                    first_difference =\
                        "Differing numbers of fields on line {}".\
                        format(line+1)
                else:
                    first_difference = "On line {}: field {} differs ({}, {})".\
                           format(line+1, result.field_index+1,
                                  result.string0, result.string1)

        return first_difference


def main():
    parser = argparse.ArgumentParser(description="Compare two delimited files")
    parser.add_argument("-d", "--delimiter", type=str, required=False,
                        help="delimiter between fields", default=",")
    parser.add_argument("FILE1", type=str)
    parser.add_argument("FILE2", type=str)
    args = parser.parse_args()

    with open(args.FILE1) as fh:
        lines0 = fh.readlines()

    with open(args.FILE2) as fh:
        lines1 = fh.readlines()

    separator = bytes(args.delimiter, "utf-8").decode("unicode_escape")
    comparer = CsvComparer(separator=separator)
    result = comparer.compare_linelists(lines0, lines1)

    for level, count in sorted(list(comparer.totals.items()),
                               key=lambda x: x[0].value):
        print("{:10d} {}".format(count, level.description))

    if result is None:
        print("The files contain the same values.")
    else:
        print("First difference:", result)


if __name__ == "__main__":
    main()

