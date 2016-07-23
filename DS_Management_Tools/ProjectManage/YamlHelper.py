#!/usr/bin/env python
# -*- coding: utf-8 -*-
from conf import get_project_list, get_yaml_data, __conf__, save_yaml, db
import os
import types
import yaml
import platform


def get_relative_path(path):
    index = path.find('EDRIS_')
    if index >= 0:
        return path[index:]
    else:
        return path


def get_component_name(rel_path):
    def is_stopword(name):
        stopwords = ['Component', 'component', 'Parameter', 'parameter', 'database']
        for word in stopwords:
            if name.find(word) >= 0:
                return True
        return False
    component_keys = [key + '.' for key in rel_path.split(os.sep) if not is_stopword(key)]
    name = ''.join(component_keys)[0:-1]
    return name


def initialize_yaml(proj_path):
    ctypes = ['Battery', 'ElectricMachine', 'Charger', 'DCDCConverter']
    for ctype in ctypes:
        initialize_yaml_by_type(proj_path, ctype)


def initialize_yaml_by_type(proj_path, type, data):
    if type in ['Battery', 'ElectricMachine', 'Charger']:
        data[type] = [{'Base': None, 'Available': [], 'Info': str(type) + '_01'},
                      {'Base': None, 'Available': [], 'Info': str(type) + '_02'}]
    else:
        data[type] = [{'Base': None, 'Available': [], 'Info': str(type) + '_01'}]

    with open(os.path.join(__conf__['edrisProjectBasePath'], proj_path, 'info.yaml'), 'w') as f:
        yaml.safe_dump({'data': data}, f)
    return data


def get_project_by_component_list(path, component_path, component_type):
    results = []

    proj_list = get_project_list()

    get_proj_name = lambda x: os.path.relpath(x, __conf__['edrisProjectBasePath']).replace('\\', '.')

    for proj_path in proj_list:
        yaml_data = get_yaml_data(proj_path)
        if yaml_data is None:
            yaml_data = {}
        component_data = yaml_data.get(component_type)
        if component_data is None or component_data == '' or len(component_data) == 0:
            yaml_data = initialize_yaml_by_type(proj_path, component_type, yaml_data)
            component_data = yaml_data[component_type]
        if isinstance(component_data, types.DictType):
            component_data = [component_data]

        for item in component_data:
            item_name = '%s.%s' % (get_proj_name(proj_path), item['Info'])
            if item['Base'] != None and item['Base']['path'] == component_path:
                results.append((item_name, 2))
            else:
                for comp_data in item['Available']:
                    if comp_data['path'] == component_path:
                        results.append((item_name, 1))
                        break
                else:
                    results.append((item_name, 0))

    return results


def get_project_component_info(item_name):
    split_list = item_name.split('.')
    component_type = split_list[-1][0: split_list[-1].find('_')]
    component_number = split_list[-1][split_list[-1].find('_') + 1:]
    project_path = os.path.join(__conf__['edrisProjectBasePath'], *split_list[0:-1])
    return project_path, component_type, int(component_number)


def set_available(yaml, component, number=1):  # 0->1, 2->1
    if isinstance(yaml, types.DictType):
        if yaml['Base'] == component:
            yaml['Base'] = None
        if yaml['Available'] is None:
            yaml['Available'] = [component]
        elif isinstance(yaml['Available'], types.ListType):
            if component not in yaml['Available']:
                yaml['Available'].append(component)
        else:
            if yaml['Available'] != component:
                yaml['Available'] = [yaml['Available'], component]
    else:
        yaml[number - 1] = set_available(yaml[number - 1], component, number)
    return yaml


def set_base(yaml, component, number=1):  # 0->2, 1->2
    if isinstance(yaml, types.DictType):
        remove_available(yaml, component, number)
        old_base = yaml['Base']
        yaml['Base'] = component
        if old_base is not None:
            yaml = set_available(yaml, old_base, number)
    else:
        yaml[number - 1] = set_base(yaml[number - 1], component, number)
    return yaml


