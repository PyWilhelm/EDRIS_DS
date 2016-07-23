#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Specific exception class for the EDRIS simulation
"""
class Signal(Exception):
    """ Generic exception class """
    pass

class FileNotFound(Exception):
    """ Generic exception class """
    pass

class BuildError(Exception):
    """ Generic exception class """
    pass


class SimulationError(Exception):
    """ Generic exception class """
    pass

class ComparisonError(Exception):
    """ Generic exception class """
    pass

class OpenModelError(Exception):
    pass

class ModelNotFoundError(Exception):
    pass