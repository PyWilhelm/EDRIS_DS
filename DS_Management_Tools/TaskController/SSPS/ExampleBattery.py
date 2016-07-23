#!/usr/bin/env python
# -*- coding: utf-8 -*-

from TaskController.BaseClass.Controller import Controller
from BuildingTools.ScriptGenerator.edrisRules import EDBBuildInfo
import json
import os


def start_controller(tid, input_data, session={}, controller=None, block=True, method='', sample=False):
    _dir = os.path.dirname(os.path.abspath(__file__))
    controller = Controller(priority=3) if controller is None else controller
    with open(_dir + '\\BatterySingleSSPS.json') as f:
        metatask_data = json.load(f)
    session['controller'] = controller
    edb_info = EDBBuildInfo(input_data['edb_paths']).get_build_info()
    metatask_data["taskGenerator"]["arguments"]["constant"]["buildingInfo"] = edb_info
    result_future = controller.add_metatask(metatask_data)
    if not block:
        return result_future
    else:
        result = result_future.get()

        session['SPS'] = result
        with open('test.json', 'w+') as f:
            f.write(json.dumps(result))
        controller.stop()
        return True


if __name__ == "__main__":
    input_data = dict()

    path_battery = r'C:\edris\EDRIS_database\ComponentData\02_ElectricEnergyStorageSystem\02_ComponentData'
    edb_paths = {u'Battery_01': os.path.join(path_battery,
                                             r'Gen5_20140828_MCV2_UHE_96s3p/10_Parameter/20140828'), }

    input_data = dict(edb_paths=edb_paths)
    result = start_controller(tid=100, input_data=input_data,)
