#!/usr/bin/env python3

from typing import List, Optional


def are_equal_numerical(string0: str, string1: str) -> bool:
    if string0 == string1:
        return True

    try:
        return float(string0) == float(string1)
    except ValueError:
        # not equal as strings, and not interpretable as a
        # float, so unequal
        return False


def compare_fields(fields0: List[str], fields1: List[str]) -> Optional[str]:
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
        if not are_equal_numerical(fields0[i], fields1[i]):
            return "field {} differs ({}, {})".format(i, fields0[i], fields1[i])

    return None


def compare_lines(line0: str, line1: str, separator=",") -> Optional[str]:
    stripped = (line0.strip(), line1.strip())
    if stripped[0] == stripped[1]:
        return None

    fields = [s.split(separator) for s in stripped]
    return compare_fields(*fields)
