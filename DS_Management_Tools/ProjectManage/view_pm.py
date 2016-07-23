#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import render_template, request, redirect, make_response, jsonify, session
from ProjectManage import app, YamlEditor
import hashlib
import threading
import subprocess
import httplib
import json
from flask_login import login_required
from AutoPoller.System.YamlWatcher import YamlWatcher
from ProjectManage.YamlHelper import *
from conf import __conf__, get_ctypes


@app.route('/')
@login_required
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    next_url = request.args.get('next')
    print(session, next_url)
    if session.get('user_id') is not None:
        return redirect(next_url or '/')
    if next_url is None:
        return render_template('login.html')
    return render_template('login.html', next_url=next_url)


@app.route('/set-project', methods=['GET', 'POST'])
@login_required
def set_project():
    if request.method == 'POST':
        return render_template('manip_project.html', ctypes=get_ctypes(), project=request.form['project'])
    return render_template('select_project.html', projects=YamlEditor.get_all_project())


@app.route('/get-info/<proj>')
@login_required
def get_info(proj):
    data = db.components.find()
    ctype = request.args['type']
    base_ctype = ctype[0: ctype.find('_')]
    component_info_all = YamlEditor.get_project_data(proj).get(ctype, {'Available': [], 'Base': ''})
    names = [item['path']
             for item in data if item['type'] == base_ctype]
    available = component_info_all.get('Available', [])
    base = component_info_all.get('Base') or ''
    new_names = [name for name in names if name not in available + [base]]
    replace_list = lambda ls: [os.path.relpath(item, __conf__['edrisDatabaseParameters']).replace(os.sep, '.')
                               for item in ls]
    red = {'base': os.path.relpath(base,
                                   __conf__['edrisDatabaseParameters']).replace(os.sep, '.') if base != '' else '',
           'available': replace_list(available), 'new_comp': replace_list(new_names)}
    return make_response(json.dumps(red))


@app.route('/save-info/<proj>', methods=['POST'])
@login_required
def save_info(proj):
    ctype = request.form['type']
    available = request.form['available']
    base = request.form['base']
    try:
        YamlEditor.save_proj(proj, ctype, json.loads(available), json.loads(base))
    except:
        import traceback
        print traceback.format_exc()
    return make_response()


@app.route('/start_proj_simulation/<proj>')
@login_required
def start_proj_simulation(proj):
    proj_path = os.path.join(__conf__['edrisProjectBasePath'], proj.replace('.', os.sep))
    print proj_path
    watcher = YamlWatcher(False, proj_path)
    threading.Thread(target=watcher.run).start()
    return make_response()


@app.route('/set-new-component')
@login_required
def set_new_component():
    return render_template('new_component.html')


@app.route('/submit', methods=['POST'])
@login_required
def submit():
    operator_id = request.form['name']
    path = request.form['path']

    description = request.form['description']
    comp_type = request.form['type']
    relative_path = get_relative_path(path)
    name = get_component_name(relative_path)
    absolute_path = os.path.join(__conf__['edrisBasePath'], relative_path)
    if os.path.exists(absolute_path):
        hv = hashlib.md5(absolute_path).hexdigest()
        c = dict()
        c['hash'] = hv
        c['operator_id'] = operator_id
        c['path'] = relative_path
        c['description'] = description
        c['files'] = os.listdir(absolute_path)
        c['type'] = comp_type
        db.components.update({'hash': c['hash']}, c, upsert=True, safe=True)
        address = 'DL-EA402all'
        url = 'https://' + __conf__['projectManageSetting']['host'] + ':' + \
            str(__conf__['projectManageSetting']['port']) + '/setprojects/' + c['hash']

        temp1 = 'Liebe DEDRIS Architekten,%0D%0A%0D%0Awir habe neue folgende Bedatung erstellt.%0D%0A%0D%0A'
        temp1 += 'Komponent: ' + name + "%0D%0AType: " + c['type']
        temp1 += '%0D%0ABeschreibung: ' + c['description']
        temp1 += '%0D%0ADateien Liste: %0D%0A'
        for file in c['files']:
            temp1 += '     %s' % file + '%0D%0A'
        temp1 += '%0D%0ALinke URL: ' + url
        temp1 += '%0D%0A%0D%0AOperator Name: ' + c['operator_id']
        import AutoPoller.Component
        thread_component_build = threading.Thread(target=AutoPoller.Component.main)
        thread_component_build.start()
        return render_template('mail.html', address=address, name=name, bodystring=temp1)
    else:
        return render_template('NotFound.html')