def remove_available(yaml, component, number=1):  # 1->0
    if isinstance(yaml, types.DictType):
        if isinstance(yaml['Available'], types.ListType):
            if component in yaml['Available']:
                yaml['Available'].remove(component)
        elif yaml['Available'] == component:
            yaml['Available'] = []
    else:
        yaml[number - 1] = remove_available(yaml[number - 1], component, number)
    return yaml


def remove_base(yaml, component, number=1):  # 2->0
    if isinstance(yaml, types.DictType):
        if yaml['Base'] == component:
            yaml['Base'] = None
    else:
        yaml[number - 1] = remove_base(yaml[number - 1], component, number)
    return yaml


def remove_component(yaml, component, number=1):  # 2->0, 1->0
    yaml = remove_base(yaml, component, number)
    yaml = remove_available(yaml, component, number)
    return yaml


def save_projects(request):
    proj_list = [(key, request.form[key]) for key in request.form.keys() if not key == 'component_name']
    component_name = request.form['component_name']
    results = db.components.find({'path': component_name})
    component_data = {'path': results[0]['path'],
                      'ReferenceInfo': results[0]['files']}
    for name, value in proj_list:
        proj_path, comp_type, comp_number = get_project_component_info(name)
        yaml_data = get_yaml_data(proj_path)
        comp_yaml_data = yaml_data[comp_type]
        if comp_yaml_data is None:
            comp_yaml_data = {'Base': None, 'Available': [], 'Info': str(comp_type) + '.01'}
        if value == u'2':
            yaml_data[comp_type] = set_base(comp_yaml_data, component_data, comp_number)
        elif value == u'1':
            yaml_data[comp_type] = set_available(comp_yaml_data, component_data, comp_number)
        elif value == u'0':
            yaml_data[comp_type] = remove_component(comp_yaml_data, component_data, comp_number)
        save_yaml(proj_path, yaml_data)


def update_database(old, new):
    if platform.system() == "Windows":
        old = old.replace('\\', '\\\\')
        new = new.replace('\\', '\\\\')
    with open(os.path.join('db', 'components.json'), 'r') as f:
        data = f.read()
    with open(os.path.join('db', 'components.json'), 'w') as f:
        f.write(data.replace(old, new))


def update_yaml(old, new):
    project_list = get_project_list()
    for proj in project_list:
        with open(os.path.join(__conf__['edrisProjectPaths'], proj, 'info.yaml'), 'r') as f:
            data = f.read()
        with open(os.path.join(__conf__['edrisProjectPaths'], proj, 'info.yaml'), 'w') as f:
            f.write(data.replace(old, new))


def move_folder(old_path, new_path, comment):
    old_dir = os.getcwd()
    os.chdir(__conf__['edrisBasePath'])
    old_list = old_path.split('/')
    new_list = new_path.split('/')
    basedir = []
    for i in range(len(old_list)):
        if old_list[i] == new_list[i]:
            basedir.append(new_list[i])
        else:
            break
    dir_index = i
    basedir = os.path.join(*basedir)
    old_path = os.path.join(basedir, old_list[dir_index])
    new_path = os.path.join(basedir, new_list[dir_index])
    os.chdir(basedir)
    file_list = os.listdir(old_list[dir_index])
    os.system("svn mkdir \"" + new_list[dir_index] + "\"")

    cp_file = lambda x: os.system(
        "svn cp \"" + os.path.join(old_list[dir_index], x) + "\" \"" + new_list[dir_index] + "\"")
    rm_file = lambda x: os.system(
        "svn delete \"" + os.path.join(old_list[dir_index], x) + "\" \"" + new_list[dir_index] + "\"")
    map(cp_file, file_list)
    map(rm_file, file_list)
    os.system("svn delete \"" + old_list[dir_index] + "\"")
    os.system("svn update")
    os.system("svn commit -m \"" + comment + "\"")

    if os.path.exists(old_list[dir_index]):
        os.system("svn delete \"" + old_list[dir_index] + "\"")
        os.system("svn commit -m \"" + comment + "\"")

    os.chdir(old_dir)

    update_database(old_path, new_path)
    update_yaml(old_path, new_path)
