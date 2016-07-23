#!/usr/bin/env python
# -*- coding: utf-8 -*-
from AutoPoller import BaseChecker as checker
from AutoPoller.System.start_controller import start_controller
from ProjectManage import YamlHelper
from TaskController.BaseClass.Controller import Controller
import conf, json, copy, os, shutil, datetime, logging


class YamlWatcher(object):
    ''' Automatic execute simulation tasks, when the project configuration file (info.yaml) modified.
        
    '''
    
    def __init__(self, auto=True, oncmd_proj_name=''):
        print 'start'

        self.__database = [data for data in conf.db.projects.find()]
        if auto == True:
            __project_list = [proj['path'] for proj in checker.check_projects() if len(proj['report'])==0]
        else:
            __project_list = [proj['path'] for proj in checker.check_projects([oncmd_proj_name]) if len(proj['report'])==0]
        print __project_list
        self.all_proj_models_list = self.__get_new_redeclare(__project_list)
        self.redeclare_models = self.convert2redeclare_data()

        
    def run(self):
        '''main function to automatic run simulation
            input:    data of info.yaml 
                      historical data in database
            output:   simulation result data stored in mat file, mat file stored in project folder.
            todo:     svn commit
            
        '''
        c = Controller()
        number = 0
        for __proj in self.redeclare_models:
            system_data = __proj['systemData']
            for model in __proj['model']:
                input_data = copy.deepcopy(system_data)
                input_data['build'] = model

                result_file_path, failed_list = start_controller(input_data, controller=c)
                number += 1
                dest_dir = os.path.join(__proj['proj'], 'result-%s' %(str(datetime.date.today()), ))
                try:
                    os.makedirs(os.path.join(__proj['proj'], dest_dir))
                except:
                    pass
                if len(failed_list) > 0:
                    logging.error('Task failed: \n' + json.dumps(failed_list, indent=2))
                shutil.copy(result_file_path, dest_dir)
                
            for proj in self.all_proj_models_list:
                if proj.project_name == __proj['proj']:
                    data = {key:{'Base': proj[key].base, 'Available':proj[key].available, 'Info': key} for key in proj.keys()}
                    db_proj = self.__find(self.__database, proj.project_name)
                    if db_proj == None:
                        conf.db.projects.insert({'path': proj.project_name, 'data': data})
                    else:
                        for key in proj.keys():
                            if db_proj.get(key) == None:
                                db_proj[key] = {'Base': None, 'Available': []}
                            if db_proj[key]['Base'] == data[key]['Base']:
                                db_proj[key]['Available'].extend(data[key]['Available'])
                            else:
                                db_proj[key]['Base'] = data[key]['Base']
                                db_proj[key]['Available'] = data[key]['Available']
                            db_proj[key]['Info'] = key
                        conf.db.projects.update({'path': proj.project_name}, 
                                               {'$set': {'data': db_proj}}, 
                                               safe=True)
        c.stop(all_stop=True)
                
        
    def convert2redeclare_data(self):
        redeclare_data_list = []
        for proj in self.all_proj_models_list:
            model = proj.get_model_variation_list()
            temp_list = []
            for comp in model['redeclareModels']:
                temp_list.append( self.__get_model_data(comp))
            redeclare_data_list.append({'proj': model['proj'], 'model': temp_list, 'systemData': copy.deepcopy(proj.system_data)})
        return redeclare_data_list
                
        
    def __get_new_redeclare(self, proj_list):
        all_proj_models_list = []
        for proj in proj_list:
            data = conf.get_yaml_data(proj)
            system_data = conf.get_yaml_data(proj, 'SystemData')
            if self.__find(self.__database, proj) == None:
                all_proj_models_list.append(YamlData(proj, data, original=True).set_system_data(system_data)) 
                continue
            old_yaml_data = YamlData(proj, self.__find(self.__database, proj), original=False)
            new_yaml_data = YamlData(proj, data, original=True)
            all_proj_models_list.append(new_yaml_data.get_diff(old_yaml_data).set_system_data(system_data))
        return all_proj_models_list
    
    
    def __get_model_data(self, model_components_path):
        model_redeclare_structure = {}
        for k in model_components_path:
            model_redeclare_structure[k] = {'data': []}
            path = os.path.join(conf.__conf__['edrisBasePath'], model_components_path[k])
            if os.path.exists(path):
                filelist = [filename for filename in os.listdir(path) if filename.find('.mat') >= 0]
                for filename in filelist:
                    header_list = [i[0][0] for i in model_redeclare_structure[k]['data']]
                    if filename[0] in header_list:
                        model_redeclare_structure[k]['data'][header_list.index(filename[0])].append(filename)
                    else:
                        model_redeclare_structure[k]['data'].append([filename])
            else:
                print 'os.path.exists(path) == FALSE', path
        return model_redeclare_structure
    
    def __find(self, db, proj):
        for item in db:
            if item['path'] == proj:
                return item['data']
        return None


class YamlSubData(object):
    def __init__(self, item, orginal=True):
        if orginal == True:
            self.base = item['Base']['path']
            self.available = [i['path'] for i in item['Available']]
            self.ctype = item['Info']
        else:
            self.base = item['Base']
            self.available = item['Available']
            self.ctype = item['Info']
            
class YamlData(object):
    def __init__(self, project_name, data, original=True):
        if original == True:
            self.__dict = {item['Info']: YamlSubData(item, original) for key in data.keys() for item in data[key] if item['Base'] != None}
        else:
            self.__dict = {key: YamlSubData(data[key], original) for key in data.keys() if data[key]['Base'] != None}
        self.simulate_base = True
        self.project_name = project_name
        self.system_data = {}
    
    def keys(self):
        return self.__dict.keys()

    def __setitem__(self, key, value):
        self.__dict[key] = value

    def __getitem__(self, key):
        return self.__dict.get(key, None)
    
    def get_base_dict(self):
        return {key: self.__dict[key].base for key in self.__dict}
    
    def get_avaiable_dict(self):
        return {key: self.__dict[key].available for key in self.__dict}
    
    def get_diff(self, other):
        if other == None:
            return copy.deepcopy(self)
        elif self.get_base_dict() != other.get_base_dict():
            return copy.deepcopy(self)
        else:
            rv = copy.deepcopy(self)
            for key in self.keys():
                new_avail = [item for item in self[key].available if item not in other[key].available]
                rv[key] = YamlSubData({'Base': self[key].base, 'Available': new_avail, 'Info': key}, False)
            rv.simulate_base = False
            return rv
        
    def set_system_data(self, system_data):
        self.system_data = system_data
        return self
        
    def get_model_variation_list(self):
        models_by_proj = {'proj': self.project_name, 'redeclareModels':[]}
        base_dict = self.get_base_dict()
        available_dict = self.get_avaiable_dict()
        if self.simulate_base == True:
            redeclare_models = [base_dict]
        else:
            redeclare_models = []
        for k in base_dict.keys():
            for item in available_dict[k]:
                temp_ = copy.deepcopy(base_dict)
                temp_[k] = item
                redeclare_models.append(temp_)    
        models_by_proj['redeclareModels'] = redeclare_models
        return models_by_proj
        
    