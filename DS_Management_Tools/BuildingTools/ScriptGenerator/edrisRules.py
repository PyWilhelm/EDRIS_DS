#!/usr/bin/env python
# -*- coding: utf-8 -*-
from conf import __conf__
import os
import edrisRulesData as rules_data
from BuildingTools.ScriptGenerator.SpecificBase import SpecificBase


class _Rules(object):
    '''
    generate project data structure from file list of the components using edris rules
    '''

    def __init__(self, yaml_data, FMU=False):

        self.__in = self.prebuild(self.__get_data(yaml_data))

    def prebuild(self, data):
        result = dict()
        for key in data.keys():
            result[key] = dict()
            subdata = data[key]['data']
            for subtype in subdata.keys():
                for v in subdata[subtype]:
                    result[key][subtype] = [] if result[key].get(
                        subtype) == None else result[key][subtype]
                    r = self.__get_subcomponent_record(
                        v, data[key]['singularType'], subtype)
                    result[key][subtype].append({'record': r})
        return result

    def generate_rule_script(self):
        out = dict()
        for key in self.__in.keys():
            out[key] = dict()
            out[key]['child'] = dict()
            for subtype in self.__in[key]:
                out[key]['child'][subtype + 'LoadSelection'] = []
                for item in self.__in[key][subtype]:
                    r = item['record']
                    out[key]['child'][
                        subtype + 'LoadSelection'].append({'type': 'record', 'method': 'redeclare', 'value': r})
                if len(out[key]['child'][subtype + 'LoadSelection']) == 0:
                    del out[key]
        return out

    def __get_data(self, data):
        res = dict()
        for key in data.keys():
            res[key] = dict()
            res[key]['singularType'] = self.__get_singular_type(key)
            res[key]['pluralType'] = self.__get_plural_type(key)
            res[key]['data'] = dict()
            for d in data[key]['data']:
                k, v = self.__get_subcomponents(d)
                if res[key]['data'].get(k) is None:
                    res[key]['data'][k] = []
                for i in v:
                    '''res[key]['data'][k].append(i)'''
                    # FIXME: HACKCODE: check Loss data, Inverter or EMashine
                    if self.__check_inverter_loss(i, res[key]['singularType'], k):
                        res['Inverter'] = {
                            'pluralType': 'Inverters', 'singularType': 'Inverter', 'data': {k: [i]}}
                    else:
                        res[key]['data'][k].append(i)

        return res

    def __get_singular_type(self, ctype):
        return ctype.split('_')[0]

    def __get_plural_type(self, ctype):
        sing2pl = {'Inverter': 'Inverters', 'ElectricMachine': 'ElectricMachines',
                   'Battery': 'Batteries', 'Charger': 'Chargers', 'DCDCConverter': 'DCDCConverters'}
        return sing2pl[ctype.split('_')[0]]

    def __get_subcomponents(self, filelist):
        get_subcomponent_type = lambda x: rules_data.sub_type_dict[x[0]]
        datalist = [filename.replace(
            '.mat', '') for filename in filelist if filename.find('.mat') >= 0]
        return get_subcomponent_type(datalist[0]), datalist

    def __get_name(self, path):
        for _, item in __conf__['libraryPath'].items():
            if path.find(item) >= 0:
                path = os.path.relpath(
                    path, os.path.join(__conf__['edrisComponentsPath'], os.path.split(item)[0]))
                break
        return path

    def __get_subcomponent_record(self, name, singtype, subtype):
        _ = [__conf__['libraryPath']['EdrisLibData'], singtype, subtype]
        path = os.path.join(__conf__['edrisComponentsPath'], *_)
        file_list = [filename for filename in os.listdir(
            path) if filename == name + '.mo']
        if len(file_list) == 0:
            print 'No record has been matched. please check!', name, singtype, subtype
            raise Exception(
                'No record has been matched. please check! ' + name + '.mo, ' + singtype + ', ' + subtype)
        else:
            return self.__get_name(os.path.join(path, file_list[0].replace('.mo', ''))).replace(os.sep, '.')

    # FIXME: HACKCODE: only for check Inverter Loss data
    def __check_inverter_loss(self, name, singtype, subtype):
        _ = [__conf__['libraryPath']['EdrisLibData'], singtype, subtype]
        path = os.path.join(__conf__['edrisComponentsPath'], *_)
        file_list = [f for f in os.listdir(path) if f == name + '.mo']
        if len(file_list) == 0:
            if singtype == 'ElectricMachine' and subtype == 'Loss':
                return True
        return False


class PiRules(object):

    def __init__(self, input_data, FMU=False):
        for data in input_data.values():
            if data.get('data') is not None and type(data['data']) is not list:
                data['data'] = [data['data']]
        self._input = input_data

    def generate_rule_script(self):
        out = dict()
        for key in self._input.keys():
            out[key] = dict()
            out[key]['child'] = {}
            out[key]['child']['data'] = []
            for item in self._input[key]['data']:
                out[key]['child']['data'].append(
                    {'value': item.replace('\\', '.').replace('/', '.')})
        return out

Rules = PiRules


class EDBBuildInfo(object):

    def __init__(self, edb_paths=dict(), spec_data=dict(), rules_cls=PiRules):
        self.edb_paths = edb_paths
        self.spec_data = rules_data.default_spec_data
        self.spec_data.update(spec_data)
        self.rules_cls = rules_cls

    def get_build_info(self):
        if (self.edb_paths == dict()) or (self.edb_paths is None):
            return dict()
        edp = self.edb_paths
        build_info = {key: {'data': edp[key]} for key in edp.keys()}
        edris_rules = SpecificBase(self.rules_cls(build_info), self.spec_data)
        model_building_info_list = edris_rules.generate_specific_script_metatask_format()
        return self._convert_build_info(model_building_info_list)

    @staticmethod
    def _convert_build_info(build_info_list):
        building_info = dict()
        for k in build_info_list:
            converted_link = EDBBuildInfo._constant_build_info(k)
            building_info = dict_merge(building_info, converted_link)
        return building_info['buildingInfo']

    @staticmethod
    def _constant_build_info(item):
        links = item['link'].split('.')
        redeclare_struct = dict()
        temp_ref = redeclare_struct
        for l in links:
            if temp_ref.get(l) == None:
                temp_ref[l] = dict()
            temp_ref = temp_ref[l]
        temp_ref[item['name']] = item['value'][0]
        EDBBuildInfo._check_plausibility(redeclare_struct)
        return redeclare_struct

    @staticmethod
    def _check_plausibility(redeclare_struct):
        pass

    @staticmethod
    def _get_mat(edb_path):
        mat_files = [[f] for f in os.listdir(edb_path) if f.find('.mat') >= 0]
        return mat_files


def dict_merge(a, b, path=None):
    "merges b into a"
    if path is None:
        path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                dict_merge(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass  # same leaf value
            else:
                raise Exception(u'Conflict at %s' %
                                '.'.join(path + [unicode(key)]))
        else:
            a[key] = b[key]
    return a
