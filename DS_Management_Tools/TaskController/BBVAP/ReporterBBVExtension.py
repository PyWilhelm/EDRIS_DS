#!/usr/bin/env python
# -*- coding: utf-8 -*-
from TaskController.BaseClass.BaseReporter import BaseReporter as brp

import HTML


class ReporterBBVFTP72(brp):

    def __init__(self, metatask):
        brp.__init__(self, metatask)
        self.final = []

    def set_data(self):
        for task in self.successful:
            result = task['result']
            self.final.append(result)

    def report(self, method=''):
        # self.set_data()
        sdf_ext = super(ReporterBBVFTP72, self).report()
        if self.prev_result is not None:
            self.prev_result['FTP72'] = sdf_ext
        else:
            self.prev_result = {'FTP72': sdf_ext}
        if method == '':
            return self.sdf_ext
        elif method == 'intermediate':
            return self.prev_result
        elif method == 'string':
            output = self.prev_result
            if len(output.keys()) < 2:
                raise Exception('output must have 2 keys')
            table_string = str(HTML.table([
                [u'FTP72 (1372s). @(25 °C, BoL, RCI=100%)',
                 "Fahrzeit (s): " + str(output['FTP72']['clock.y'][0]),
                 "Energie (Wh): " + str(output['FTP72']['summary.energyBatteryWh'][0]),
                 "Effizienz: " + str(output['FTP72']['summary.efficiencyEnergy'][0]),
                 "End SOC: " + str(output['FTP72']['summary.SOC'][0])
                 ],
                [u'WLTP (1800s). @(25 °C, BoL, RCI=100%)',
                 "Fahrzeit (s): " + str(output['WLTP']['clock.y'][0]),
                 "Energie (Wh): " + str(output['WLTP']['summary.energyBatteryWh'][0]),
                 "Effizienz: " + str(output['WLTP']['summary.efficiencyEnergy'][0])],
                "End SOC: " + str(output['WLTP']['summary.SOC'][0])
            ], set_column=True))
            return table_string


class ReporterBBVWLTP(brp):

    def __init__(self, metatask):
        brp.__init__(self, metatask)
        self.final = []

    def set_data(self):
        for task in self.successful:
            result = task['result']
            self.final.append(result)

    def report(self, method=''):
        # self.set_data()
        sdf_ext = super(ReporterBBVWLTP, self).report()

        if self.prev_result is not None:
            self.prev_result['WLTP'] = sdf_ext
        else:
            self.prev_result = {'WLTP': sdf_ext}
        if method == '':
            return sdf_ext
        elif method == 'intermediate':
            return self.prev_result
        elif method == 'string':
            output = self.prev_result
            if len(output.keys()) < 2:
                raise Exception('output must have 2 keys')
            table_string = str(HTML.table([
                [u'FTP72 (1372s). @(25 °C, BoL, RCI=100%)',
                 "Fahrzeit (s): " + str(output['FTP72']['clock.y'][0]),
                 "Energie (Wh): " + str(output['FTP72']['summary.energyBatteryWh'][0]),
                 "Effizienz: " + str(output['FTP72']['summary.efficiencyEnergy'][0]),
                 "End SOC: " + str(output['FTP72']['summary.SOC'][0])
                 ],
                [u'WLTP (1800s). @(25 °C, BoL, RCI=100%)',
                 "Fahrzeit (s): " + str(output['WLTP']['clock.y'][0]),
                 "Energie (Wh): " + str(output['WLTP']['summary.energyBatteryWh'][0]),
                 "Effizienz: " + str(output['WLTP']['summary.efficiencyEnergy'][0]),
                 "End SOC: " + str(output['WLTP']['summary.SOC'][0])
                 ],
            ], set_column=True))
            return table_string


class ReporterBBVFTP72Full(brp):

    def __init__(self, metatask):
        brp.__init__(self, metatask)
        self.final = []

    def set_data(self):
        for task in self.successful:
            result = task['result']
            self.final.append(result)

    def report(self, method=''):
        # self.set_data()
        sdf_ext = super(ReporterBBVFTP72Full, self).report()
        if self.prev_result is not None:
            self.prev_result['FTP72'] = sdf_ext
        else:
            self.prev_result = {'FTP72': sdf_ext}
        if method == '':
            return sdf_ext
        elif method == 'intermediate':
            return self.prev_result
        elif method == 'string':
            output = self.prev_result
            if len(output.keys()) < 3:
                raise Exception('output must have 2 keys')
            table_string = str(HTML.table([
                [u'FTP72 bis derating @(25 °C, BoL, RCI=100%)',
                 "Fahrzeit (s): " + str(output['FTP72']['clock.y'][0]),
                 "Energie (Wh): " + str(output['FTP72']['summary.energyBatteryWh'][0]),
                 "Effizienz: " + str(output['FTP72']['summary.efficiencyEnergy'][0]),
                 "End SOC: " + str(output['FTP72']['summary.SOC'][0])
                 ],
                [u'WLTP, bis derating @(25 °C, BoL, RCI=100%)',
                 "Fahrzeit (s):" + str(output['WLTP']['clock.y'][0]),
                 "Energie (Wh): " + str(output['WLTP']['summary.energyBatteryWh'][0]),
                 "Effizienz: " + str(output['WLTP']['summary.efficiencyEnergy'][0]),
                 "End SOC: " + str(output['WLTP']['summary.SOC'][0])
                 ],
                [u'MKV, bis derating @(25 °C, BoL, RCI=100%, bis Derating)',
                 "Fahrzeit (s): " + str(output['MKV']['clock.y'][0]),
                 "Energie (Wh): " + str(output['MKV']['summary.energyBatteryWh'][0]),
                 "Effizienz: " + str(output['MKV']['summary.efficiencyEnergy'][0]),
                 "End SOC: " + str(output['MKV']['summary.SOC'][0])
                 ],
            ], set_column=True))
            return table_string


