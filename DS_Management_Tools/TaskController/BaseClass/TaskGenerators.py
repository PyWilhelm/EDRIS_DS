#!/usr/bin/env python
# -*- coding: utf-8 -*-
import copy
from TaskController.BaseClass.BaseTaskGenerator import BaseTaskGenerator as btg
from TaskController.BaseClass.BaseTaskGenerator import BuilderType


def _get_task_collection(task_generator, variable_dicts):
    if len(variable_dicts) > 0:
        task_collection = []
    else:
        task_collection = [task_generator['arguments']['constant']]
    for subdict in variable_dicts:
        temp_dict = dict()
        constant = copy.deepcopy(task_generator['arguments']['constant'])
        for item in subdict:
            links = item['link'].split('.')
            temp = constant
            for l_key in links:
                if temp.get(l_key) == None:
                    temp[l_key] = dict()
                temp = temp[l_key]
            temp[item['name']] = item['value']
        temp_dict = constant
        temp_dict['taskGenerateName'] = task_generator['taskGenerateName']
        task_collection.append(temp_dict)
    return task_collection


def _overflow(vector):
    if vector[-1] == 1:
        return True
    return False


class FullFactorialTG(btg):

    def __init__(self, data, builder=BuilderType.Dymola):
        btg.__init__(self, data, builder)

    def generate_simple(self):
        task_generator = self.data['taskGenerator']
        self._flatten_variable()
        variable_dicts = self._get_variable_dicts(task_generator)
        return _get_task_collection(task_generator, variable_dicts)

    def _get_variable_dicts(self, task_generator):
        variable_dicts = []
        arguments = task_generator['arguments']
        if 'variable' in arguments:
            number = len(arguments['variable'])
            vector = [0] * (number + 1)
            vector_max = [len(arg['value']) - 1
                          for arg in arguments['variable']]
            while not _overflow(vector):
                temp_dicts = []
                for index in range(len(vector_max)):
                    name = arguments['variable'][index]['name']
                    value = arguments['variable'][index]['value'][vector[index]]
                    temp_dicts.append({'link': arguments['variable'][index]['link'],
                                       'value': value, 'name': name})
                variable_dicts.append(temp_dicts)
                self._get_next_index(vector, vector_max)
        return variable_dicts

    def _get_next_index(self, vector, vector_max):
        for i in range(len(vector) - 1):
            if vector[i] < vector_max[i]:
                vector[i] += 1
                return
            else:
                vector[i] = 0
        vector[-1] = 1


class FullFactorialTGNoDymola(FullFactorialTG):

    def __init__(self, data, builder=BuilderType.NoBuilder):
        FullFactorialTG.__init__(self, data, builder)


class FullFactorialTGDummy(FullFactorialTG):

    def __init__(self, data, builder='dummy'):
        FullFactorialTG.__init__(self, data, builder)


class FullFactorialTGSOH(FullFactorialTG):

    def __init__(self, data, builder=BuilderType.Dymola):
        FullFactorialTG.__init__(self, data, builder)

    def generate_simple(self):
        task_collection = super(FullFactorialTGSOH, self).generate_simple()
        for task in task_collection:
            if task['parameterOfFunction']['testArguments']['SOH'] == '1':
                task['parameterOfFunction']['testArguments'][
                    'parameters']['setNcAgingFactor'] = '1'
                task['parameterOfFunction']['testArguments'][
                    'parameters']['setRiAgingFactor'] = '1'
        return task_collection


class ChangeOneTG(btg):

    def __init__(self, data, builder=BuilderType.Dymola):
        btg.__init__(self, data, builder)

    def generate_simple(self):
        task_generator = self.data['taskGenerator']
        self._flatten_variable()
        variable_dicts = self._get_variable_dicts(task_generator)
        return _get_task_collection(task_generator, variable_dicts)

    def _get_variable_dicts(self, task_generator):
        variable_dicts = []
        arguments = task_generator['arguments']
        if 'variable' not in arguments:
            return []

        variables = task_generator['arguments']['variable']

        keys = [item['name'] for item in variables]
        get_link = lambda key: arguments['variable'][keys.index(key)]['link']

        base_variable = {field['name']: field['value'][0] for field in variables}
        non_base = {field['name']: field['value'][1:] for field in variables}

        base_point = [dict(link=get_link(key), value=base_variable[key], name=key)
                      for key in base_variable]
        variable_dicts.append(base_point)

        for variable_key in non_base:
            for variable_value in non_base[variable_key]:
                temp_dicts = [elem for elem in base_point
                              if elem['name'] is not variable_key]
                temp_dicts.append(dict(link=get_link(variable_key),
                                       value=variable_value,
                                       name=variable_key))
                variable_dicts.append(temp_dicts)
        return variable_dicts


class ChangeOneTGNoDymola(ChangeOneTG):

    def __init__(self, data, builder=BuilderType.NoBuilder):
        ChangeOneTG.__init__(self, data, builder)


class SimpleVariationTG(btg):

    def __init__(self, data, builder=BuilderType.Dymola):
        btg.__init__(self, data, builder)

    def __flatten(self, tg_data):
        var = tg_data['arguments']['variable']
        var_build = [i for i in var if i.get('build')]
        var_para = [i for i in var if i not in var_build]
        build_list, build_length = self.__get_build_dicts(var_build)
        build_length = 1 if build_length == 0 else build_length
        if len(var_para) > 0:
            length_para = len(var_para[0]['value'])
            for var in var_para:
                var['value'] = [i for _ in range(build_length) for i in var['value']]
            for var in build_list:
                var['value'] = [i for i in var['value'] for _ in range(length_para)]
        var_para.extend(build_list)
        tg_data['arguments']['variable'] = var_para
        return tg_data

    def generate_simple(self):
        task_generator = self.data['taskGenerator']
        self._flatten_variable()
        # Simple Variation for each of parameters and building info. But full factorial variation between these two.
        task_generator = self.__flatten(task_generator)
        variable_dicts = self.__get_variable_dicts(task_generator)

        return _get_task_collection(task_generator, variable_dicts)

    def __get_variable_dicts(self, task_generator):
        variable_dicts = []
        arguments = task_generator['arguments']
        if 'variable' in arguments:
            variables = task_generator['arguments']['variable']
            list_values = zip(*[field['value'] for field in variables])
            for value_tuple in list_values:
                temp_dicts = []
                keys = [item['name'] for item in variables]
                for key, value in zip(keys, value_tuple):
                    temp_dicts.append({'link': arguments['variable'][keys.index(key)]['link'],
                                       'value': value,
                                       'name': key})
                variable_dicts.append(temp_dicts)
        return variable_dicts

    def __get_build_dicts(self, variable):
        variable_list = copy.deepcopy(variable)
        length = 0
        for var in variable_list:
            var['value'] = []

        number = len(variable)
        vector = [0] * (number + 1)
        vector_max = [len(arg['value']) - 1
                      for arg in variable]
        while not _overflow(vector):
            for index in range(len(vector_max)):
                name = variable[index]['name']
                value = variable[index]['value'][vector[index]]
                for var in variable_list:
                    if var['link'] == variable[index]['link'] and var['name'] == name:
                        var['value'].append(value)
                        length = len(var['value'])
                        break
            self.__get_next_index(vector, vector_max)
        return variable_list, length

    def __get_next_index(self, vector, vector_max):
        for i in range(len(vector) - 1):
            if vector[i] < vector_max[i]:
                vector[i] += 1
                return
            else:
                vector[i] = 0
        vector[-1] = 1
