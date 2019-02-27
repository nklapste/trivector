#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""setup.py for trivector"""

import codecs
import re
import sys
import os
from setuptools import setup, find_packages
from setuptools.command.test import test


def find_version(*file_paths):
    with codecs.open(os.path.join(os.path.abspath(os.path.dirname(__file__)), *file_paths), 'r') as fp:
        version_file = fp.read()
    m = re.search(r"^__version__ = \((\d+), ?(\d+), ?(\d+)\)", version_file, re.M)
    if m:
        return "{}.{}.{}".format(*m.groups())
    raise RuntimeError("Unable to find a valid version")


VERSION = find_version("trivector", "__init__.py")


class Pylint(test):
    user_options = [('pylint-args=', 'a', "Arguments to pass to pylint")]

    def initialize_options(self):
        test.initialize_options(self)
        self.pylint_args = "trivector --persistent=y --rcfile=.pylintrc --output-format=colorized"

    def run_tests(self):
        import shlex
        # import here, cause outside the eggs aren't loaded
        from pylint.lint import Run
        Run(shlex.split(self.pylint_args))


class PyTest(test):
    user_options = [('pytest-args=', 'a', "Arguments to pass to pytest")]

    def initialize_options(self):
        test.initialize_options(self)
        self.pytest_args = "-v --cov={}".format("trivector")

    def run_tests(self):
        import shlex
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(shlex.split(self.pytest_args))
        sys.exit(errno)


def readme():
    with open("README.rst", encoding="utf-8") as f:
        return f.read()


setup(
    name="trivector",
    version=VERSION,
    description="Convert an image into a ``.svg`` vector image composed of triangles",
    long_description=readme(),
    author="Nathan Klapstein",
    author_email="nklapste@ualberta.ca",
    url="https://github.com/nklapste/trivector",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Multimedia :: Graphics :: Editors :: Vector-Based",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
    ],
    packages=find_packages(exclude=["test"]),
    include_package_data=True,
    install_requires=[
        "svgwrite>=1.1.12,<2.0.0",
        "opencv-python>=3.4.1.15,<4.0.0.0",
        "numpy>=1.14.3,<2.0.0",
        "progressbar2>=3.37.1,<4.0.0",
    ],
    tests_requires=[
        "pytest>=2.8.7,<4.0.0",
        "pytest-cov<=2.6.0",
        "pylint>=1.9.1,<2.0.0",
        "svglib>=0.9.0,<1.0.0"
    ],
    extras_require={
        "docs": [
            "sphinx>=1.7.5,<2.0.0",
            "sphinx_rtd_theme>=0.3.1,<1.0.0",
            "sphinx-autodoc-typehints>=1.3.0,<2.0.0",
            "sphinx-argparse>=0.2.2,<1.0.0",
        ],
    },
    cmdclass={"test": PyTest, "lint": Pylint},
    entry_points={
        "console_scripts": [
            "trivector = trivector.__main__:main"
        ]
    },
)