class ReporterBBVWLTPFull(brp):

    def __init__(self, metatask):
        brp.__init__(self, metatask)
        self.final = []

    def set_data(self):
        for task in self.successful:
            result = task['result']
            self.final.append(result)

    def report(self, method=''):
        sdf_ext = super(ReporterBBVWLTPFull, self).report()
        if self.prev_result is not None:
            self.prev_result['WLTP'] = sdf_ext
        else:
            self.prev_result = {'WLTP': sdf_ext}
        if method == '':
            return sdf_ext
        elif method == 'intermediate':
            return self.prev_result
        elif method == 'string':
            output = self.prev_result
            if len(output.keys()) < 3:
                raise Exception('output must have 2 keys')
            table_string = str(HTML.table([
                [u'FTP72 bis derating @(25 °C, BoL, RCI=100%)',
                 "Fahrzeit (s): " + str(output['FTP72']['clock.y'][0]),
                 "Energie (Wh): " + str(output['FTP72']['summary.energyBatteryWh'][0]),
                 "Effizienz: " + str(output['FTP72']['summary.efficiencyEnergy'][0]),
                 "End SOC: " + str(output['FTP72']['summary.SOC'][0])
                 ],
                [u'WLTP, bis derating @(25 °C, BoL, RCI=100%)',
                 "Fahrzeit (s):" + str(output['WLTP']['clock.y'][0]),
                 "Energie (Wh): " + str(output['WLTP']['summary.energyBatteryWh'][0]),
                 "Effizienz: " + str(output['WLTP']['summary.efficiencyEnergy'][0]),
                 "End SOC: " + str(output['WLTP']['summary.SOC'][0])
                 ],
                [u'MKV, bis derating@(25 °C, BoL, RCI=100%, bis Derating)',
                 "Fahrzeit (s): " + str(output['MKV']['clock.y'][0]),
                 "Energie (Wh): " + str(output['MKV']['summary.energyBatteryWh'][0]),
                 "Effizienz: " + str(output['MKV']['summary.efficiencyEnergy'][0]),
                 "End SOC: " + str(output['MKV']['summary.SOC'][0])
                 ],
            ], set_column=True))
            return table_string


class ReporterBBVMKVFull(brp):

    def __init__(self, metatask):
        brp.__init__(self, metatask)
        self.final = []

    def set_data(self):
        for task in self.successful:
            result = task['result']
            self.final.append(result)

    def report(self, method=''):
        sdf_ext = super(ReporterBBVMKVFull, self).report()
        if self.prev_result is not None:
            self.prev_result['MKV'] = sdf_ext
        else:
            self.prev_result = {'MKV': sdf_ext}
        if method == '':
            return sdf_ext
        elif method == 'intermediate':
            return self.prev_result
        elif method == 'string':
            output = self.prev_result
            if len(output.keys()) < 3:
                raise Exception('output must have 2 keys')
            table_string = str(HTML.table([
                [u'FTP72 bis derating @(25 °C, BoL, RCI=100%)',
                 "Fahrzeit (s): " + str(output['FTP72']['clock.y'][0]),
                 "Energie (Wh): " + str(output['FTP72']['summary.energyBatteryWh'][0]),
                 "Effizienz: " + str(output['FTP72']['summary.efficiencyEnergy'][0]),
                 "End SOC: " + str(output['FTP72']['summary.SOC'][0])
                 ],
                [u'WLTP, bis derating @(25 °C, BoL, RCI=100%)',
                 "Fahrzeit (s):" + str(output['WLTP']['clock.y'][0]),
                 "Energie (Wh): " + str(output['WLTP']['summary.energyBatteryWh'][0]),
                 "Effizienz: " + str(output['WLTP']['summary.efficiencyEnergy'][0]),
                 "End SOC: " + str(output['WLTP']['summary.SOC'][0])
                 ],
                [u'MKV, bis derating@(25 °C, BoL, RCI=100%, bis Derating)',
                 "Fahrzeit (s): " + str(output['MKV']['clock.y'][0]),
                 "Energie (Wh): " + str(output['MKV']['summary.energyBatteryWh'][0]),
                 "Effizienz: " + str(output['MKV']['summary.efficiencyEnergy'][0]),
                 "End SOC: " + str(output['MKV']['summary.SOC'][0])
                 ],
            ], set_column=True))
            return table_string
