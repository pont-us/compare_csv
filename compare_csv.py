#!/usr/bin/env python3

from typing import List, Optional
import argparse
import csv


class CsvComparer:

    def __init__(self, separator=","):
        self.separator = separator
        self.precision = 0.001

    def are_essentially_equal(self, string0: str, string1: str) -> bool:
        if string0 == string1:
            return True

        try:
            f0 = float(string0)
            f1 = float(string1)
            smaller = min(f0, f1)
            fudge_factor = abs(smaller * self.precision)
            return abs(f0-f1) <= fudge_factor
        except ValueError:
            # not equal as strings, and not interpretable as a
            # float, so unequal
            return False

    def compare_fields(self, fields0: List[str], fields1: List[str]) ->\
            Optional[str]:
        """
        Compare two lists of strings. If they're equal, return none.
        If not, return a string describing how they differ. The definition
        of equality includes the possibility that two strings are different
        decimal representations of the same number (e.g. "3" and "3.00").

        :param fields0: a list of strings
        :param fields1: another list of strings
        :return: None if lists equal, otherwise
        """

        if len(fields0) != len(fields1):
            return "Lengths differ ({}, {})".format(len(fields0), len(fields1))

        for i in range(len(fields0)):
            if not self.are_essentially_equal(fields0[i], fields1[i]):
                return "field {} differs ({}, {})".format(
                    i+1, fields0[i], fields1[i])

        return None

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

        for line in range(len(fields[0])):
            result = self.compare_fields(fields[0][line], fields[1][line])
            if result is not None:
                return "On line {}: ".format(line+1)+result

        return None


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
    if result is None:
        print("The files contain the same values.")
    else:
        print(result)


if __name__ == "__main__":
    main()

