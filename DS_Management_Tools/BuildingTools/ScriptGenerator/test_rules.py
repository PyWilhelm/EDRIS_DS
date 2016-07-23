#!/usr/bin/env python
# -*- coding: utf-8 -*-
from BuildingTools.ScriptGenerator.edrisRules import EDBBuildInfo
import unittest
import os.path
import nose
import sys
import re


class testSuite(unittest.TestCase):

    def setUp(self):
        pass

    def test_conversion(self):
        path_battery = r'C:\edris\EDRIS_database\ComponentData\02_ElectricEnergyStorageSystem\02_ComponentData'
        path_em = r'C:\edris\EDRIS_database\ComponentData\04_EM\02_ComponentData'
        edb_paths = {u'Battery_01': os.path.join(path_battery,
                                                 r'Gen5_20140717_PHEV1_85mm_UHE_88s6p\10_Parameter\20140717'),
                     u'ElectricMachine_01':
                     os.path.join(path_em,
                                  r'Gen5_ASM_HEAT_klein_HDZ_30krpm\10_Parameter\140811_Ueberarb_PK_Q4_2014')}
        edb_info = EDBBuildInfo(edb_paths).get_build_info()
        print edb_info
        model_name = edb_info["eMachine_FluidPort1"]["child"]["ControllerLoadSelection"]["value"]
        self.assertEqual(get_controller_data(edb_paths[u'ElectricMachine_01'])[0:-4],
                         model_name.split(".")[-1])


def get_controller_data(path):
    model_pattern = u'C[0-9]{3}'
    all_files = os.listdir(path)
    file_list = [filename for filename in all_files if re.match(model_pattern, filename) != None]
    if len(file_list) > 1:
        raise Exception("found more than one controller data")
    return file_list[0]

if __name__ == '__main__':
    module_name = sys.modules[__name__].__file__
    result = nose.run(argv=[sys.argv[0], module_name, '--with-xunit', ])
