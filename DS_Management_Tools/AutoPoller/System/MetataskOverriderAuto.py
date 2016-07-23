#!/usr/bin/env python
# -*- coding: utf-8 -*-

from BuildingTools.ScriptGenerator.SpecificBase import SpecificBase
from BuildingTools.ScriptGenerator.edrisRules import Rules 
from TaskController.BaseClass.BaseMetataskOverrider import BaseMetataskOverrider as bmto


class MetataskOverriderAuto(bmto):
    def override_all(self, userinput):
        if userinput.get('Battery'):
            build_info = {'Battery': userinput['Battery']}
            spec_data = {'parameter': dict(), 'definition': self.input['building']['definition']}
            model_building_info_list = SpecificBase(Rules(build_info), spec_data).generate_specific_script_metatask_format()
            model = {'buildingInfo': model_building_info_list}
            self.add_model(model)
        if userinput.get('build'):
            build_info = userinput['build']
            spec_data = {'parameter': dict(), 'definition': self.input['building']['definition']}
            model_building_info_list = SpecificBase(Rules(build_info), spec_data).generate_specific_script_metatask_format()
            model = {'buildingInfo': model_building_info_list}
            self.add_model(model)
        for item in self.input['taskGenerator']['arguments']['variable']:
            if item['name'] == 'setSpeed':
                ls = item['value']
                ls = ls.replace('n_max', str(userinput['n_max']))
                ls = ls.replace('n_eck', str(userinput['n_eck']))
                item['value'] = ls
        if userinput.get('modelName') != None:
            self.input['taskGenerator']['arguments']['constant']['parameterOfFunction']['testArguments']['modelName'] = userinput['modelName']
        if userinput.get('setNcAgingFactor') != None:
            self.input['taskGenerator']['arguments']['constant']['parameterOfFunction']['testArguments']['parameters']['setNcAgingFactor'] \
            = str(userinput['setNcAgingFactor'])
        if userinput.get('setRiAgingFactor') != None:
            self.input['taskGenerator']['arguments']['constant']['parameterOfFunction']['testArguments']['parameters']['setRiAgingFactor'] \
            = str(userinput['setRiAgingFactor'])
        return self.input 

    