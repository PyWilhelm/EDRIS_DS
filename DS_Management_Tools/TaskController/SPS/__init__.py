#!/usr/bin/env python
# -*- coding: utf-8 -*-

from TaskController.SPS.MetataskOverriderSPS import MetataskOverriderSPS
from TaskController.SPS.ReporterSPS import ReporterSPS
from BuildingTools.ScriptGenerator import ModelSDS
from TaskController.BaseClass.Controller import Controller
import json
import os


def start_controller(tid, input_data, session={}, controller=None, block=True, method='', sample=False):
    _dir = os.path.dirname(os.path.abspath(__file__))
    if method == 'BatteryPlot':
        controller = Controller(priority=3) if controller is None else controller
        with open(_dir + '\\BatterySPSPlot.json') as f:
            metatask_data = json.load(f)
    elif method == 'SystemPlot':
        controller = Controller(priority=3) if controller is None else controller
        with open(_dir + '\\SystemSPSPlot.json') as f:
            metatask_data = json.load(f)
    elif method == 'System' or method == '':
        controller = Controller(priority=99) if controller is None else controller
        if not sample:
            with open(_dir + '\\SystemSPS.json') as f:
                metatask_data = json.load(f)
        else:
            with open(_dir + '\\SystemSPSSmall.json') as f:
                metatask_data = json.load(f)
    session['controller'] = controller
    metatask_data = override(metatask_data, input_data, method)
    result_future = controller.add_metatask(metatask_data)
    if not block:
        return result_future
    else:
        session['SPS'] = result_future.get(sdf=method.find('Plot') >= 0)
        controller.stop()
        return True


def override(metatask_temp, userinput, plot):
    mto = MetataskOverriderSPS(metatask_temp)
    return mto.override_all(userinput, plot)
