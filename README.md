# comparedecimal

A package to compare decimal representations of floating-point numbers,
including a command-line tool to report on the similarity between data in
CSV files.

## Installation

The `comparedecimal` package can be installed from source by running `pip3
install .` or `python3 setup.py` within its directory. The command-line
utility `comparecsv` will be installed as part of the package.

## Command-line usage

`comparecsv` is a command line utility for finding duplicates among
delimited textual files containing numerical data (e.g. CSV files), even
when the string representations of the data differ.

`comparecsv` takes as its arguments two delimited files with the same
layout (i.e. same number of rows and columns) and compares them field by
field. For each pair of corresponding fields, it determines a level of
equality:

1. Identical: the character strings are equal.

2. Numerically equal: the character strings, when parsed as floating-point
   decimals, produce numbers which are equal.

3. Compatible: there exists a single floating-point number which, when
   formatted, could produce both the string representations. Under this
   definition, for example, "1.9" and "1.95" would be compatible, because
   they are both valid representations of 1.949. This equality level is
   particularly useful for finding duplicate files with differing levels
   of precision.

4. Close: The character strings are unequal and cannot represent the same
   number, but the values they represent are within 1% of each other
   (formally: denoting the represented values by a and b, they are close
   if have the same sign and `max(abs(a), abs(b)) <= 1.01 * min(abs(a),
   abs(b)))`. This equality level is useful for finding ‘duplicate’ files
   generated from the same data in which truncation or rounding errors
   have caused values to diverge slightly.

5. Unequal: The character strings are unequal and cannot represent
   the same number, and the values they represent are not close in the sense
   defined above.

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
