#!/usr/bin/env python
# -*- coding: utf-8 -*-
from TaskController.BaseClass.BaseReporter import BaseReporter as brp

import copy
import HTML


class ReporterBBV(brp):

    def __init__(self, metatask):
        brp.__init__(self, metatask)
        self.final = {}
        self.template = {'row': {'value': [], 'name': ''}, 'column': {'value': [], 'name': ''}, 'data': None}

    def set_head(self):
        d = self.metatask['taskGenerator']['arguments']['constant']['parameterOfFunction']['testArguments']['results']
        for k in d:
            table = copy.deepcopy(self.template)
            table['column']['name'] = 'setRci'
            table['row']['name'] = 'setTemp'
            table['column']['value'] = [float(v)
                                        for v in self.get_dict_from_name(
                self.metatask['taskGenerator']['arguments']['variable'],
                'setRci')['value']]
            table['row']['value'] = [float(v)
                                     for v in self.get_dict_from_name(
                self.metatask['taskGenerator']['arguments']['variable'],
                'setTemp')['value']]
            table['data'] = [['Nil' for _ in range(len(table['column']['value']))]
                             for __ in range(len(table['row']['value']))]
            self.final[k['signalName']] = table

    def set_data(self):
        self.set_head()
        for k in self.final:
            row = self.final[k]['row']
            column = self.final[k]['column']
            break
        for task in self.successful:
            result = task['result']
            row_index = row['value'].index(
                float(task['message']['parameterOfFunction']['testArguments']['parameters']['setTemp']))
            column_index = column['value'].index(
                float(task['message']['parameterOfFunction']['testArguments']['parameters']['setRci']))
            for k in result.keys():
                self.final[k]['data'][row_index][column_index] = float(result[k])

    def report(self, method=''):
        sdf_ext = super(ReporterBBV, self).report()
        # self.set_data()
        if method == '':
            return sdf_ext
        elif method == 'string':
            table_string = str(HTML.table([
                [u'Innenwiderstand (Ohm, 10 s, 25 °C)',
                 str(sdf_ext['summary.resistanceInnerCell'][0][0][0]),
                 str(sdf_ext['summary.resistanceInnerCell'][1][0][0]),
                 str(sdf_ext['summary.resistanceInnerCell'][2][0][0])],
                [u'Innenwiderstand (Ohm, 10 s, 0 °C)',
                 str(sdf_ext['summary.resistanceInnerCell'][0][1][0]),
                 str(sdf_ext['summary.resistanceInnerCell'][1][1][0]),
                 str(sdf_ext['summary.resistanceInnerCell'][2][1][0])],
                ['OCV (V)',
                 str(sdf_ext['summary.voltageIdle'][0][0][0]),
                 str(sdf_ext['summary.voltageIdle'][1][0][0]),
                 str(sdf_ext['summary.voltageIdle'][2][0][0])],
            ], header_row=['', "RCI = 5%", "RCI = 50%", "RCI = 90%", ], set_column=True))
            return table_string
