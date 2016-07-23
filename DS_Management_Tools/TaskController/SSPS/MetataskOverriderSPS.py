#!/usr/bin/env python
# -*- coding: utf-8 -*-
from TaskController.BaseClass.BaseMetataskOverrider import BaseMetataskOverrider as bmto
from BuildingTools.ScriptGenerator.edrisRules import Rules
from BuildingTools.ScriptGenerator.SpecificBase import SpecificBase


class MetataskOverriderSSPS(bmto):

    def override_all(self, userinput, plot=''):
        '''if userinput.get('Battery'):
            build_info = {'Battery': userinput['Battery']}
            spec_data = {'parameter': dict(), 'definition': self.input['building']['definition']}
            model_building_info_list = SpecificBase(Rules(build_info), spec_data)
                                       .generate_specific_script_metatask_format()
            model = {'buildingInfo': model_building_info_list}
            self.add_model(model)'''

        if userinput.get('build'):
            build_info = userinput['build']
            spec_data = {'parameter': dict(), 'definition': self.input['building']['definition']}
            model_building_info_list = SpecificBase(
                Rules(build_info), spec_data).generate_specific_script_metatask_format()
            model = {'buildingInfo': model_building_info_list}
            self.add_model(model)
        if plot.find('Plot') >= 0:
            for key in [k for k in userinput.keys() if k != 'build']:
                if self.__check_single_value(userinput[key]):
                    if key in ['setTemp', 'setRci', 'setSpeed', 'RCIend_terminate']:
                        self.input['taskGenerator']['arguments']['constant']['parameterOfFunction']['testArguments']['parameters'][key] \
                            = userinput[key]
                    elif key == 'StopTime':
                        self.input['taskGenerator']['arguments']['constant']['parameterOfFunction']['testArguments']['simulationSettings'][key] \
                            = userinput[key]
                    elif key == 'SOH':
                        self.input['taskGenerator']['arguments']['constant']['parameterOfFunction']['testArguments'][key] \
                            = userinput[key]
                else:
                    if self.input['taskGenerator']['arguments'].get('variable') == None:
                        self.input['taskGenerator']['arguments']['variable'] = []
                    temp_dict = {'name': key, 'value': userinput[key]}
                    if key in ['setTemp', 'setRci', 'setSpeed']:
                        temp_dict['link'] = 'parameterOfFunction.testArguments.parameters'
                    elif key == 'SOH':
                        temp_dict['link'] = 'parameterOfFunction.testArguments'
                    self.input['taskGenerator']['arguments']['variable'].append(temp_dict)

        else:
            for item in self.input['taskGenerator']['arguments']['variable']:
                if item['name'] == 'setSpeed':
                    ls = item['value']
                    ls = ls.replace('n_max', userinput['n_max'])
                    ls = ls.replace('n_eck', userinput['n_eck'])
                    item['value'] = ls
        if userinput.get('modelName') != None:
            self.input['taskGenerator']['arguments']['constant']['parameterOfFunction']['testArguments']['modelName'] \
                = userinput['modelName']
        if userinput.get('setNcAgingFactor') != None:
            self.input['taskGenerator']['arguments']['constant']['parameterOfFunction']['testArguments']['parameters']['setNcAgingFactor'] \
                = userinput['setNcAgingFactor']
        if userinput.get('setRiAgingFactor') != None:
            self.input['taskGenerator']['arguments']['constant']['parameterOfFunction']['testArguments']['parameters']['setRiAgingFactor'] \
                = userinput['setRiAgingFactor']
        return self.input

    def __check_single_value(self, value):
        if value.find(' ') >= 0:
            return False
        if value.find(':') >= 0:
            return False
        if value.find(',') >= 0:
            return False
        return True
