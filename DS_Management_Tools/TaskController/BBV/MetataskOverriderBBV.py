#!/usr/bin/env python
# -*- coding: utf-8 -*-
from TaskController.BaseClass.BaseMetataskOverrider import BaseMetataskOverrider as bmto
from BuildingTools.ScriptGenerator.edrisRules import Rules
from BuildingTools.ScriptGenerator.SpecificBase import SpecificBase


class MetataskOverriderBBV(bmto):

    def override_all(self, userinput):
        info_data = userinput
        spec_data = {'parameter': dict(), 'definition': self.input['building']['definition']}
        model_building_info_list = SpecificBase(Rules(info_data), spec_data).generate_specific_script_metatask_format()

        model = {'buildingInfo': model_building_info_list}
        self.add_model(model)
        return self.input

    def get_task_data(self):
        return self.input

    def override_userinput(self, userinput, SOH=0):
        ls = self.input['taskGenerator']['arguments']['variable']['setSpeed']['value']
        ls.remove(u'n_max')
        ls.remove(u'n_eck')
        ls.extend([userinput['n_max'], userinput['n_eck']])

        self.input['taskGenerator']['arguments']['variable']['setSpeed']['value'] = ls

        self.input['taskGenerator']['arguments']['constant']['parameterOfFunction']['testArguments']['SOH'] = SOH
        if SOH == 0:
            self.input['taskGenerator']['arguments']['constant']['parameterOfFunction'][
                'testArguments']['parameters']['setNcAgingFactor'] = userinput['setNcAgingFactor']
            self.input['taskGenerator']['arguments']['constant']['parameterOfFunction'][
                'testArguments']['parameters']['setRiAgingFactor'] = userinput['setRiAgingFactor']
        elif SOH == 1:
            self.input['taskGenerator']['arguments']['constant']['parameterOfFunction'][
                'testArguments']['parameters']['setNcAgingFactor'] = '1'
            self.input['taskGenerator']['arguments']['constant']['parameterOfFunction'][
                'testArguments']['parameters']['setRiAgingFactor'] = '1'
