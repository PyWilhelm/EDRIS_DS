#!/usr/bin/env python
# -*- coding: utf-8 -*-
from TaskController.BaseClass.BaseReporter import BaseReporter as brp

import copy
import HTML


class ReporterBBVData(brp):

    def __init__(self, metatask):
        brp.__init__(self, metatask)
        self.final = {}
        self.template = {'row': {'value': [], 'name': ''}, 'column': {'value': [], 'name': ''}, 'data': None}

    def set_head(self):
        d = self.metatask['taskGenerator']['arguments']['constant']['parameterOfFunction']['testArguments']['results']
        for k in d:
            table = copy.deepcopy(self.template)
            table['column']['name'] = 'setTemp'
            table['row']['name'] = 'Nothing'
            table['column']['value'] = [float(v)
                                        for v in self.get_dict_from_name(
                self.metatask['taskGenerator']['arguments']['variable'], 'setTemp')['value']]
            table['row']['value'] = [0]
            table['data'] = [['Nil' for _ in range(len(table['column']['value']))]
                             for __ in range(len(table['row']['value']))]
            self.final[k['signalName']] = table

    def set_data(self):
        self.set_head()
        for k in self.final:
            # row = self.final[k]['row']
            column = self.final[k]['column']
            break
        for task in self.successful:
            result = task['result']
            row_index = 0
            column_index = column['value'].index(
                float(task['message']['parameterOfFunction']['testArguments']['parameters']['setTemp']))
            for k in result.keys():
                self.final[k]['data'][row_index][column_index] = float(result[k])

    def report(self, method=''):
        self.set_data()
        if method == '':
            return self.final
        elif method == 'string':
            output = self.final
            table_string = str(HTML.table([
                ['Stromgrenze (A, Peak)',
                 output['summary.currentLimDischargeDynamic']['data'][0][0],
                 output['summary.currentLimDischargeDynamic']['data'][0][1],
                 output['summary.currentLimDischargeDynamic']['data'][0][2]],
                ['Stromgrenze (A, Dauer)',
                 output['summary.currentLimDischargeContinuous']['data'][0][0],
                 output['summary.currentLimDischargeContinuous']['data'][0][1],
                 output['summary.currentLimDischargeContinuous']['data'][0][2]],
            ], header_row=['', "-10 °C", "10 °C", "25 °C"], set_column=True))
            return table_string
