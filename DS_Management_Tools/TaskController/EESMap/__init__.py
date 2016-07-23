#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
from TaskController.SPS.MetataskOverriderSPS import MetataskOverriderSPS
from TaskController.BaseClass.Controller import Controller
from TaskController.PISystem import PostProcessing


def start_controller(tid, input_data, session={}, controller=None, block=True, method='', sample=False):
    _dir = os.path.dirname(os.path.abspath(__file__))
    if method == '':
        controller = Controller(priority=3) if controller is None else controller
        with open(os.path.join(_dir, 'metataskEESMap.json')) as f:
            metatask_data = json.load(f)
    else:
        raise Exception("Method " + method + " unknown")

    session['controller'] = controller
    # metatask_data = override(metatask_data, input_data, method)
    result_future = controller.add_metatask(metatask_data)
    if not block:
        return result_future
    else:
        result = result_future.get()
        result.save_as_sdf()

        controller.stop()
        return True


def override(metatask_temp, userinput, plot):
    mto = MetataskOverriderSPS(metatask_temp)
    return mto.override_all(userinput, plot)

if __name__ == "__main__":
    input_data = dict()
    result = start_controller(tid=100, input_data=input_data)
