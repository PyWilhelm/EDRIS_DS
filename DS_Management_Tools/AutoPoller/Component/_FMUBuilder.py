#!/usr/bin/env python
# -*- coding: utf-8 -*-
import math, os, hashlib, json

from scipy.io import savemat, loadmat

from BuildingTools.BuildWrapper import ModelGenerator 
from BuildingTools.ScriptGenerator import ModelSDS
from BuildingTools.ScriptGenerator.SpecificFMU import SpecificFMU
from BuildingTools.ScriptGenerator.edrisRules import Rules
from conf import __conf__
from dymola.dymola_exception import DymolaException
from dymola.dymola_interface import DymolaInterface


component_type_dict = {"02": "Battery",
                       "04": "ElectricMachine",
                       "05": "DCDCConverter",
                       "06": "Charger"
                       }
model_name_mapping = {"Battery": 'EdrisLibComponents.Components.Batteries.FMI.FMI_Battery_Template',
                      "ElectricMachine": 'EdrisLibSysTemp.FMI_ElectricDrive.FMI_ElectricDrive_NewApproach_Template',
                      "DCDCConverter": 'EdrisLibComponents.Components.DCDCConverters.FMI.FMI_DCDCConverter_Template',
                      'Charger': 'EdrisLibComponents.Components.Chargers.FMI.FMI_Charger_Template'
                      }

class FMUBuilder(object):
    def __init__(self, component_path, component_type=''):
        self.__component_path = component_path
        if component_type != '':
            self.__component_type = component_type
        else:
            rel_path = os.path.relpath(self.__component_path, os.path.join(__conf__['edrisBasePath'], __conf__['edrisComponentData']))
            self.__component_type = component_type_dict.get(rel_path[0:2], 'unknown')
        self.__model_name = model_name_mapping[self.__component_type]
        

    def build(self):
        '''
            Build FMU. 
            using hackcode for constant redeclare or rewritten parameter.
        '''
        if os.path.exists(self.__component_path) == False:
            raise Exception('Component Path not found! ' + self.__component_path)
        mat_list = [[f] for f in os.listdir(self.__component_path) if f.find('.mat') > 0]
        input_data = {self.__component_type: {'data': mat_list}}
        spec_data = {'parameter': dict(), 'definition': self.__get_ctype_definition(self.__component_type)}
        spec_data = self.__hackcode(input_data, spec_data)

            
        model_building_info_list = SpecificFMU(Rules(input_data), spec_data).generate_specific_script_metatask_format()
        rv = self.__add_model(model_building_info_list)
        modelsds = ModelSDS(rv['buildingInfo'])
        script = modelsds.generate_model_script()
        return self.simple_fmu_build(self.__model_name, script, self.__component_path)
    
    def __hackcode(self, input_data, spec_data):
        para = spec_data['parameter']
        for key in input_data.keys():
            if key == 'Battery':
                keys = ['startCoolingTemp', 'stopCoolingTemp', 'SOCmin', 'SOCmax']
                values_dict = self.__hackcode_get_values_dict(keys)
                para[spec_data['definition'][key]] = {'child' : {'ControllerLoadSelection': [{'child': {}}]}}
                para[spec_data['definition'][key]]['child']['ControllerLoadSelection'][0]['child'] = values_dict
                para[spec_data['definition'][key]]['child']['initEnergy'] = [{'value': '2'}]
        return spec_data
    
    @staticmethod
    def simple_fmu_build(model_name, script, component_path):   
        building_info = {'name': model_name, 'value': script}
        dymola_interface = DymolaInterface(__conf__['buildSetting']['dymolaPath'])
        model_generator = ModelGenerator(building_info, dymola_interface,
                                         component_path, 
                                         __conf__['edrisComponentsPath'], 
                                         __conf__['libraryPath'], 
                                         translate_fmu=True, fmu_type='cs', temp_dir=__conf__['tempdir'], 
                                         fmu_name=FMUBuilder.__fmu_name('cs', component_path))
        cs_finish, cs_log = model_generator.build_model()
        model_generator = ModelGenerator(building_info, dymola_interface,
                                         component_path, 
                                         __conf__['edrisComponentsPath'], 
                                         __conf__['libraryPath'], 
                                         translate_fmu=True, fmu_type='me', temp_dir=__conf__['tempdir'], 
                                         fmu_name=FMUBuilder.__fmu_name('me', component_path))
        me_finish, me_log = model_generator.build_model()
        dymola_interface.close()
        return cs_finish, me_finish, cs_log, me_log
    
    @staticmethod
    def __fmu_name(fmu_type, component_path):
        temp_file_path = [p for p in os.listdir(component_path) if p.find('M_') == 0 and p.find('.m') > 0]
        if len(temp_file_path) == 1:
            file_path = temp_file_path[0].replace('.m','')[2:]
        else:
            raise Exception('No Member File! ', component_path)
        if fmu_type == 'cs':
            return 'FMU_%s_CoSim.fmu' %(file_path,)
        elif fmu_type == 'me':
            return 'FMU_%s.fmu' %(file_path,)
        else:
            raise Exception()
    
    def __get_ctype_definition(self, ctype):
        mapping = {'Battery': { 'Battery': 'battery'}, 
                   'ElectricMachine': {'ElectricMachine': 'eMachine', 'Inverter': 'inverter'}}
        return mapping.get(self.__component_type, {self.__component_type: self.__component_type})
    
    # hackcode for initializing  
    def __hackcode_get_values_dict(self, keys):
        temp_file_path = [p for p in os.listdir(self.__component_path) if p.find('C') == 0]
        if len(temp_file_path) == 1:
            file_path = os.path.join(self.__component_path, temp_file_path[0])
        else:
            raise Exception('Controller Data ERROR', self.__component_path)
        data_dict = loadmat(file_path)
        return {k: {'value': data_dict[k][0][0]} for k in keys}
        
        
    def __add_model(self, model_building_info_list):
        rv = {}
        for model in model_building_info_list:
            self.__add_model_to_constant(model, rv)
        return rv
        
    def __add_model_to_constant(self, item,rv):
        links = item['link'].split('.')
        temp = rv
        for l in links:
            if temp.get(l) == None:
                temp[l] = dict()
            temp = temp[l]
        temp[item['name']] = item['value'][0]  
        
