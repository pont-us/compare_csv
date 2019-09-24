import setuptools
import os.path

cwd = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(cwd, "README.md")) as fh:
    long_desc = fh.read()

setuptools.setup(
    name="compare_csv",
    version="1.0.0",
    packages=["compare_csv"],
    url="https://github.com/pont-us/compare_csv",
    license="GNU GPLv3+",
    author="Pontus Lurcock",
    author_email="pont@talvi.net",
    description=
    "Determine whether delimited text files contain the same numerical data.",
    long_description_content_type="text/markdown",
    long_description=long_desc,
    classifiers=["Development Status :: 5 - Production/Stable",
                 "License :: OSI Approved :: "
                 "GNU General Public License v3 or later (GPLv3+)",
                 "Topic :: Scientific/Engineering",
                 "Programming Language :: Python :: 3",
                 "Intended Audience :: Science/Research"
                 ],
    entry_points={"console_scripts":
                      ["compare-csv=compare_csv.compare_csv:main"]
                  }
)
