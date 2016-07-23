import os, re

from conf import __conf__, db
import conf


sing2pl = {'Inverter': 'Inverters', 'ElectricMachine': 'ElectricMachines',
            'Battery' : 'Batteries', 'Charger' : 'Chargers', 'DCDCConverter' : 'DCDCConverters'}
    
sub_type_dict = {'G': 'General', 'C': 'Controller', 'L': 'Loss', 'E': 'EnergyAnalysis',
                'T': 'Thermal', 'S': 'StressIndicator'}

def check_components():
    rv = []
    components = db.components.find()
    for comp in components:
        path = comp['path']
        ctype = comp['type']
        filelist = os.listdir(os.path.join(__conf__['edrisBasePath'], path))
        error, report_fs = check_component_filelist(filelist, ctype)
        if error == True:
            rv.append({'path': path, 'report': report_fs, 'error': error})
            continue
        error, report_lib = check_component_lib(filelist, ctype)
        if error == True:
            rv.append({'path': path, 'report': report_fs + report_lib, 'error': error})
            continue
        rv.append({'path': path, 'report': report_fs + report_lib, 'error': False})
    for item in rv:
        if item['error'] == True:
            db.components.update({'path': item['path']}, {'$set': {'deprecated': True, 
                                                             'files': os.listdir(os.path.join(__conf__['edrisBasePath'], item['path']))}})
        else:
            db.components.update({'path': item['path']}, {'$set': {'deprecated': False,
                                                             'files': os.listdir(os.path.join(__conf__['edrisBasePath'], item['path']))}})
    return rv
      
def check_component_filelist(filelist, ctype):
    if len(filelist) == 0:
        return True, ['Folder is empty!']
    if len(filelist) == 1 and 'work' in filelist:
        return True, ['Folder is empty (except "work")!']
    rv = []
    error = False
    c = [f for f in filelist if re.compile(r'^C\d{3}.*\.mat$').match(f) != None]
    g = [f for f in filelist if re.compile(r'^G\d{3}.*\.mat$').match(f) != None]
    l_em = [f for f in filelist if re.compile(r'^L\d{3}.*_EM\.mat$').match(f) != None]
    l_inv = [f for f in filelist if re.compile(r'^L\d{3}.*_Inv\.mat$').match(f) != None]
    l = [f for f in filelist if re.compile(r'^L\d{3}.*\.mat$').match(f) != None]
    t = [f for f in filelist if re.compile(r'^T\d{3}.*\.mat$').match(f) != None]
    m = [f for f in filelist if re.compile(r'^M_.*\.m$').match(f) != None]
    sdf = [f for f in filelist if re.compile(r'^.*\.sdf$').match(f) != None]
    sdf_int = [f for f in filelist if re.compile(r'^.*_interpolated\.sdf$').match(f) != None]
    fmu = [f for f in filelist if re.compile(r'^.*\.fmu').match(f) != None]
    fmu_cos = [f for f in filelist if re.compile(r'^.*_Cosim\.fmu').match(f) != None]
    pcp = [f for f in filelist if re.compile(r'^PCP_.*\.mat').match(f) != None]
    pdf = [f for f in filelist if re.compile(r'^.*\.pdf').match(f.lower()) != None]
    docx = [f for f in filelist if re.compile(r'^.*\.doc[x]?').match(f.lower()) != None]
    
    if ctype == 'ElectricMachine':
        if len(c) < 1:
            rv.append('Controller Data missing!')
            error = True
        if len(c) > 1:
            rv.append('Multiple Controller Data found!')
            error = True
        if len(g) != 1:
            rv.append('General Data Error!')
            error = True
        if len(l_em) != 1:
            rv.append('Loss Data Error!')
            error = True
        if len(l_inv) != 1:
            rv.append('Inverter Loss Data Error!')
            error = True
        #if len(m) != 1:
        #    rv.append('Member Data Error!')
        if len(sdf) < 1:
            rv.append('SDF Data Error')
        if len(sdf_int) != 1:
            rv.append('SDF Interpolated Data Error')
        #if len(pdf) + len(docx) != 1:
        #    rv.append('Document File Error')
        #    error = True
    elif ctype == 'Battery':
        if len(c) < 1:
            rv.append('Controller Data missing!')
            error = True        
        if len(c) > 1:
            rv.append('Multiple Controller Data found!')
            error = True
        if len(g) != 1:
            rv.append('General Data Error!')
            error = True
        if len(m) != 1:
            rv.append('Member Data Error!')
            error = True
        if len(t) != 1:
            rv.append('Thermal Data Error!')
            error = True
        if len(fmu) < 2:
            rv.append('FMU Data missing!')
        if len(pcp) < 1:
            rv.append('PCP Data missing!')
        if len(pdf) + len(docx) != 1:
            rv.append('Document File Error')
            error = True
    elif ctype in ['DCDCConverter', 'Charger']:
        if len(t) > 0:
            rv.append('Thermal Data found unexpected')
            error = True 
        if len(c) < 1:
            rv.append('Controller Data missing!')
            error = True        
        if len(c) > 1:
            rv.append('Multiple Controller Data found!')
            error = True
        if len(l) != 1:
            rv.append('Loss Data missing or multiple found!')
            error = True
        if len(m) != 1:
            rv.append('Member Data missing or multiple found!!')
            error = True   
        if len(pdf) + len(docx) != 1:
            rv.append('Document File Error')
            error = True
    elif ctype == 'PowerElectronics':
        if len(t) > 0:
            rv.append('Thermal Data found unexpected')
            error = True 
        if len(c) < 1:
            rv.append('Controller Data missing!')
            error = True        
        if len(c) > 1:
            rv.append('Multiple Controller Data found!')
            error = True
        if len(l) != 1:
            rv.append('Loss Data missing or multiple found!')
            error = True
        if len(m) != 1:
            rv.append('Member Data missing or multiple found!!')
            error = True   
    elif ctype == 'EDrive':
        if len(c) < 1:
            rv.append('Controller Data missing!')
            error = True
        if len(c) > 1:
            rv.append('Multiple Controller Data found!')
            error = True
        if len(g) != 1:
            rv.append('General Data Error!')
            error = True
        if len(l_em) != 1:
            rv.append('Loss Data Error!')
            error = True
        if len(l_inv) != 1:
            rv.append('Inverter Loss Data Error!')
            error = True
        if len(fmu) != 2:
            rv.append('FMU Data Error!')
        if len(fmu_cos) != 1:
            rv.append('FMU Cos Data Error!')
        if len(m) != 1:
            rv.append('Member Data Error!')
            error = True
    elif ctype == 'SuperCap':
        if len(c) != 1:
            rv.append('Controller Data Error!')
            error = True
        if len(g) != 1:
            rv.append('General Data Error!')
            error = True
        if len(t) != 1:
            rv.append('Thermal Data Error!')
    elif ctype == 'WireHarness':
        pass
    return error, rv
            
