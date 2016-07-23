#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import re
import sys, nose
import unittest, conf, os

import AutoPoller.BaseChecker as chkr


err_list = []

escape_none_name = lambda x : re.sub(r'[^a-zA-Z_0-9]', r'_', x)

def get_function(name):
    def check_exception(arg_dict):
        arg_dict['test_generator'].__name__ = str(name)
        if arg_dict['exception_type']== 'Error':
            raise Exception(arg_dict['exception_value'])
    check_exception.description = name
    return check_exception
        
def test_generator():
    error_infos = check_main()
    for name, exception_type, exception_value in error_infos:
        check_exception = get_function(name)
        arg_dict = dict_no_str(exception_type=exception_type, 
                               exception_value=exception_value, 
                               test_generator=test_generator)
        yield check_exception, arg_dict

class dict_no_str(dict):
    """ wrapper class to hackaround python x units print out  """
    
    def __init__(self,*args,**kwargs): 
        dict.__init__(self,*args,**kwargs) 

    def __repr__(self):
        return ''

    def __str__(self):
        return ''

    def __unicode__(self): 
        return u''

def check_data_dir_map(data_dir):
    test_name = escape_none_name(unicode(u'_test_' + os.path.relpath(data_dir, 
                                                    conf.__conf__['edrisBasePath']).replace(os.sep, '_')))
    try:
        ctype = get_ctype_by_path(data_dir)
        pattern_check, lib_check = check_and_find_lib(data_dir, ctype)
        except_str = '\n' + err2str(pattern_check) + '\n' + err2str(lib_check)

        if pattern_check[1] != 'Error' and lib_check[1] != 'Error':
            exception_type = 'Warning'
            return (test_name, exception_type, except_str)
        else:
            exception_type = 'Error'
    except Exception as err:
        except_str = unicode(err)
        exception_type = 'Error'
    
    return (test_name, exception_type, except_str)

def check_main():
    all_errors_collection = []

    comp_sub_list = get_all_list()
    for comp in comp_sub_list:

        data_dir_list, error_list = check_filesystem(comp)
        if len(error_list) == 0 and len(data_dir_list) != 0:
            for err in error_list:
                pass
            if len(data_dir_list) == 0:
                all_errors_collection.append(get_comp_warning(comp, 'Message: No parameter folder found.'))
            else:
                all_new_tests = map(check_data_dir_map, data_dir_list)
                all_errors_collection += all_new_tests
    return all_errors_collection 

def get_comp_err(component, err_str):
    return (unicode(component), 'Error', )

def get_comp_warning(component, err_str):
    return (unicode(component), 'Warning', )

def err2str(error_tuple, indent=0):
    indent_str = '\n'
    for i in range(indent):
        indent_str += '\t'
    error_str = indent_str + error_tuple[1] + ':' + indent_str + 'file:///'+ error_tuple[0] + indent_str + str(error_tuple[2])
    return re.sub(r'(.*edris/EDRIS_database)', r'C:/\1', error_str) 

def get_all_list():
    comp_list = [(u'02_ElectricEnergyStorageSystem', 1), (u'04_EM', 1), (u'05_DCDC', 1), 
                  (u'06_Charger', 1),  #(u'09_EDrive', 1),  #(u'03_PowerElectronics', 1) , 
                  (u'07_WireHarness', 1), (u'10_SuperCap', 1),]
                  
    returnlist = []
    for c in comp_list:
        try:
            returnlist.extend(get_comp_list(c[0], c[1]))
        except Exception as e:
            pass
            #print e
    return returnlist
            
def get_comp_list(comp_subfolder, level):
    base = os.path.join(conf.__conf__['edrisBasePath'], conf.__conf__['edrisDatabase'], 
                        u'ComponentData', comp_subfolder, u'02_ComponentData')
    if os.path.exists(base) == False:
        raise Exception("dummy_2")
    main_list = [os.path.join(base, _dir) for _dir in os.listdir(base) if os.path.isdir(os.path.join(base, _dir))]
    if level == 1:
        return main_list
    if level == 2:
        sub_list = [os.path.join(_main, _dir) for _main in main_list for _dir in os.listdir(_main) if os.path.isdir(os.path.join(_main, _dir))]
    return sub_list
    
def check_filesystem(dirname):
    err_list = []
    # method 1
    sub_rel_list = os.listdir(dirname)
    sub_abs_list = [os.path.join(dirname, _dir) for _dir in os.listdir(dirname)]
    sub_list_prex = [sub[0:2] if len(sub) >= 2 else sub for sub in sub_rel_list]
    for prex in sub_list_prex:
        try:
            _ = int(prex)
        except:
            if os.path.isfile(sub_abs_list[sub_list_prex.index(prex)]) == True:
                err_list.append((os.path.dirname(sub_abs_list[sub_list_prex.index(prex)]), 'Error', 'File system organization Error'))
            else:
                err_list.append((sub_abs_list[sub_list_prex.index(prex)], 'Error', 'File system naming Error ' + prex))
            return '', err_list
    # check 10_parameter
    param_dir = ''
    for abs_dir in sub_abs_list:
        if os.path.relpath(abs_dir, dirname).find('10') == 0:
            param_dir = abs_dir
            if os.path.relpath(abs_dir, dirname) != '10_Parameter':
                err_list.append((abs_dir, 'Warning', 'Naming Warning, should be 10_Parameter'))
            break
    data_dir_list = []
    if param_dir != '':
        data_dir_list = check_parameter_function_1(param_dir)
    return data_dir_list, err_list
        
def check_parameter_function_1(param_dir):
    data_dir_list = [os.path.join(param_dir, _dir) for _dir in os.listdir(param_dir) if os.path.isdir(os.path.join(param_dir, _dir))]
    return data_dir_list
            
def check_and_find_lib(bedatung_dir, ctype):
    error1, report_fs1 = chkr.check_component_filelist(os.listdir(bedatung_dir), ctype)
    error2, report_fs2 = chkr.check_component_lib(os.listdir(bedatung_dir), ctype)
    return (bedatung_dir, 'Error' if error1 else 'Warning', report_fs1), (bedatung_dir, 'Error' if error2 else 'Warning', report_fs2)

def get_ctype_by_path(path):
    if path.find('02_ElectricEnergyStorageSystem') >= 0:
        return 'Battery'
    elif path.find('04_EM') >= 0:
        return 'ElectricMachine'
    elif path.find('05_DCDC') >= 0:
        return 'DCDCConverter'
    elif path.find('06_Charger') >= 0:
        return 'Charger'
    elif path.find('03_PowerElectronics') >= 0:
        return 'PowerElectronics'
    elif path.find('09_EDrive') >= 0:
        return 'EDrive'
    elif path.find('07_WireHarness') >= 0:
        return 'WireHarness'
    elif path.find('10_SuperCap') >= 0:
        return 'SuperCap'
    else:
        raise Exception(path + 'cannot determine the component type')
     
if __name__ == '__main__':
    # print check_main()

    module_name = sys.modules[__name__].__file__
    result = nose.run(argv=[sys.argv[0], module_name, '--with-xunit', ])
