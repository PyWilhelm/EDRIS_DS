#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sdf
import json
import logging
import copy
import types
import pickle

from TaskController.BaseClass.SDFExtension import SDFExtension


def convert(input_data):
    if isinstance(input_data, dict):
        return dict((convert(key), convert(value)) for key, value in input_data.iteritems())
    elif isinstance(input_data, list):
        return [convert(element) for element in input_data]
    else:
        if not type(input_data) in [types.FloatType, types.IntType, types.BooleanType]:
            input_data = input_data.decode('utf-8', 'ignore')
        try:
            input_data = float(input_data)
        except:
            pass
        return input_data


class BaseReporter(object):
    '''
        baseclass for reporting results of simulation
        interface:
            set_sim_results(metatask_data, cid, successful, failed, sdf): set results
                metatsk_data:
                cid: the controller's id, which has executed the simulation
                successful: list of results of successful executed tasks
                failed: list of results/logs of failed executed tasks
                sdf: [True, False] whether use sdf data structure as internal or intermediate DS
            set_prev_result(prev_result): set other result of reporter if it needs

        rewritten in subclass:
            report():
                the function in baseclass: save sdf data structure into temp folder and return the DS.
                if you want to use this base function as a part feature in subclass, must set sdf=True
                (default value) in function set_sim_results

    '''

    def __init__(self, metatask_data):
        self.cid = None
        self.metatask = metatask_data
        self.successful = None
        self.failed = None
        self.sdf_extenion = None
        self.prev_result = None
        self.report_name = ''

    def _recover(self, file_path, metatask_filepath):
        with open(file_path) as f:
            self.sdf_extenion = pickle.load(f)
        with open(metatask_filepath) as f:
            self.metatask = json.load(f)
        return self

    def set_prev_result(self, prev_result):
        self.prev_result = prev_result
        return self

    def set_sim_results(self, metatask_data, cid, successful, failed, sdf=True):
        print 'set_sim results---------START'
        self.metatask = metatask_data
        logging.info(json.dumps(self.metatask, indent=2))
        if sdf:
            self.__init_sdf_extension(self.metatask)
        self.successful = successful
        self.failed = failed
        self.cid = cid
        if sdf:
            self.__set_results(successful)
        print 'set_sim results--------FINISH'
        return self

    def report(self, arg=None):
        name = self.__save()
        self.report_name = name
        return self.sdf_extenion

    def get_dict_from_name(self, variable_list, name):
        for item in variable_list:
            if item['name'] == name:
                return item
        return None

    def __init_sdf_extension(self, metatask):
        variables = metatask['taskGenerator']['arguments'].get('variable')
        result_paras = metatask['taskGenerator']['arguments'][
            'constant']['parameterOfFunction']['testArguments']['results']
        # FIXME:
        method = metatask['classes']['taskGenerator'].lower()
        self.sdf_extenion = SDFExtension(method)
        if variables is not None:
            self.sdf_extenion.set_scales(convert(variables))
        self.sdf_extenion.set_result_dataset(result_paras)

    def __set_results(self, results):
        for r in results:
            simple_result = convert(r['result'])
            if self.metatask['taskGenerator']['arguments'].get('variable') != None:
                simple_variable = convert(self.__get_variable_from_task(self.metatask, r['message']))
            else:
                simple_variable = None
            self.sdf_extenion.add_value(simple_variable, simple_result)

    def __get_variable_from_task(self, metatask, task_data):
        variables = copy.deepcopy(metatask['taskGenerator']['arguments']['variable'])
        for var in variables:
            links = var['link'].split('.')
            temp_dict = task_data
            for step in links:
                temp_dict = temp_dict[step]
            value = temp_dict[var['name']]
            var['value'] = value
        return variables

    def __save(self):
        return self.sdf_extenion.save()
