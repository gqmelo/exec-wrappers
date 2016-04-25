#!/usr/bin/env python

import sys
from glob import glob

if 'develop' in sys.argv:
    from setuptools import setup
else:
    from distutils.core import setup

setup(
    name="conda-wrappers",
    version='0.1',
    author="Guilherme Quentel Melo",
    author_email="gqmelo@gmail.com",
    url="https://github.com/gqmelo/conda-wrappers",
    license="BSD",
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
    description="wrappers for running commands inside a conda environment",
    long_description=open('README.rst').read(),
    packages=['conda_wrappers'],
    scripts=glob('bin/*'),
    install_requires=['conda'],
)
