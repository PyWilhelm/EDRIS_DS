#!/usr/bin/env python
# -*- coding: utf-8 -*-
from TaskController.BaseClass.BaseReporter import BaseReporter as brp


class ReporterSPSPlot(brp):

    def __init__(self, metatask):
        brp.__init__(self, metatask)
        self.final = []

    def set_data(self):
        for task in self.successful:
            result = task['result']
            self.final.append(result)

    def report(self, method=''):
        return brp.report(self)
