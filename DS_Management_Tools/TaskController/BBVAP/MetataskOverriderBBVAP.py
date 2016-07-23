#!/usr/bin/env python
# -*- coding: utf-8 -*-
from TaskController.BaseClass.BaseMetataskOverrider import BaseMetataskOverrider as bmto
from BuildingTools.ScriptGenerator.edrisRules import Rules
from BuildingTools.ScriptGenerator.SpecificBase import SpecificBase


class MetataskOverriderBBVAP(bmto):

    def override_all(self, userinput, SOH=0):
        self.override_userinput(userinput, SOH)
        build_info = {'Battery': userinput['Battery']}
        spec_data = {'parameter': dict(), 'definition': self.input['building']['definition']}
        model_building_info_list = SpecificBase(Rules(build_info), spec_data).generate_specific_script_metatask_format()
        model = {'buildingInfo': model_building_info_list}
        self.add_model(model)
        return self.input

    def override_userinput(self, userinput, SOH=0):
        parameterOfFunction = self.input['taskGenerator']['arguments']['constant']['parameterOfFunction']
        if parameterOfFunction['testArguments']['parameters'].get('setNcAgingFactor') == None:
            return
        parameterOfFunction['testArguments']['SOH'] = SOH

        if SOH == 0:
            parameterOfFunction['testArguments']['parameters']['setNcAgingFactor'] = userinput['setNcAgingFactor']
            parameterOfFunction['testArguments']['parameters']['setRiAgingFactor'] = userinput['setRiAgingFactor']
        else:
            parameterOfFunction['testArguments']['parameters']['setNcAgingFactor'] = 1
            parameterOfFunction['testArguments']['parameters']['setRiAgingFactor'] = 1
