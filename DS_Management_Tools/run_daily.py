'''
Created on 05.08.2014

@author: q350609
'''

from TaskController.BaseClass.Controller import Controller
from conf import __conf__, get_project_list, get_yaml_data
import copy, types, os, subprocess
from TaskController.SPS.MetataskOverriderSPS import MetataskOverriderSPS
from TaskController.SPS import start_controller

def update_svn():
    old_cwd = os.getcwd()
    os.chdir(__conf__['edrisBasePath'])
    svn_log = subprocess.check_output('svn update --username qxg2705 --password mam1kawa',shell=True)
    os.chdir(__conf__['edrisComponentsPath'])
    svn_log = subprocess.check_output('svn update --username qxg2705 --password mam1kawa',shell=True)
    os.chdir(old_cwd)

def get_model_variation_list(proj_list):
    return_list = []
    for proj in proj_list:
        models_by_proj = {'proj': proj, 'redeclareModels':[]}
        yaml_data = get_yaml_data(proj)
        base_model = dict()
        variable = dict()
        for k in yaml_data.keys():
            components = yaml_data[k]
            if isinstance(components, types.ListType):
                for component in components:
                    if component.get('Base') != None:
                        base_model[component['Info']] = component['Base']['path']
                        variable[component['Info']] = [avail['path'] for avail in component['Available']]
            else:
                if components.get('Base') != None:
                    base_model[components['Info']] = components['Base']['path']
                    variable[components['Info']] = [avail['path'] for avail in components['Available']]
        models_by_proj['redeclareModels'].append(base_model)       
        for k in base_model.keys():

            for item in variable[k]:
                temp_ = copy.deepcopy(base_model)
                temp_[k] = item
                models_by_proj['redeclareModels'].append(temp_)
        
        import json
        print json.dumps(models_by_proj, indent=2)
        return_list.append((proj, models_by_proj))
        
    return return_list

def get_model_data(model_components_path):
    model_redeclare_structure = {}
    for k in model_components_path:
        model_redeclare_structure[k] = {'data': []}
        path = os.path.join(__conf__['edrisBasePath'], model_components_path[k])
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
        

if __name__ == '__main__':
    c = Controller()
    model_variation_list = get_model_variation_list(get_project_list())

    results = {}
    for model_variation in model_variation_list:
        results[model_variation[0]] = []
        for model in model_variation[1]['redeclareModels']:
            temp_model_data = get_model_data(model)
            print 'temp_model_data', temp_model_data
        print '-*-----*--'
        '''result_future = start_controller(None, {'build': temp_model_data, 'n_max': '10000', 
                                                    'n_eck': '5000', 'setNcAgingFactor': '1.3', 
                                                    'setRiAgingFactor': '0.8'}, controller=c, plot=False)
            results[model_variation[0]].append(result_future)
    for r in results.keys():
        for i in results[r]:
            print r.get()
            
    '''