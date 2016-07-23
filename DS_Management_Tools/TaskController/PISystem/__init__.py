#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import time
import numpy as np
from TaskController.BaseClass.Controller import Controller
from TaskController.PISystem import PostProcessing
from BuildingTools.ScriptGenerator.edrisRules import EDBBuildInfo
from BuildingTools.ScriptGenerator.edrisRules import Rules
from BuildingTools.ScriptGenerator.edrisRulesData import default_spec_data
import piutils


def start_controller(tid, input_data, session={}, controller=None, block=True, method='mock'):
    controller = Controller(
        priority=99, no_cache=True) if controller is None else controller
    session['controller'] = controller

    try:
        edb_paths = input_data.get('edb_paths')
        pi_parameters = input_data['pi_parameters']
        model_name = input_data.get('model_name')
        pisys = PISystemSim(edb_paths, pi_parameters=pi_parameters,
                            method=method, model_name=model_name)
        pisys.simulate(controller)
        if not block:
            return pisys
        else:
            sdf_filename = pisys.get_results()
            session['result'] = os.path.basename(sdf_filename)
            controller.stop()
            return True
    except Exception:
        import traceback
        traceback.print_exc()
        controller.set_error(traceback.format_exc())

# TODO: Abstraction for metatask class


class PISystemSim(object):

    def __init__(self, edb_paths, pi_parameters=None, method='full', model_name=None):
        default_pi_parameters = piutils.get_default_pi_parameters()

        if pi_parameters is not None:
            default_pi_parameters.update(pi_parameters)

        self.model_name = model_name
        self.pi_parameters = default_pi_parameters
        print(edb_paths)
        self.edb_info = EDBBuildInfo(edb_paths).get_build_info()
        print(self.edb_info)
        self._set_metatask(method)

    def _save_metatasks(self):
        _dir = os.path.dirname(os.path.abspath(__file__))

        with open(os.path.join(_dir, 'new-metatask-peak-%s.json' % time.time()), 'a') as f:
            f.write(json.dumps(self.metatask_data_peak))
        with open(os.path.join(_dir, 'new-metatask-cont-%s.json' % time.time()), 'a') as f:
            f.write(json.dumps(self.metatask_data_cont))

    def _set_metatask(self, method):
        _dir = os.path.dirname(os.path.abspath(__file__))
        if method == 'small':
            with open(os.path.join(_dir, 'SystemSPSDARTSmall.json')) as f:
                self.metatask_data_peak = json.load(f)
            with open(os.path.join(_dir, 'SystemSSPSDARTSmall.json')) as f:
                self.metatask_data_cont = json.load(f)
        elif method == 'mock':
            with open(os.path.join(_dir, 'SystemSPSDARTMock.json')) as f:
                self.metatask_data_peak = json.load(f)
            with open(os.path.join(_dir, 'SystemSSPSDARTMock.json')) as f:
                self.metatask_data_cont = json.load(f)
        elif method == 'full':
            with open(os.path.join(_dir, 'SystemSPSDART.json')) as f:
                self.metatask_data_peak = json.load(f)
            with open(os.path.join(_dir, 'SystemSSPSDART.json')) as f:
                self.metatask_data_cont = json.load(f)
        else:
            raise Exception("Method " + method + " unknown")

        if self.model_name is not None:
            self.metatask_data_cont["taskGenerator"]["arguments"]["constant"][
                "parameterOfFunction"]["testArguments"]['modelName'] = self.model_name
            self.metatask_data_peak["taskGenerator"]["arguments"]["constant"][
                "parameterOfFunction"]["testArguments"]['modelName'] = self.model_name

        if self.metatask_data_cont["taskGenerator"]["arguments"]["constant"].get("buildingInfo") is None:
            self.metatask_data_cont["taskGenerator"][
                "arguments"]["constant"]["buildingInfo"] = dict()
        if self.metatask_data_peak["taskGenerator"]["arguments"]["constant"].get("buildingInfo") is None:
            self.metatask_data_peak["taskGenerator"][
                "arguments"]["constant"]["buildingInfo"] = dict()
        if self.metatask_data_cont["taskGenerator"]["arguments"]["constant"][
                "parameterOfFunction"]["testArguments"].get("parameters") is None:
            self.metatask_data_cont["taskGenerator"]["arguments"]["constant"][
                "parameterOfFunction"]["testArguments"]["parameters"] = dict()
        if self.metatask_data_peak["taskGenerator"]["arguments"]["constant"][
                "parameterOfFunction"]["testArguments"].get("parameters") is None:
            self.metatask_data_peak["taskGenerator"]["arguments"]["constant"][
                "parameterOfFunction"]["testArguments"]["parameters"] = dict()

        self.metatask_data_cont["taskGenerator"]["arguments"][
            "constant"]["buildingInfo"].update(self.edb_info)
        self.metatask_data_peak["taskGenerator"]["arguments"][
            "constant"]["buildingInfo"].update(self.edb_info)

        self.metatask_data_peak["taskGenerator"]["arguments"]["constant"]["parameterOfFunction"][
            "testArguments"]["parameters"].update(piutils.extract_peak_parameters(self.pi_parameters))
        self.metatask_data_cont["taskGenerator"]["arguments"]["constant"]["parameterOfFunction"][
            "testArguments"]["parameters"].update(piutils.extract_cont_parameters(self.pi_parameters))

        n_eck = self.pi_parameters["n_eck"]
        n_max = self.pi_parameters["n_max"]

        if self.metatask_data_peak["taskGenerator"]["arguments"]["constant"]["parameterOfFunction"].get("info") is None:
            self.metatask_data_peak["taskGenerator"]["arguments"][
                "constant"]["parameterOfFunction"]["info"] = dict()
        if self.metatask_data_cont["taskGenerator"]["arguments"]["constant"]["parameterOfFunction"].get("info") is None:
            self.metatask_data_cont["taskGenerator"]["arguments"][
                "constant"]["parameterOfFunction"]["info"] = dict()
        self.metatask_data_peak["taskGenerator"]["arguments"][
            "constant"]["parameterOfFunction"]["info"]["n_eck"] = n_eck
        self.metatask_data_cont["taskGenerator"]["arguments"][
            "constant"]["parameterOfFunction"]["info"]["n_eck"] = n_eck
        self.metatask_data_peak["taskGenerator"]["arguments"][
            "constant"]["parameterOfFunction"]["info"]["n_max"] = n_max
        self.metatask_data_cont["taskGenerator"]["arguments"][
            "constant"]["parameterOfFunction"]["info"]["n_max"] = n_max
        if (n_eck is not None) and (n_max is not None):
            self.metatask_data_peak = piutils.set_variable_parameters(self.metatask_data_peak,
                                                                      'setSpeed',
                                                                      piutils.get_rpms(n_eck, n_max))
            self.metatask_data_cont = piutils.set_variable_parameters(self.metatask_data_cont,
                                                                      'setSpeed',
                                                                      piutils.get_rpms(n_eck, n_max))

    def simulate(self, controller):
        self.result_future_peak = controller.add_metatask(
            self.metatask_data_peak)
        self.result_future_cont = controller.add_metatask(
            self.metatask_data_cont)
        return self

    def get_results(self):
        result_peak = self.result_future_peak.get()
        result_cont = self.result_future_cont.get()
        sdf_merged = PostProcessing.merge_peak_cont(result_peak, result_cont,
                                                    self.metatask_data_peak)
        return sdf_merged

