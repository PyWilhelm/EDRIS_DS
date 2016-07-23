#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json, os

from AutoPoller.System.MetataskOverriderAuto import MetataskOverriderAuto
from TaskController.BaseClass.Controller import Controller


def start_controller(input_data, session={}, controller=None):
    _dir = os.path.dirname(os.path.abspath(__file__))
    controller = Controller(priority=1) if controller == None else controller
    with open(_dir + '\\metatask.json') as f:
        metatask_data = json.load(f)
    metatask_data = override(metatask_data, input_data)
    result_future = controller.add_metatask(metatask_data)
    name, failed_list = result_future.get(sdf=False)
    
    return name, failed_list
    
def override(metatask_temp, userinput):
    mto = MetataskOverriderAuto(metatask_temp)
    return mto.override_all(userinput)
