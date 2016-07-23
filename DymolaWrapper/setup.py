from setuptools import setup, find_packages
import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "EDRIS wrapper",
    version = "dev",
    author = "Ziyang Li",
    author_email = "ziyang.li@bmw.de",
    keywords = "EDRIS wrapper",
    packages = find_packages()
)
