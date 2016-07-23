#!/usr/bin/env python
# -*- coding: utf-8 -*-
from TaskController.BaseClass.BaseReporter import BaseReporter as brp
from TaskController.BaseClass.ReporterSimpleDymola import ReporterSimpleDymola as simple_rp
import HTML


class ReporterBBVOneC(brp):

    def __init__(self, metatask):
        brp.__init__(self, metatask)
        self.final = []

    def set_data(self):
        for task in self.successful:
            result = task['result']
            self.final.append(result)

    def report(self, method=''):
        # self.set_data()
        sdf_ext = super(ReporterBBVOneC, self).report()
        if self.prev_result is not None:
            self.prev_result['OneC'] = sdf_ext
        else:
            self.prev_result = {'OneC': sdf_ext}
        if method == '':
            return sdf_ext
        elif method == 'intermediate':
            return self.prev_result
        elif method == 'string':
            output = self.prev_result
            if len(output.keys()) < 2:
                raise Exception('output must have 2 keys')
            try:
                oneCResult = [u'Energie (Wh, 1C Entladen, Speicher Derating Aktiv) ',
                              self.prev_result['OneC']['summary.energyBatteryWh'][0]]
            except:
                oneCResult = [u'Energie (Wh, 1C Entladen, Speicher Derating Aktiv) ', 'Simulation Failed!']

            table_string = str(HTML.table([[u'AP1 (25 °C, 10s, EoL, RCI=10%)', "Leistung (W): " +
                                            str(self.prev_result['AP']['summary.batteryPower'][0])],
                                           [u'AP3 (0 °C, 10s, EoL, RCI=80%)', "Leistung (W): " +
                                            str(self.prev_result['AP']['summary.batteryPower'][1])],
                                           [u'AP6 (25 °C, 10s, BoL, RCI=80%)', "Leistung (W): " +
                                            str(self.prev_result['APBOL']['summary.batteryPower'][0])],
                                           [u'Dauerleistung (25 °C, BoL, RCI@End=5%)', "Leistung (W): " +
                                            str(self.prev_result['Dauer'][0]['result']['summary.batteryPower'])],
                                           oneCResult],
                                          set_column=True))
        return table_string


class ReporterBBVAP(brp):

    def __init__(self, metatask):
        brp.__init__(self, metatask)
        self.final = []

    def set_data(self):
        for task in self.successful:
            result = task['result']
            self.final.append(result)

    def report(self, method=''):
        # self.set_data()
        sdf_ext = super(ReporterBBVAP, self).report()
        if self.prev_result is not None:
            self.prev_result['AP'] = sdf_ext
        else:
            self.prev_result = {'AP': sdf_ext}
        if method == '':
            return self.sdf_ext
        elif method == 'intermediate':
            return self.prev_result
        elif method == 'string':
            output = self.prev_result
            if len(output.keys()) < 2:
                raise Exception('output must have 2 keys')
            try:
                oneCResult = [u'Energie (Wh, 1C Entladen, Speicher Derating Aktiv) ', str(
                    self.prev_result['OneC']['summary.energyBatteryWh'][0])]
            except:
                oneCResult = [u'Energie (Wh, 1C Entladen, Speicher Derating Aktiv) ', 'Simulation Failed!']
            table_string = str(HTML.table([[u'AP1 (25 °C, 10s, EoL, RCI=10%)', "Leistung (W): " +
                                            str(self.prev_result['AP']['summary.batteryPower'][0])],
                                           [u'AP3 ( 0 °C, 10s, EoL, RCI=80%)', "Leistung (W): " +
                                            str(self.prev_result['AP']['summary.batteryPower'][1])],
                                           [u'AP6 (25 °C, 10s, BoL, RCI=80%)', "Leistung (W): " +
                                            str(self.prev_result['APBOL']['summary.batteryPower'][0])],
                                           oneCResult],
                                          set_column=True))
        return table_string


class ReporterBBVAPBOL(brp):

    def __init__(self, metatask):
        brp.__init__(self, metatask)
        self.final = []

    def set_data(self):
        for task in self.successful:
            result = task['result']
            self.final.append(result)

    def report(self, method=''):
        # self.set_data()
        sdf_ext = super(ReporterBBVAPBOL, self).report()
        if self.prev_result is not None:
            self.prev_result['APBOL'] = sdf_ext
        else:
            self.prev_result = {'APBOL': sdf_ext}
        if method == '':
            return self.sdf_ext
        elif method == 'intermediate':
            return self.prev_result
        elif method == 'string':
            output = self.prev_result
            if len(output.keys()) < 2:
                raise Exception('output must have 2 keys')
            try:
                oneCResult = [u'Energie (Wh, 1C Entladen, Speicher Derating Aktiv) ',
                              str(self.prev_result['OneC']['summary.energyBatteryWh'][0])]
            except:
                oneCResult = [u'Energie (Wh, 1C Entladen, Speicher Derating Aktiv) ', 'Simulation Failed!']
            table_string = str(HTML.table([[u'AP1 (25 °C, 10s, EoL, RCI=10%)', "Leistung (W): " +
                                            str(self.prev_result['AP']['summary.batteryPower'][0])],
                                           [u'AP3 ( 0 °C, 10s, EoL, RCI=80%)', "Leistung (W): " +
                                            str(self.prev_result['AP']['summary.batteryPower'][1])],
                                           [u'AP6 (25 °C, 10s, BoL, RCI=80%)', "Leistung (W): " +
                                            str(self.prev_result['APBOL']['summary.batteryPower'][0])],
                                           oneCResult],
                                          set_column=True))
        return table_string


class ReporterBBVDauer(simple_rp):

    def __init__(self, metatask):
        brp.__init__(self, metatask)
        self.final = []

    def report(self, method=''):
        result = super(ReporterBBVDauer, self).report()
        if self.prev_result is not None:
            self.prev_result['Dauer'] = result
        else:
            self.prev_result = {'Dauer': result}
        return self.prev_result
