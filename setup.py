#!/usr/bin/python
# -*- coding: utf-8 -*-

"""setup.py for trivector"""

import sys
import os
from setuptools import setup, find_packages
from setuptools.command.test import test


class PyTest(test):
    user_options = [('pytest-args=', 'a', "Arguments to pass to pytest")]

    def initialize_options(self):
        test.initialize_options(self)
        self.pytest_args = "-v --cov=trivector"

    def run_tests(self):
        import shlex
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(shlex.split(self.pytest_args))
        sys.exit(errno)


def readme():
    with open("README.rst") as f:
        return f.read()


setup(
    name="trivector",
    version="0.0.0",
    description="",  # TODO
    long_description=readme(),
    author="Nathan Klapstein",
    author_email="nklapste@ualberta.ca",
    url="https://github.com/nklapste/trivector",  # TODO
    download_url="https://github.com/nklapste/trivector/",  # TODO
    packages=find_packages(exclude=["test"]),
    include_package_data=True,
    package_data={
        "": ["README.rst"],
    },
    entry_points={
        "console_scripts": [
            "trivector = trivector.__main__:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
    install_requires=[
        "svgwrite>=1.1.12,<2.0.0",
        "opencv-python>=3.4.1.15,<4.0.0.0",
        "numpy>=1.14.3,<2.0.0"
    ],
    tests_require=[
        "pytest",
        "pytest-cov",
        "pytest-timeout",
    ],
    cmdclass={"test": PyTest},
)
