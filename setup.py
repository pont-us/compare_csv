import setuptools
import os.path

cwd = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(cwd, "README.md")) as fh:
    long_desc = fh.read()

setuptools.setup(
    name="comparedecimal",
    version="1.0.0",
    packages=["comparedecimal"],
    url="https://github.com/pont-us/comparedecimal",
    license="GNU GPLv3+",
    author="Pontus Lurcock",
    author_email="pont@talvi.net",
    description=
    "Compare decimal representations of floating-point numbers.",
    long_description_content_type="text/markdown",
    long_description=long_desc,
    classifiers=["Development Status :: 5 - Production/Stable",
                 "License :: OSI Approved :: "
                 "GNU General Public License v3 or later (GPLv3+)",
                 "Topic :: Scientific/Engineering :: Information Analysis",
                 "Environment :: Console",
                 "Programming Language :: Python :: 3",
                 "Intended Audience :: Science/Research"
                 ],
    entry_points={"console_scripts":
                  ["comparecsv=comparedecimal.comparedecimal:main"]
                  }
)