@app.route('/setprojects/<hv>', methods=['GET', 'POST'])
@login_required
def set_projects(hv):
    if request.method == 'POST':
        save_projects(request)
        return redirect('/')
    else:
        results = db.components.find({'hash': hv})
        if results.count() == 0:
            return render_template('NotFound.html')
        path = results[0]['path']
        comp_name = get_component_name(path)
        description = results[0]['description']
        file_list = results[0]['files']
        operator = results[0]['operator_id']
        comp_type = results[0]['type']
        project_list = get_project_by_component_list(path, path, comp_type)
        return render_template('setprojects.html', name=comp_name, path=path, description=description,
                               file_list=file_list, projects=project_list, operator=operator)


@app.route('/rename', methods=['GET', 'POST'])
@login_required
def renameproject():
    if request.method == 'GET':
        return render_template('rename.html')
    else:
        old_path = request.form['path']
        new_path = request.form['post_newpath']
        comment = request.form['comment']
        move_folder(old_path, new_path, comment)
        return render_template('rename.html')


@app.route('/get_fs_list/<path>')
@login_required
def test_web(path):
    if path == 'Battery':
        return render_template('test_tree.html', basepath=__conf__['edrisDatabaseEESParameters'])
    elif path == 'All':
        return render_template('test_tree.html', basepath=__conf__['edrisDatabaseParameters'])
    elif path == 'ElectricMachine':
        return render_template('test_tree.html', basepath=__conf__['edrisDatabaseEMParameters'])
    elif path == 'DCDCConverter':
        return render_template('test_tree.html', basepath=__conf__['edrisDatabaseDCDCParameters'])
    elif path == 'Charger':
        return render_template('test_tree.html', basepath=__conf__['edrisDatabaseChargerParameters'])


@app.route('/getfilelist', methods=['GET', 'POST'])
@login_required
def get_file_list():
    root = request.args['file']
    root = os.path.join(__conf__['edrisBasePath'], root)
    get_dirlist = lambda root: [f for f in os.listdir(root) if os.path.isdir(os.path.join(root, f))]
    filelist = get_dirlist(root)
    jsonlist = []
    for fn in filelist:
        filedict = {}
        filedict['title'] = fn
        filedict['key'] = os.path.join(root, fn).replace(__conf__['edrisBasePath'] + os.sep, '')
        filedict['isFolder'] = True
        filedict['expand'] = not len(get_dirlist(os.path.join(root, fn))) > 0
        filedict['isLazy'] = len(get_dirlist(os.path.join(root, fn))) > 0
        jsonlist.append(filedict)
    string = json.dumps(jsonlist, indent=2)
    return make_response(string)


@app.route('/update-svn', methods=['GET'])
@login_required
def update_svn():
    try:
        print 'update svn'
        info = subprocess.check_output('svn update --username %s --password %s' % (__conf__['svn']['username'], __conf__['svn']['password']),
                                       cwd=__conf__['svn']['componentsPath'], shell=True)
        print info
        for line in info.splitlines():
            if line.find('revision ') >= 0:
                return make_response(line[line.find('revision ') + len('revision '):])
        return make_response(info)
    except Exception:
        info = subprocess.call('svn cleanup {0}'.format(__conf__['svn']['password']))
        return make_response("problem with svn update, trying to clean up")


@app.route('/get-filenames', methods=['GET'])
@login_required
def get_filenames():
    abs_path = os.path.join(__conf__['edrisBasePath'], request.args['folder'])
    if os.path.exists(abs_path):
        filenames = os.listdir(abs_path)
        string = ''
        for name in filenames:
            string += '<li>' + name + '</li>'
        return make_response(string)
    else:
        return make_response()


@app.route('/system', methods=['GET'])
@login_required
def get_system_info():
    return render_template('system_info.html')


@app.route('/check-system-info')
@login_required
def check_system_info():
    conn = httplib.HTTPConnection(__conf__['webSetting']['host'],
                                  __conf__['webSetting']['port'])
    conn.request('GET', '/get-workers-info')
    response = conn.getresponse()
    data = json.loads(response.read())
    ls_t = [{'name': key, 'value': data[key]} for key in data.keys()]
    conn = httplib.HTTPConnection(__conf__['webSetting']['host'],
                                  __conf__['webSetting']['port'])
    conn.request('GET', '/get-tasks-info')
    response = conn.getresponse()
    data = json.loads(response.read())
    sum_list = []
    precent_list = []
    for ls in data.values():
        _sum = sum(ls)
        sum_list.append(_sum)
        precent_list.append([float(i) * 100 / float(_sum) for i in ls])
    ls1 = {'controllers': data.keys(), 'values': zip(*precent_list), 'sum': sum_list}

    return jsonify(speed=ls_t, controller=ls1)


@app.route('/shutdown')
@login_required
def shutdown():
    conn = httplib.HTTPConnection(__conf__['webSetting']['host'],
                                  __conf__['webSetting']['port'])
    conn.request('GET', '/get-workers-info')
    response = conn.getresponse()

    return response.read()
