#!/usr/bin/env python

"""
Call `pip install -e .` to install package locally for testing.
"""

from setuptools import setup

# Build setup.
setup(
    name="sproc",
    version="0.0.1",
    url="https://github.com/HenryLandis/sproc",
    author="Henry Landis",
    author_email="hnl2109@columbia.edu",
    description="A package to calculate species range overlap from occurrence data.",
)