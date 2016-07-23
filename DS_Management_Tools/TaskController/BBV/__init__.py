#!/usr/bin/env python
# -*- coding: utf-8 -*-
from TaskController.BBV.MetataskOverriderBBV import MetataskOverriderBBV
from TaskController.BBV.ReporterBBV import ReporterBBV
from TaskController.BaseClass.Controller import Controller
import TaskController.SPS
from BuildingTools.ScriptGenerator import ModelSDS
import json
import os


MetataskOverrider = MetataskOverriderBBV
Reporter = ReporterBBV


def start_controller(userinput, session={}, controller=None, block=True):
    controller = Controller() if controller is None else controller
    _dir = os.path.dirname(os.path.abspath(__file__))
    with open(_dir + '\\metatask_BBV.json') as f:
        metatask_data = json.load(f)
    metatask_data = override(metatask_data, userinput)
    result_f = controller.add_metatask(metatask_data)
    if not block:
        return result_f
    else:
        print '---------REPORTING----------'
        result = result_f.get()
        session['AP1'] = result
        print '---------REPORTING---------- finish'
        return result


def override(metatask_temp, userinput):
    mto = MetataskOverrider(metatask_temp)
    return mto.override_all(userinput)
