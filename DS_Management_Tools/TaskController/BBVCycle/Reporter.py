#!/usr/bin/env python
# -*- coding: utf-8 -*-
from TaskController.BaseClass.BaseReporter import BaseReporter as brp


class ReporterBBVCycle(brp):

    def __init__(self, metatask):
        brp.__init__(self, metatask)
        self.final = []

    def set_data(self):
        for task in self.successful:
            result = task['result']
            self.final.append({'column': 'TestColumn', 'data': result['summary.batteryPower']})

    def report(self):
        self.set_data()
        return self.final
