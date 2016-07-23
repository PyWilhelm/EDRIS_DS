#!/usr/bin/env python
# -*- coding: utf-8 -*-

from BuildingTools.ScriptGenerator.SpecificBase import SpecificBase


class SpecificFMU(SpecificBase):

    def __init__(self, rules, specific_info):
        super(SpecificFMU, self).__init__(rules, specific_info)
