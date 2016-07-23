#!/usr/bin/env python
# -*- coding: utf-8 -*-
from multiprocessing import Lock
import json
import sys
import os
import yaml
import types
import platform
import time
import global_info


global_info.clear_all()


from pymongo import MongoClient
reload(sys)
sys.setdefaultencoding('utf-8')


def __conf():
    local_config = os.path.join(os.path.dirname(__file__), 'configuration_local')
    default_config = os.path.join(os.path.dirname(__file__), 'configuration')
    if os.path.exists(local_config):
        conf_path = local_config
    else:
        conf_path = default_config
    return get_configuration(conf_path)


def get_configuration(conf_path):
    c = dict()
    c['programPath'] = os.path.abspath(os.path.dirname(__file__))
    sys.path.append(os.path.join(c['programPath'], 'dymola.egg'))
    with open(os.path.join(conf_path, 'conf_controller.json'), 'r') as f:
        c.update(json.load(f))
    with open(os.path.join(conf_path, 'conf_web.json'), 'r') as f:
        c.update(json.load(f))
    c['edrisComponentsPath'] = c['svn']['componentsPath']
    c['edrisBasePath'] = c['edrisComponentsPath']
    c['outputPath'] = os.path.join(c['programPath'], c['outputPath'])
    for key in c.keys():
        if isinstance(c[key], types.StringType):
            if platform.system() == "Windows":
                c[key] = c[key].replace('/', '\\')
            else:
                c[key] = c[key].replace('\\', '/')
    if os.environ.get('jenkins_mode'):
        c['edrisBasePath'] = os.path.join(c['programPath'], '..', 'edrisAscent')
        c['edrisComponentsPath'] = os.path.join(c['programPath'], '..', 'EdrisAscent')
    return c

__conf__ = __conf()


def check_project(folder_path):
    subdir_list = os.listdir(folder_path)
    filter_list = filter(lambda x: x in subdir_list, __conf__['edrisProjectPattern'])
    if len(filter_list) == len(__conf__['edrisProjectPattern']):
        return True
    else:
        return False


def get_project_list():
    project_folder_list = [
        os.path.join(__conf__['edrisProjectBasePath'], dir) for dir in __conf__['edrisProjectPaths']]
    project_list = [os.path.join(dir, subdir)
                    for dir in project_folder_list
                    if os.path.exists(dir)
                    for subdir in os.listdir(dir)
                    if subdir.find(__conf__['edrisProjectKeyWord']) >= 0
                    if check_project(os.path.join(dir, subdir)) == True]
    return project_list


def get_yaml_data(project_path, key='data'):
    try:
        with open(os.path.join(__conf__['edrisProjectBasePath'], project_path, 'info.yaml')) as f:
            return yaml.safe_load(f.read()).get(key, None)
    except Exception as e:
        raise e


def save_yaml(project_path, data, key='data'):
    with open(os.path.join(__conf__['edrisProjectBasePath'], project_path, 'info.yaml'), 'r') as f:
        yaml_data = yaml.safe_load(f.read())
    with open(os.path.join(__conf__['edrisProjectBasePath'], project_path, 'info.yaml'), 'w') as f:
        yaml_data[key] = data
        yaml.safe_dump(yaml_data, f, default_flow_style=False)


def get_dymosim_path(modelname, hashvalue):
    modelpath = modelname.replace('.', os.sep)
    return [os.path.join(modelpath, hashvalue, 'dymosim.exe'),
            os.path.join(modelpath, hashvalue, 'dsin.txt'),
            __conf__['buildSetting']['dymolaLicensePath']]

# TODO: Hackcode of definition component types of system


def get_ctypes():
    return ['Battery_01', 'Battery_02', 'Charger_01', 'Charger_02', 'DCDCConverter_01', 'ElectricMachine_01', 'ElectricMachine_02']

sync_lock = Lock()


def threaded_safe(function):
    def wrapper(*args, **kw):
        sync_lock.acquire()
        rv = function(*args, **kw)
        sync_lock.release()
        return rv
    return wrapper


class DBI():

    def __init__(self):
        self.db = None
        self._tasks = None

    def get_db(self):
        self.db = self.db if self.db != None else MongoClient(
            __conf__['databaseSetting']['dbmsHost'])
        return self.db
        while True:
            try:
                self.db = self.db if self.db != None else MongoClient(
                    __conf__['databaseSetting']['dbmsHost'])
                if self.db.alive():
                    return self.db
                else:
                    raise Exception()
            except:
                print 'DB not ready'
                time.sleep(5)
            pass

    @property
    def projects(self):
        return self.get_db()['edris_proj']['projects']

    @property
    def components(self):
        return self.get_db()['edris_proj']['components']

    @property
    def tasks(self):
        self._tasks = self.get_db()['edirs_controller_d'][
            'results'] if self._tasks == None else self._tasks
        return self._tasks

db = DBI()

db = DBI()
