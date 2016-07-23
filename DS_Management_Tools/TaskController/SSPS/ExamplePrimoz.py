#!/usr/bin/env python
# -*- coding: utf-8 -*-

from TaskController.BaseClass.Controller import Controller
from BuildingTools.ScriptGenerator.edrisRules import EDBBuildInfo
import json
import os
import copy


def change_redeclare(metatask_base, paths):
    edb_info = EDBBuildInfo(paths).get_build_info()
    metatask_data = copy.deepcopy(metatask_base)
    metatask_data["taskGenerator"]["arguments"]["constant"]["buildingInfo"] = edb_info

    return metatask_data

if __name__ == "__main__":
    path_battery = r'C:\edris\EDRIS_database\ComponentData\02_ElectricEnergyStorageSystem\02_ComponentData'
    edb_paths1 = {u'Battery_01': os.path.join(path_battery,
                                              r'Gen5_20140828_MCV2_UHE_96s3p/10_Parameter/20140828'), }

    _dir = os.path.dirname(os.path.abspath(__file__))

    with open(os.path.join(_dir, 'BatteryVariationSSPS.json')) as f:
        metatask_data_base = json.load(f)

    controller = Controller(priority=3)

    metatask1 = change_redeclare(metatask_data_base, edb_paths1)
    metatask2 = change_redeclare(metatask_data_base, edb_paths1)

    result_future_1 = controller.add_metatask(metatask1)
    result_future_2 = controller.add_metatask(metatask1)

    # !! Blocking operation, do them at last
    result1 = result_future_1.get()
    result1.save_as_sdf()

    result2 = result_future_2.get()
    result2.save_as_sdf()
    controller.stop()
