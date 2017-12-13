import os
import sys

from pyreleaseplugin import CleanCommand, ReleaseCommand, PyTest
from setuptools import find_packages, setup, Command


def read(fname):
    """Utility function to read the README file into the long_description."""
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


install_requires_list = []
tests_require = ["pytest>=2.9"]


version_file = "pyreleaseplugin/_version.py"
with open(version_file) as fp:
    exec(fp.read())

setup(
    name="pyreleaseplugin",
    version=__version__,
    author="Devils Team",
    author_email="_CP_RD_Team_Devils@manh.com",
    description="A setuptools plugin for simplifying the release of Python modules",
    install_requires=install_requires_list,
    tests_require=tests_require,
    include_package_data=True,
    packages=find_packages(exclude=["tests"]),
    cmdclass={"test": PyTest, "clean": CleanCommand, "release": ReleaseCommand})
