#!/usr/bin/env python
# -*- coding: utf-8 -*-
from AutoPoller import BaseChecker as checker
from AutoPoller.Component._FMUBuilder import FMUBuilder
import conf, os, json, traceback


class ComponentWatcher(object):
    def __init__(self):
        self.__components = checker.check_components()
        self.__new_components = self.__get_new_components(self.__components)
    
    def __get_new_components(self, component_list):
        return [comp['path'] for comp in component_list 
                if u'.fmu' not in [os.path.splitext(_file)[1]
                               for _file in os.listdir(os.path.join(conf.__conf__['edrisBasePath'], comp['path']))]]
    
    def build_fmu(self):
        log_dict = {}
        for c in self.__new_components:
            try:
                comp_dict = [data for data in checker.db_comp.find({'path': c})][0]
                success, log = ComponentData(comp_dict).build_fmu()
                if success == False:
                    log_dict[c] = log
            except:
                log_dict[c] = traceback.format_exc()
        self.save()
        return log_dict
        
    def save(self):
        checker.check_components()
                
class ComponentData(object):
    def __init__(self, comp_dict):
        self.__path = os.path.join(conf.__conf__['edrisBasePath'], comp_dict['path'])
        self.__type = comp_dict['type']
        
    def get_path(self):
        return os.path.relpath(self.__path, conf.__conf__['edrisBasePath'])

    
    def build_fmu(self):
        try:
            cs, me, cs_log, me_log = FMUBuilder(self.__path, self.__type).build()
            if cs and me:
                return True, None
            else:
                return False, cs_log + '\n' + me_log
        except Exception as e:
            return False, str(e)
        