if __name__ == "__main__":
    #     path_battery = r'C:\EdrisAscent\EDRIS_database\trunk\ComponentData\02_ElectricEnergyStorageSystem\
    #                      02_ComponentData'
    #     path_em = r'C:\EdrisAscent\EDRIS_database\trunk\ComponentData\04_EM\02_ComponentData'
    #     edb_paths = {u'Battery_01': os.path.join(path_battery,
    #                                     r'SP06\10_Parameter\2014-12-20_Meta23_v2'),
    #                  u'ElectricMachine_01': os.path.join(path_em,
    #                                 r'ZF_PSM_EMP26970\10_Parameter\140807_REVO_K30_LE125Dx')}
    #     edb_paths_dummy = {u'Battery_01': None, u'ElectricMachine_01': None}
    #     pi_parameters = {u'n_eck' : 3500, u'n_max': 7000, u'HV_consumption': 1500,
    #                             u'motorOrGenerator': None, u'numberOfParalellCell': None,
    #                             u'setNumberOfParallelCells': None, u'RCIend_terminate': 0.05}
    #     input_data = dict(pi_parameters=pi_parameters, edb_paths=edb_paths)
    #     result = start_controller(tid=100, input_data=input_data, method='small')

    # =========================================================================
    # =========================================================================
    edb_paths = {u'Battery_01': r'battery1\data.mat',
                 u'ElectricMachine_01': r'em1\data.mat'}
    pi_parameters = {u'n_eck': 3500, u'n_max': 7000, u'HV_consumption': 1500,
                     u'motorOrGenerator': None, u'numberOfParalellCell': None,
                     u'setNumberOfParallelCells': None, u'RCIend_terminate': 0.05}
    input_data = dict(pi_parameters=pi_parameters, edb_paths=edb_paths)
    result = start_controller(tid=100, input_data=input_data, method='small')
