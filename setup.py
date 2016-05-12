#!/usr/bin/env python

import sys
from glob import glob

if 'develop' in sys.argv:
    from setuptools import setup
else:
    from distutils.core import setup

setup(
    name="exec-wrappers",
    version='0.1',
    author="Guilherme Quentel Melo",
    author_email="gqmelo@gmail.com",
    url="https://github.com/gqmelo/exec-wrappers",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
    ],
    description="wrappers for running commands that need some initial setup",
    long_description=open('README.rst').read(),
    packages=['exec_wrappers'],
    include_package_data=True,
    install_requires=[],
)
