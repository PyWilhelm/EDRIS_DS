#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "EDRIS Scheduler",
    version = "dev",
    author = "Ziyang Li",
    author_email = "ziyang.li@bmw.de",
    keywords = "EDRIS Scheduler Master Tasks",
    url = "http://packages.python.org/an_example_pypi_project",
    packages=['edris_server'],
    long_description=read('README.TXT'),
)