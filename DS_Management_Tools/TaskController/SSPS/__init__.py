#!/usr/bin/env python
# -*- coding: utf-8 -*-

from TaskController.BaseClass.Controller import Controller
import json
import os


def start_controller(tid, input_data, session={}, controller=None, block=True, method=''):
    _dir = os.path.dirname(os.path.abspath(__file__))
    if method == 'BatteryPlot':
        controller = Controller(priority=3) if controller is None else controller
        with open(os.path.join(_dir, 'BatterySSPS.json')) as f:
            metatask_data = json.load(f)
    elif method == 'SystemSSPS':
        controller = Controller(priority=3) if controller is None else controller
        with open(os.path.join(_dir, 'SystemSSPSDARTSmall.json')) as f:
            metatask_data = json.load(f)
    elif method == 'SystemMock':
        controller = Controller(priority=3) if controller is None else controller
        with open(os.path.join(_dir, 'SystemSSPSDARTMock.json')) as f:
            metatask_data = json.load(f)
    session['controller'] = controller
    result_future = controller.add_metatask(metatask_data)
    if not block:
        return result_future
    else:
        result = result_future.get()
        session['SSPS'] = result
        result.save_as_sdf()
        controller.stop()
        return True

if __name__ == "__main__":
    input_data = dict()
    result = start_controller(tid=100, input_data=input_data, method='SystemMock')
