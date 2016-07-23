#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy, types, json, time, os, copy
from scipy.io import savemat

from TaskController.BaseClass.BaseReporter import BaseReporter as brp
from conf import __conf__


def convert(_input):
    if isinstance(_input, dict):
        return dict((convert(key), convert(value)) for key, value in _input.iteritems())
    elif isinstance(_input, list):
        return [convert(element) for element in _input]
    else:
        if not type(_input) in [types.FloatType, types.IntType, types.BooleanType]:
            _input = str(_input).encode('ascii')
        try:
            _input = float(_input)
        except:
            pass
        return _input  
    
    
a = lambda x: x.encode('ascii')


class ReporterAuto(brp):
    def __init__(self,metatask):
        brp.__init__(self, metatask)
        self.__mat = dict()
        self.__mat['allResults'] = []
        self.__mat['Dymola2DSet'] = dict()
        self.__mat['isWeb'] = 1
        self.__mat['Dymola2DSet']['test00_GENERATOR'] = dict()
        self.__mat['Dymola2DSet']['test00_GENERATOR']['Data'] = dict()
        #self.__mat[('Dymola2DSet')] = {('test00_GENERATOR'): {('Data'): dict()}}
        self.__results = []
        
    def report(self, method=''):
        print 'get_converted_data-----START'
        self.get_converted_data(self.successful, self.metatask)
        print 'get_converted_data-----FINISH'
        name = os.path.join(__conf__['outputPath'], 'mat', 'result-%s.mat' %(str(time.time())))
        print 'savemat-----START'
        savemat(name, mdict=convert(self.__mat), do_compression=True)
        print 'savemat-----FINISH'''
        self.__mat = {}
        self.successful = []
        return name, self.failed
        #return True
        
    def get_converted_data(self, tasks, metatask): 
        tasks = convert(tasks)
        metatask = convert(metatask)
        with open(__conf__['programPath'] + '\\db\\ConverterMappingSPS.json') as f:
            cmapping = json.load(f)
        self.get_allResults(cmapping['allResults'], tasks)
        self.get_Dymola2DSet(cmapping, metatask)
        return self.__mat
        
    def get_allResults(self, mapping, tasks):
        sp_map = mapping['simulationParameterSet']
        re_map = mapping['result']
        for task in tasks:
            subdict = task['message']['parameterOfFunction']
            cell = {'simulationParameterSet': dict(), 'result': dict()}
            cell['simulationParameterSet'] = {key: self.__get_value(subdict, sp_map[key]) for key in sp_map.keys() }
            cell['result'] = {key: self.__get_value(task['result'], re_map[key], False) for key in re_map.keys()}
            #cell['result']['power'] = float(cell['result']['torque']) * cell['simulationParameterSet']['RPM'] / 60.0 * 2.0 * numpy.pi
            self.__mat['allResults'].append(cell)
                    
    def __get_value(self, subdict, key, split=True):  

        try: 
            key = int(key)
            return key
        except:
            pass  
        if key == u'':
            return key
        if split:
            if key.find('functionArguments') < 0:
                subdict = subdict['testArguments']
            key_list = key.split('.')
            for k in key_list:
                if k in subdict.keys():
                    subdict = subdict[k]
                else:
                    return ''
            return subdict
        else:
            return subdict.get(key, 0)
        
    def get_Dymola2DSet(self, mapping, metatask):
        subdict = self.__mat['Dymola2DSet']['test00_GENERATOR']['Data']
        subdict['Name'] = 'AP1'
        subdict['modelName'] = metatask['taskGenerator']['arguments']['constant']['parameterOfFunction']['testArguments']['modelName']
        constant_parameters = metatask['taskGenerator']['arguments']['constant']['parameterOfFunction']['testArguments']['parameters']
        variable_parameters = metatask['taskGenerator']['arguments']['variable']
        sp_map = mapping['allResults']['simulationParameterSet']
        constant_cell = [self.get_constant_cell(self.get_key_from_value(sp_map, key), constant_parameters[key])
                         for key in constant_parameters.keys()]
        constant_cell.extend(self.get_function_argments(metatask, sp_map))
        variable_cell = [self.get_variable_cell(self.get_key_from_value(sp_map, item['name']), item['value'])
                         for item in variable_parameters if not isinstance(item['value'][0], types.DictType)]
        subdict['constantParameters'] = constant_cell
        subdict['variableParameters'] = variable_cell
        subdict['PlottingInfo_2d'] = {'x_var': '', 'y_var': '', 'fix': '', 'Contour_set': ''}
        
        
    def get_key_from_value(self, sp_map, value):
        for key in sp_map.keys():
            if str(sp_map[key]).find(value) >= 0:
                return key 
        return value
            
    def get_constant_cell(self, name, value):
        return {'name': name, 'value': value, 'unit': '/', 'description':'' }
    
    def get_variable_cell(self, name, value):
        
        return {'name': name, 'stars': value[0], 'testPoints': value, 'basOperatingPoints': value[0], 'unit': '/', 'description':''}
        
    def get_function_argments(self, metatask, sp_map):
        func_arg = metatask['taskGenerator']['arguments']['constant']['parameterOfFunction']['functionArguments']
        return [self.get_constant_cell(self.get_key_from_value(sp_map, key), func_arg[key]['maxValue']) for key in func_arg.keys()]
