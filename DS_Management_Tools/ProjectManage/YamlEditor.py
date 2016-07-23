#!/usr/bin/env python
# -*- coding: utf-8 -*-
import conf
import os
import yaml
import types


def get_all_project():
    proj_list = conf.get_project_list()
    return [(proj, os.path.relpath(proj,
                                   conf.__conf__['edrisProjectBasePath']).replace(os.sep, '.'))
            for proj in proj_list]


def get_project_data(proj_path, all=False):
    info_data = __get_data(proj_path, 'data')
    return __reconstruct(info_data, all)


def get_project_systemdata(proj_path):
    return __get_data(proj_path, 'systemData')


def set_project_systemdata(proj_path, new_data):
    yaml_data = __get_data(proj_path)
    yaml_data['systemData'] = new_data
    __save_data(proj_path, yaml_data)


def save_proj(proj_path, key, available, base):
    available_list = []
    for item in available:
        abs_path = os.path.join(
            conf.__conf__['edrisBasePath'], conf.__conf__['edrisDatabaseParameters'], item.replace('.', os.sep))
        if os.path.exists(abs_path) == False:
            raise Exception('The component is not found: ' + abs_path)
        filelist = os.listdir(abs_path)
        item = {'ReferenceInfo': filelist, 'path': os.path.relpath(abs_path, conf.__conf__['edrisBasePath'])}
        available_list.append(item)
    if isinstance(base, types.UnicodeType) and base != '':
        base_item = base
    elif isinstance(base, types.ListType) and len(base) > 0:
        base_item = base[0]
    else:
        base_item = None
    if base_item is not None:
        abs_path = os.path.join(
            conf.__conf__['edrisBasePath'], conf.__conf__['edrisDatabaseParameters'], base_item.replace('.', os.sep))
        if os.path.exists(abs_path) == False:
            raise Exception('The component is not found: ' + base_item)
        filelist = os.listdir(abs_path)
        base_item = {'ReferenceInfo': filelist, 'path': os.path.relpath(abs_path, conf.__conf__['edrisBasePath'])}
    else:
        base_item = None
    info_data = __get_data(proj_path)
    for _k in info_data['data'].keys():
        for _i in info_data['data'][_k]:
            if _i['Info'] == key:
                _i['Available'] = available_list
                _i['Base'] = base_item
                break
    else:
        ctype = key[0:key.find('_')]
        if info_data['data'].get(ctype) == None:
            if ctype in ['Battery', 'Charger', 'ElectricMachine']:
                info_data['data'][ctype] = [{'Base': None, 'Available': [], 'Info': str(ctype) + '_01'},
                                            {'Base': None, 'Available': [], 'Info': str(ctype) + '_02'}]
            else:
                info_data['data'][ctype] = [{'Base': None, 'Available': [], 'Info': str(ctype) + '_01'}]
        for _i in info_data['data'][ctype]:
            if _i['Info'] == key:
                _i['Available'] = available_list
                _i['Base'] = base_item
                break
    __save_data(proj_path, info_data)


def __get_data(proj, key=None):
    proj = __get_proj_path(proj)
    with open(os.path.join(proj, 'info.yaml')) as f:
        return yaml.load(f)[key] if key is not None else yaml.load(f)


def __save_data(proj, yaml_data):
    proj = __get_proj_path(proj)
    with open(os.path.join(proj, 'info.yaml'), 'w') as f:
        yaml.safe_dump(yaml_data, f, encoding='utf-8', allow_unicode=True, default_flow_style=False
                       )


def __get_proj_path(proj):
    if proj.find('.') >= 0:
        proj = proj.replace('.', os.sep)
        return os.path.join(conf.__conf__['edrisProjectBasePath'], proj)
    else:
        return proj


def __reconstruct(data, all):
    return_data = {}
    for key in data.keys():
        for item in data[key]:
            return_data[item['Info']] = {}
            avail = item['Available']
            base = item['Base']
            avail_list = [i['path'] for i in avail]
            if base is not None:
                base_value = base.get('path')
            else:
                base_value = None
            return_data[item['Info']]['Available'] = avail_list
            return_data[item['Info']]['Base'] = base_value
            if not all:
                if base_value is None and len(avail_list) is 0:
                    del return_data[item['Info']]
    return return_data