def check_component_lib(filelist, ctype):
    rv = []
    error = False
    filelist = [f.replace('.mat', '') for f in filelist if os.path.splitext(f)[1] == '.mat']
    for f in filelist:
        subtype = sub_type_dict[f[0]]
        _ = [__conf__['libraryPath']['EdrisLibData'], ctype, subtype]
        path = os.path.join(__conf__['edrisComponentsPath'], *_)
        if os.path.exists(path) == False and ctype != 'EDrive':
            rv.append('The Path not found ' + path)
            error = True
        elif ctype == 'EDrive':
            err, _rv = check_component_lib([f + '.mat'], 'ElectricMachine')
            error = err
            rv += _rv
        else:
            file_list = [_f for _f in os.listdir(path) if _f == f + '.mo']
            if len(file_list) == 0:
                if ctype == 'ElectricMachine' and subtype == 'Loss':
                    err, _rv = check_component_lib([f + '.mat'], 'Inverter')
                    error = err
                    rv += _rv
                else:
                    rv.append('Record Data %s is missing. ' %(f,))
                    error = True
    return error, rv

def check_projects(project_list=[]):
    rv = []
    check_components()
    proj_list = conf.get_project_list() if len(project_list) == 0 else [p for p in project_list if len(p) > 0]
    for proj in proj_list:
        temp_rv = []
        data = conf.get_yaml_data(proj)
        components = get_all_components_by_proj(data)
        for c in components:
            db_rs = db.components.find({'path': c})
            if db_rs.count() < 1:
                temp_rv.append('%s not in Database, please check and add this into Database before set in projects.' %(c, ))
            elif db_rs[0].get('deprecated') == True:
                temp_rv.append('%s is deprecated, please correct the error of components' %(c, ))
        rv.append({'path': proj, 'report': temp_rv})
    print rv
    return rv
                            
        
def get_all_components_by_proj(data):
    rv = []
    for key in data:
        for item in data[key]:
            if item['Base'] != None:
                rv.append(item['Base']['path'])
            rv.extend([p['path'] for p in item['Available']])
    rv = list(set(rv))
    return rv

