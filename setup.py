#!/usr/bin/env python

from setuptools import setup

setup(
    name="exec-wrappers",
    version="1.1.2",
    author="Guilherme Quentel Melo",
    author_email="gqmelo@gmail.com",
    url="https://github.com/gqmelo/exec-wrappers",
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    description="wrappers for running commands that need some initial setup",
    long_description=open("README.rst").read(),
    packages=["exec_wrappers"],
    entry_points={
        "console_scripts": "create-wrappers = exec_wrappers.create_wrappers:main"
    },
    package_data={"exec_wrappers": ["templates/*/*"]},
    include_package_data=True,
    install_requires=[],
)
