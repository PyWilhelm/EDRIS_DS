#!/usr/bin/env pytho
# -*- coding: utf-8 -*-
import numpy as np
import copy
from BuildingTools.ScriptGenerator.edrisRules import EDBBuildInfo

_default_pi_parameters = {u'n_eck' : None,
                          u'n_max': None,
                          u'baseTemperature': 25,
                          u'baseRCI': 0.5,
                          u'baseTime': 10,
                          u'HV_consumption': None,
                          u'motorOrGenerator': None,
                          u'numberOfParalellCell': None,
                          u'setNumberOfParallelCells': None,
                          u'RCIend_terminate': None}
_special_parameters_keys = [u'n_eck',
                            u'n_max',
                            u'baseTemperature',
                            u'baseRCI',
                            u'baseTime',
                            u'motorOrGenerator',
                            u'RCIend_terminate',
                            ]


def get_rpms(n_corner, n_max):
    if n_corner is None:
        raise Exception("n_eck not set")
    if n_max is None:
        raise Exception("n_max not set")
    normal_rpms = np.arange(500, n_max, 500)
    special_rpms = np.array([n_max, n_corner])
    return np.unique(np.concatenate((normal_rpms, special_rpms))).tolist()

def get_default_pi_parameters():
    return copy.deepcopy(_default_pi_parameters)

def get_special_parameters_keys():
    return _special_parameters_keys

def _extract_normal_parameters(pi_parameters):
    parameters = dict()
    special_parameters = get_special_parameters_keys()
    normal_parameters_keys = [k for k in pi_parameters.keys() 
                                if k not in special_parameters]
    valued_keys = filter(lambda x:pi_parameters[x] is not None, 
                         normal_parameters_keys)
    for key in valued_keys:
        parameters[key] = pi_parameters[key]
    return parameters 

def extract_cont_parameters(pi_parameters):
    parameters = _extract_normal_parameters(pi_parameters)
    key = u'RCIend_terminate'
    if pi_parameters[key] is not None: 
        parameters[key] = pi_parameters[key]
    return parameters

def extract_peak_parameters(pi_parameters):
    return _extract_normal_parameters(pi_parameters)

def get_base_op(base_op_name):
    if op == "master_op1":
        return dict(t = 10, n = n_eck,  RCI = 10, T = 10, SoH = 100, mode = "mot")
    elif op == "master_op2":
        return dict(t = 10, n = n_eck,  RCI = 80, T = 0, SoH = 100, mode = "mot")
    elif op == "master_op3":
        return dict(t = 150, n = n_eck,  RCI = 50, T = 25, SoH = 100, mode = "mot")
    else:
        raise Exception('unknown operating point defined: base_op_name=' + base_op_name)

def set_metatask(metatask_data, pi_parameters, edb_paths=None):
    hv_consumption = pi_parameters['HV_consumption']
    metatask_data = set_constant_parameter(metatask_data, 'HV_consumption', hv_consumption)

    if edb_paths is not None:
        edb_info = EDBBuildInfo(edb_paths).get_build_info()
        metatask_data["taskGenerator"]["arguments"]["constant"]["buildingInfo"] = edb_info
    return metatask_data

def use_operating_point(metatask_data, base_op, pi_parameters):
    n_corner = pi_parameters['n_eck']
    n_max = pi_parameters['n_max']

    metatask_data = set_variable_parameters(metatask_data, 'StopTime', get_range('time', base_value=base_op['t']))
    metatask_data = set_variable_parameters(metatask_data, 'setRci', get_range('RCI', base_value=base_op['RCI']))
    metatask_data = set_variable_parameters(metatask_data, 'setSpeed', get_range('rpm', base_op['n'], dict(n_corner=n_corner,n_max=n_max)))
    metatask_data = set_variable_parameters(metatask_data, 'setTemp', get_range('temperature', base_value=base_op['t']))
    return metatask_data

