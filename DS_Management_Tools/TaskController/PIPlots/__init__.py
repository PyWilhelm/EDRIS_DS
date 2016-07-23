#!/usr/bin/env python
# -*- coding: utf-8 -*-

from TaskController.BaseClass.Controller import Controller
from BuildingTools.ScriptGenerator.edrisRules import EDBBuildInfo
import json
import os
import copy
import piutils
import numpy as np

_dir = os.path.dirname(os.path.abspath(__file__))


def start_controller(tid, input_data=None, session={}, controller=None, block=True, method='', sample=False):
    controller = Controller(priority=3) if controller is None else controller
    with open(os.path.join(_dir, u'mock.json')) as f:
        metatask_data = json.load(f)
    session['controller'] = controller

    if input_data is not None:
        edb_info = EDBBuildInfo(input_data['edb_paths']).get_build_info()
        metatask_data["taskGenerator"]["arguments"]["constant"]["buildingInfo"] = edb_info
    result_future = controller.add_metatask(metatask_data)

    if not block:
        return result_future
    else:
        result = result_future.get()
        session['SPS'] = result
        controller.stop()
        return True


class PIData(object):

    def __init__(self, fixed_op=None, base_op=None, edb_paths=None, pi_parameters=None):
        if (fixed_op is None) and (base_op is None):
            raise Exception("you should either set fixed_op or base_op")
        elif (fixed_op is not None) and (base_op is not None):
            raise Exception("you should not set fixed_op or base_op at the same time")

        self.pi_parameters = piutils.get_default_pi_parameters()
        if pi_parameters is not None:
            self.pi_parameters.update(pi_parameters)
        self.edb_paths = edb_paths
        if fixed_op is not None:
            self.set_metatask_fixed_op(fixed_op)
        elif base_op is not None:
            self.set_metatask_base_op(base_op)

    def set_metatask_fixed_op(self, op):
        with open(os.path.join(_dir, u'mock.json')) as f:
            metatask_data = json.load(f)
        self.metatask = piutils.set_metatask(metatask_data, self.pi_parameters, self.edb_paths)
        self.metatask = piutils.use_predefined_operating_point(metatask_data, op, self.pi_parameters)

    def set_metatask_base_op(self, base_op):
        with open(os.path.join(_dir, u'mock.json')) as f:
            metatask_data = json.load(f)
        self.metatask = piutils.set_metatask(metatask_data, self.pi_parameters, self.edb_paths)
        self.metatask = piutils.use_operating_point(metatask_data, base_op, self.pi_parameters)

    def start_simulation(self, controller):
        self.result_future = controller.add_metatask(self.metatask)
        return self.result_future

    def get_scale(self, scale_name):
        result = self.result_future.get()
        return get_scale(result, scale_name)

    def get_default_stars(self, scale_name):
        scale = self.get_scale(scale_name).data
        base = scale[0]
        others = scale[1:]
        import math
        first_star_value = others[0] + (others[-1] - others[0]) / 5.0 * 1.0
        last_star_value = others[0] + (others[-1] - others[0]) / 5.0 * 4.0

        first_star = min(others, key=lambda x: abs(x - first_star_value))
        last_star = min(others, key=lambda x: abs(x - last_star_value))
        return piutils.no_duplicate([base, first_star, last_star])

    def get_results(self, data_name, scale_name):
        result = self.result_future.get()
        return get_data(result, data_name, scale_name)


def get_scale(sde_data, scale_name):
    index = get_scale_index(sde_data, scale_name)
    return sde_data.get_sdf_datasets()[index]


def get_scale_index(sde_data, scale_name):
    datasets = sde_data.get_sdf_datasets()
    index_tuple_array = [tup for tup in enumerate(datasets) if tup[1].name == scale_name]
    index = index_tuple_array[0][0]
    return index


def get_scale_length(sde_data, scale_name):
    datasets = sde_data.get_sdf_datasets()
    index = get_scale_index(sde_data, scale_name)
    return len(datasets[index].data)


def get_data(sde_data, data_name, scale_name):
    datasets = sde_data.get_sdf_datasets()
    scale_index = get_scale_index(sde_data, scale_name)
    scale_length = get_scale_length(sde_data, scale_name)

    index_tuple_array = [tup for tup in enumerate(datasets) if tup[1].name == data_name]
    dataset = index_tuple_array[0][1]

    new_dataset = copy.deepcopy(dataset)
    data = new_dataset.data
    new_data = np.concatenate([[data[0, 0]], data[scale_index, 1:(1 + scale_length)]])
    new_dataset.data = new_data
    return new_dataset

if __name__ == "__main__":
    input_data = dict()

    path_battery = r'C:\edris\EDRIS_database\ComponentData\02_ElectricEnergyStorageSystem\02_ComponentData'
    edb_paths = {u'Battery_01': os.path.join(path_battery,
                                             r'Gen5_20140828_MCV2_UHE_96s3p/10_Parameter/20140828'), }

    input_data = dict(edb_paths=edb_paths)
    result = start_controller(tid=100, input_data=input_data,)
