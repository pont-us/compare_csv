# comparedecimal

A package to compare decimal representations of floating-point numbers,
including a command-line tool to report on the similarity between data in
CSV files.

## Installation

The `comparedecimal` package can be installed from source by running `pip3
install .` or `python3 setup.py` within its directory. The command-line
utility `comparecsv` will be installed as part of the package.

## Rationale

I wrote this tool to help me when organizing and tidying up scientific
data sets. It occasionally happens that I come across two files which I
suspect contain the same data, but because they've been through different
processing steps, the values are no longer byte-for-byte identical – for
example, a CSV file may have been opened in Excel and saved again,
truncating the number of decimal places in the floating-point values. In
these cases, it's useful to be able to ascertain how compatible the files
are – is it possible that one is a lower-precision version of the other
(e.g. ‘2.0’ and ‘1.99’)? Or that the numerical values are in fact
identical but the strings representing them differ (e.g. ‘1234’ and
‘1.234e3’)? `comparedecimal` provides a Python package and command-line
tool to answer such questions.

## Equality levels

For any pair of strings, `comparedecimal` determines one of five equality
levels between them. The highest possible equality level is always given,
so for instance a pair of strings which is both ‘compatible’ and ‘close’
will be classified as ‘compatible’. The equality levels are as follows:

1. Identical: the character strings are equal.

2. Numerically equal: the character strings, when parsed as floating-point
   decimals, produce numbers which are equal.

3. Compatible: there exists a single floating-point number which, when
   formatted, could produce both the string representations. Under this
   definition, for example, "1.9" and "1.95" would be compatible, because
   they are both valid representations of 1.949. This equality level is
   particularly useful for finding duplicate files with differing levels
   of precision.

4. Close: the difference between the numbers represented by the character
   strings is below a certain threshold (formally: denoting the
   represented values by `a` and `b` and the threshold by `t`, they are
   close if have the same sign and `max(abs(a), abs(b)) <= (1 + t) *
   min(abs(a), abs(b)))`. This equality level is useful for finding
   ‘duplicate’ files generated from the same data in which truncation or
   rounding errors have caused values to diverge slightly.

5. Unequal: The character strings are unequal and cannot represent
   the same number, and the values they represent are not close in the sense
   defined above.

## The `comparedecimal` package

The `comparedecimal` package provides the class `DecimalComparer`, which
is initialized with a separator string (used to divide lines for multi-field
comparisons) and a threshold (used to define the `Close` equality level
described above). The class provides the following methods:

- `compare_strings` to compare individual strings
- `compare_string_lists` to compare lists of strings
- `compare_line_lists` to compare lists of lines, using the predefined
  separator to split each line into strings

`DecimalComparer` has an instance variable `totals`. `totals` is a
dictionary with a key for each equality level (represented by the
`EqualityLevel` enum). The associated value for each equality level is
an integer representing the total number of comparisons made so far
which resulted in this equality level.

## The `comparecsv` command-line tool

`comparecsv` is a command line utility for finding duplicates among
delimited textual files containing numerical data (e.g. CSV files), even
when the string representations of the data differ.

`comparecsv` takes as its arguments two delimited files with the same
layout (i.e. same number of rows and columns) and compares them field by
field. For each pair of corresponding fields, it determines a level of
equality as defined above.

When run on two files, `comparecsv` prints total counts for field pairs
at each level of equality. For every field pair, the highest possible
equality level is given: for instance, if two fields are not identical but
are numerically equal, then they will (by definition) also be compatible
and close; in this case, `comparecsv` will report the equality level
‘numerically equal’.

## License

Copyright 2018, 2019 Pontus Lurcock
pont@talvi.net

Released under the GNU GPL v3; see the file COPYING for details.
