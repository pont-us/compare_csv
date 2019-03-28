# compare_csv.py

A tool to determine whether delimited text files contain essentially the
same data.

## Description

compare_csv is a utility for finding duplicates among delimited textual
files containing numerical data (e.g. CSV files), even when the string
representations of the data differ.

compare_csv takes two delimited files with the same layout (i.e. same
number of rows and columns) and compares them field by field. For
each pair of corresponding fields, it determines a level of equality:

1. Identical: the character strings are equal.

2. Numerically equal: the character strings, when parsed as
   floating-point decimals, produce numbers which are equal.

3. Compatible: there exists a single floating-point number which,
   when formatted, could produce both the string representations.
   Under this definition, for example, "1.9" and "1.95" would be
   compatible, because they are both valid representations of 1.949.
   This equality level is particularly useful for finding duplicate
   files with differing levels of precision.

4. Unequal: The character strings are unequal and cannot represent
   the same number.

When run on two files, compare_csv prints total counts for field pairs
at each level of equality.

## License

Copyright 2018, 2019 Pontus Lurcock
pont@talvi.net

Released under the GNU GPL v3; see the file COPYING for details.