def use_predefined_operating_point(metatask_data, op, pi_parameters):
    n_corner = pi_parameters['n_eck']
    n_max = pi_parameters['n_max']

    if op == "master_op1":
        metatask_data = set_variable_parameters(metatask_data, 'StopTime', [10])
        metatask_data = set_variable_parameters(metatask_data, 'setRci', get_range('RCI', base_value=0.1))
        metatask_data = set_variable_parameters(metatask_data, 'setSpeed', get_range('rpm', n_corner, dict(n_corner=n_corner,n_max=n_max)))
        metatask_data = set_variable_parameters(metatask_data, 'setTemp', [10])
    elif op == "master_op2":
        metatask_data = set_variable_parameters(metatask_data, 'StopTime', get_range('temperature', base_value=150))
        metatask_data = set_variable_parameters(metatask_data, 'setRci', [0.8])
        metatask_data = set_variable_parameters(metatask_data, 'setSpeed', [n_corner])
        metatask_data = set_variable_parameters(metatask_data, 'setTemp', [0])
    elif op == "master_op3":
        metatask_data = set_variable_parameters(metatask_data, 'StopTime', [10])
        metatask_data = set_variable_parameters(metatask_data, 'setRci', get_range('RCI', base_value=0.8))
        metatask_data = set_variable_parameters(metatask_data, 'setSpeed', [n_corner])
        metatask_data = set_variable_parameters(metatask_data, 'setTemp', get_range('temperature', base_value=-10))
    else:
        raise Exception(op + u" not found!")
    return metatask_data

def get_range(name, base_value, options=dict()):
    if name == 'RCI':
        converted_base_value = base_value/100.0
        rci_range = [0.1, 0.2,  0.3,  0.4,  0.5,  0.6,  0.7,  0.8,  0.9,  1.0,]  
        return no_duplicate([converted_base_value] + rci_range)
    elif name == 'rpm':
        n_corner = options['n_corner']
        n_max = options['n_max']
        rpm_range = get_rpms(n_corner, n_max)
        return no_duplicate([base_value] + rpm_range)
    elif name == 'time':
        time_range = [2, 5, 10, 30, 60, 150, 300]
        return no_duplicate([base_value] + time_range)
    elif name == 'temperature':
        temperature_range = [-10, -5, 0, 10, 25, 35, 40]
        return no_duplicate([base_value] + temperature_range)

def no_duplicate(seq):
    seen = set()
    seq_no_duplicate = []
    for x in seq:
        if not x in seen:
            seq_no_duplicate.append(x)
            seen.add(x)
    return seq_no_duplicate 

def get_stars(name, base_value):
    pass

def set_constant_parameter(metatask_data, name, value):
    new_metatask_data = copy.deepcopy(metatask_data)
    constant = new_metatask_data["taskGenerator"]["arguments"]["constant"] 
    model_parameters = constant["parameterOfFunction"]["testArguments"]["parameters"]
    return new_metatask_data 

def set_variable_parameters(metatask_data, name, value):
    new_metatask_data = copy.deepcopy(metatask_data)
    if new_metatask_data["taskGenerator"]["arguments"].get("variable") is None:
        new_metatask_data["taskGenerator"]["arguments"]["variable"] = []
    variable = new_metatask_data["taskGenerator"]["arguments"]["variable"] 

    entries = [elem for elem in variable if elem["name"] == name]
    if len(entries) == 0:
        new_entry = {u"name": name, u"value": value}
        variable.append(new_entry)
    elif len(entries) == 1:
        entries[0][u"value"] = value
    else:
        raise Exception(u"the variable " + name + 
                        u" is found at least twice (normally is alright, but not here")

    return new_metatask_data 


class PISimSetup(object):
    def __init__(self, pi_parameters=None, test_type='peak'):
       self.test_type = test_type

       if pi_parameter is not None:
           self.variable = PISimSetup._get_variable(pi_parameters, test_type)
           self.constant = PISimSetup._get_constant(pi_parameters, test_type)
       else:
           self.variable = None
           self.constant = None
    
    @staticmethod
    def get_variable(pi_parameters, test_type):
        pass

    @staticmethod
    def get_variable(pi_parameters, test_type):
        pass


