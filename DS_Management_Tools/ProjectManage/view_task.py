#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import render_template, request, make_response, send_file, send_from_directory, jsonify
from ProjectManage import app
import hashlib
import threading
import subprocess
import time
import numpy
import shutil
import matplotlib
import gc
import socket
matplotlib.use("Agg")
from flask_login import login_required
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import axes3d
from ProjectManage.YamlHelper import *
from conf import __conf__
import TaskController.SPS
import TaskController.BBVAP

import TaskController.PISystem
import ProjectManage.validate as va


@app.route('/pi-system-sdf', methods=['GET', 'POST'])
@login_required
def set_pi_system_sdf():
    if request.method == 'POST':
        tid = request.form['tid']
        modelname = request.form['modelname']
        n_max = float(request.form['n_max'])
        n_eck = float(request.form['n_eck'])
        HVConsumption = float(request.form['HVConsumption'])
        RCIend_terminate = float(request.form['RCIend_terminate']) / 100
        path_battery = str(request.form['Battery'])
        path_em = str(request.form['ElectricMachine'])

        em_abs_path = os.path.join(__conf__['edrisBasePath'], path_em) if path_em != '' else None
        battery_abs_path = os.path.join(__conf__['edrisBasePath'], path_battery) if path_battery != '' else None

        print "em_abs_path is", em_abs_path
        print "battery_abs_path is", battery_abs_path

        pi_parameters = {u'n_eck': n_eck, u'n_max': n_max, u'HV_consumption': HVConsumption,
                         u'motorOrGenerator': None, u'numberOfParalellCell': None,
                         u'setNumberOfParallelCells': None, u'RCIend_terminate': RCIend_terminate}
        edb_paths_all = {u'Battery_01': battery_abs_path, u'ElectricMachine_01': em_abs_path}
        edb_paths = {key: edb_paths_all[key] for key in edb_paths_all if edb_paths_all[key] is not None}
        input_data = dict(pi_parameters=pi_parameters, edb_paths=edb_paths, model_name=modelname)
        app.results[tid]['data'] = {'clientHost': socket.gethostbyaddr(request.remote_addr)[0],
                                    'taskName': 'pi_system_sdf'}
        app.results[tid]['input'] = input_data
        app.results[tid]['start'] = time.time()
        app.results[tid]['function'] = 'pi-system-sdf'

        t = threading.Thread(target=TaskController.PISystem.start_controller,
                             args=(tid, input_data, app.results[tid], None, True))
        app.results[tid]['thread'] = t
        t.start()
        return make_response()
    else:
        tid = hashlib.md5(threading.current_thread().getName() + str(time.time())).hexdigest()
        app.results[tid] = dict()

        return render_template('pi_system_sdf.html', tid=tid)


@app.route('/pi-tool-master', methods=['GET', 'POST'])
@login_required
def set_pi_tool_master():
    if request.method == 'POST':
        tid = request.form['tid']
        n_max = float(request.form['n_max'])
        n_eck = float(request.form['n_eck'])
        y_max = float(request.form['y_max'])
        HVConsumption = float(request.form['HVConsumption'])
        path_battery = str(request.form['Battery'])
        path_em = str(request.form['ElectricMachine'])

        em_abs_path = os.path.join(__conf__['edrisBasePath'], path_em) if path_em != '' else None
        battery_abs_path = os.path.join(__conf__['edrisBasePath'], path_battery) if path_battery != '' else None

        pi_parameters = {u'n_eck': n_eck, u'n_max': n_max, u'HV_consumption': HVConsumption,
                         u'motorOrGenerator': None, u'numberOfParalellCell': None,
                         u'setNumberOfParallelCells': None}
        edb_paths_all = {u'Battery_01': battery_abs_path, u'ElectricMachine_01': em_abs_path}
        edb_paths = {key: edb_paths_all[key] for key in edb_paths_all if edb_paths_all[key] is not None}

        import PISlides.PIConnectModel
        print 'start posting'
        input_data = dict(pi_parameters=pi_parameters, edb_paths=edb_paths, y_max=y_max)

        app.results[tid]['data'] = {'clientHost': socket.gethostbyaddr(request.remote_addr)[0],
                                    'taskName': 'pi_tool_master'}
        app.results[tid]['input'] = input_data
        app.results[tid]['start'] = time.time()
        app.results[tid]['function'] = 'pi-tool-master'

        t = threading.Thread(target=PISlides.PIConnectModel.start_pi,
                             args=('pi-tool-master', input_data, app.results[tid]))
        app.results[tid]['thread'] = t
        t.start()
        return make_response()
    else:
        tid = hashlib.md5(threading.current_thread().getName() + str(time.time())).hexdigest()
        app.results[tid] = dict()
        return render_template('pi_tool_master.html', tid=tid)


@app.route('/set-BBVAP', methods=['GET', 'POST'])
@login_required
def set_BBVAP():
    if request.method == 'POST':
        tid = request.form['tid']
        componentnames = request.form['componentnames'].splitlines()
        revision_number = get_svn_revision_number()
        for componentname in componentnames:
            componentname = componentname[componentname.find('EDRIS_'):]
            setNcAgingFactor = str(float(request.form['NcAging']))
            setRiAgingFactor = str(float(request.form['RiAging']))
            app.results[tid]['data'] = {'clientHost': socket.gethostbyaddr(request.remote_addr)[0], 'taskName': 'BBVAP'}
            app.results[tid][componentname] = dict()
            app.results[tid][componentname]['input'] = {
                'componentname': componentname,
                'setNcAgingFactor': setNcAgingFactor,
                'setRiAgingFactor': setRiAgingFactor}
            app.results[tid]['components'].append(componentname)
            app.results[tid]['start'] = time.time()
            app.results[tid]['function'] = 'bbvap'
            if componentname == '':
                filenames = []
            else:
                abs_path = os.path.join(__conf__['edrisBasePath'], componentname)
                filenames = os.listdir(abs_path)

            userinput = {'Battery': {'data': [[f] for f in filenames if f.find('.mat') >= 0]},
                         'setNcAgingFactor': setNcAgingFactor,
                         'setRiAgingFactor': setRiAgingFactor,
                         'componentname': componentname}

            t = threading.Thread(target=TaskController.BBVAP.start_controller,
                                 args=(tid, userinput, app.results[tid][componentname], None, True, revision_number))
            app.results[tid][componentname]['thread'] = t
            t.start()
        return make_response()
    else:
        revision_number = get_svn_revision_number()
        tid = hashlib.md5(threading.current_thread().getName() + str(time.time())).hexdigest()
        app.results[tid] = dict()

        app.results[tid]['components'] = []
        return render_template('settaskBBVAP.html', revision_number=revision_number, tid=tid)


@app.route('/Battery-SPS-Plot', methods=['GET', 'POST'])
@login_required
def set_Battery_SPS():
    if request.method == 'POST':
        tid = request.form['tid']
        setRci = request.form['setRci']
        setTemp = request.form['setTemp']
        StopTime = request.form['StopTime']
        _, error = va.validate_sps_plot_value({'setRci': setRci, 'setTemp': setTemp, 'StopTime': StopTime})
        if error is None:
            print error
            return jsonify(validate=json.dumps(error, indent=2))
        componentname = request.form['componentname']
        if len(componentname) > 0:
            componentname = componentname[componentname.find('EDRIS_'):]
        app.results[tid]['data'] = {'clientHost': socket.gethostbyaddr(request.remote_addr)[0], 'taskName': 'SPS Plot'}
        app.results[tid]['input'] = {'componentname': componentname,
                                     'setRci': setRci,
                                     'setTemp': setTemp,
                                     'StopTime': StopTime,
                                     'build': {}}
        if componentname == '':
            filenames = []
        else:
            abs_path = os.path.join(__conf__['edrisBasePath'], componentname)
            filenames = os.listdir(abs_path)
        app.results[tid]['start'] = time.time()
        app.results[tid]['function'] = 'sps_plot'
        userinput = app.results[tid]['input']
        userinput['build']['Battery'] = {'data': [[f] for f in filenames if f.find('.mat') >= 0]}
        t = threading.Thread(target=TaskController.SPS.start_controller,
                             args=(tid, userinput, app.results[tid], None, True, 'BatteryPlot'))
        app.results[tid]['thread'] = t
        t.start()
        return make_response()
    else:
        revision_number = get_svn_revision_number()
        tid = hashlib.md5(threading.current_thread().getName() + str(time.time())).hexdigest()
        app.results[tid] = dict()

        return render_template('setBatterySPS.html', revision_number=revision_number, tid=tid)


@app.route('/System-SPS-Plot', methods=['GET', 'POST'])
@login_required
def set_system_sps_plot():
    if request.method == 'POST':
        tid = request.form['tid']
        setRci = request.form['setRci']
        setTemp = request.form['setTemp']
        StopTime = request.form['StopTime']
        setSpeed = request.form['setSpeed']
        SOH = request.form['SOH']
        battery = request.form['Battery']
        emachine = request.form['ElectricMachine']
        setNcAgingFactor = str(float(request.form['NcAging']))
        setRiAgingFactor = str(float(request.form['RiAging']))

        _, error = va.validate_sps_plot_value({'setRci': setRci,
                                               'setTemp': setTemp,
                                               'StopTime': StopTime,
                                               'setSpeed': setSpeed,
                                               'SOH': SOH})
        if error is None:
            print error
            return jsonify(validate=json.dumps(error, indent=2))
        app.results[tid]['data'] = {'clientHost': socket.gethostbyaddr(request.remote_addr)[0], 'taskName': 'SPS Plot'}
        app.results[tid]['input'] = {'BatteryComponentName': battery,
                                     'ElectricMachineComponentName': emachine,
                                     'setRci': setRci,
                                     'setTemp': setTemp,
                                     'StopTime': StopTime,
                                     'setSpeed': setSpeed,
                                     'SOH': SOH,
                                     'setNcAgingFactor': setNcAgingFactor,
                                     'setRiAgingFactor': setRiAgingFactor,
                                     'build': {}}
        app.results[tid]['start'] = time.time()
        app.results[tid]['function'] = 'sps_plot'
        userinput = app.results[tid]['input']

        if battery == '':
            filenames = []
        else:
            abs_path = os.path.join(__conf__['edrisBasePath'], battery)
            filenames = os.listdir(abs_path)
        userinput['build']['Battery_01'] = {'data': [[f] for f in filenames if f.find('.mat') >= 0]}
        if emachine == '':
            filenames = []
        else:
            abs_path = os.path.join(__conf__['edrisBasePath'], emachine)
            filenames = os.listdir(abs_path)
        userinput['build']['ElectricMachine_01'] = {'data': [[f] for f in filenames if f.find('.mat') >= 0]}

        t = threading.Thread(target=TaskController.SPS.start_controller,
                             args=(tid, userinput, app.results[tid], None, True, 'SystemPlot'))
        app.results[tid]['thread'] = t
        t.start()
        return make_response()
    else:
        revision_number = get_svn_revision_number()
        tid = hashlib.md5(threading.current_thread().getName() + str(time.time())).hexdigest()
        app.results[tid] = dict()

        return render_template('system_sps_plot.html', revision_number=revision_number, tid=tid)


@app.route('/mytasks')
@login_required
def get_my_tasks():
    ip = request.remote_addr
    tasks = app.get_results_from_ip(ip)
    return render_template('mytasks.html', tasks=tasks)


@app.route('/get-mytasks/<tid>')
@login_required
def get_mytasks_tid(tid):
    task = app.get_result_from_tid(tid)
    if task == {}:
        return render_template('NotFound.html')
    if task.get('input') == None:
        task = {'components': [task[k] for k in task if k not in ['components', 'data']]}
    return render_template('mytask_tid.html', tid=tid, task=task)


@app.route('/get-results/<tid>')
@login_required
def get_results(tid):
    if app.results.get(tid) == None:
        return make_response('timeout of the page, please refresh.')
    response_info = ''
    result_info = ''
    report_file_string = ''
    all_finish = 0
    with_report = False
    for componentname in app.results[tid]['components']:
        shortname = os.path.basename(componentname)
        controller = app.results[tid][componentname].get('controller')
        finish = app.results[tid].get('finish', False)
        progress_info = None
        if controller is None:
            finish, progress_info, building_error = controller.check_progress()
        if not finish:
            if progress_info is None:
                response_info += '<b>' + shortname + ':</b><br/>' + \
                    progress_information_html_string(progress_info, building_error)
            else:
                response_info += '<b>' + shortname + ':</b><br/>' + '<b>Initialize... Please wait</b><p>'
            all_finish += 1
        else:
            if app.results[tid][componentname].get('error') == True:
                response_info += '<font color="red"><b>' + shortname + ' ERROR!</b><br/>'
                response_info += '<b>' + app.results[tid][componentname]['returnValue'] + '</b><br/></font>'
            else:
                with_report = True
                app.results[tid][componentname]['thread'].join()
                string = ''
                if app.results[tid]['function'] == 'bbvap':
                    string = app.results[tid][componentname]['returnValue']
                elif app.results[tid]['function'] == 'sps_plot':
                    app.results[tid]['sps-thread'] = threading.Thread(target=__make_result_sps, )
                    string = __make_result_sps(app.results[tid], progress_info)

                total_time = time.time() - app.results[tid]['start']
                log_file_string = u'<p><a target="_blank" href="/log/%s">log file</a>' % id(
                    app.results[tid][componentname]['controller'])

                result_info += '<b>' + shortname + ':</b><br/>' + string + ' <pdf:nextpage />'
                rs = u'<p>total simulation time: %.2f seconds' % (total_time,) + log_file_string \
                    + progress_information_html_string(progress_info, building_error)
                response_info += '<b>' + shortname + ':</b><br/>' + rs
    if app.results[tid].get('finish') == True or (all_finish == 0 and with_report):
        # for componentname in app.results[tid]['components']:
            # if app.results[tid][componentname].get('controller') != None:
            #    app.results[tid][componentname]['controller']
        app.results[tid]['finish'] = True
        if app.results[tid].get('finish_time') == None:
            app.results[tid]['finish_time'] = time.time()
        result_info = 'Subversion Revision Number: ' + get_svn_revision_number() + '<br/><br/>' + result_info
        report_file_string = u'<b><p><a target="_blank" href="/report/%s">Download report.zip</a> <p></b>' % tid
        gc.collect()
        return make_response('<b>ALL FINISHED!</b> <p>' + report_file_string + '<br/>' +
                             result_info + '<p>' + response_info)

    else:
        return make_response(result_info + '<p>' + response_info)


@app.route('/get-result/<tid>')
@login_required
def get_result(tid):
    if app.results.get(tid) == None:
        return make_response('timeout of the page, please refresh.')
    finish = False
    if app.results[tid].get('finish') == True:
        finish = True
    controller = app.results[tid].get('controller')
    if controller is None:
        finish, progress_info, building_error = controller.check_progress()
    else:
        finish = False
        building_error = []
        progress_info = None
    if not finish:
        if building_error != []:
            return make_response('errors are: <br/>' + str(building_error))
        if progress_info is None:
            return make_response(progress_information_html_string(progress_info, building_error))
        return make_response('<b>Initialize... Please wait</b><p>')
    else:
        app.results[tid]['thread'].join()
        string = ''
        if app.results[tid]['function'] == 'bbvap':
            pass
        elif app.results[tid]['function'] == 'sps_plot':
            string = __make_result_sps(app.results[tid])
        elif app.results[tid]['function'] == 'sps_mat':
            string = '<p><a target="_blank" href="/mat/%s">Download Mat File</a>' % (app.results[tid]['SPS'],)
        elif app.results[tid]['function'] == 'pi-system-sdf':
            string = '<p><a target="_blank" href="/sde/%s">Download SDF File</a>' % (app.results[tid]['result'],)
        elif app.results[tid]['function'] == 'pi-tool-master':
            directory = os.path.join(__conf__['outputPath'], 'tmp_sdf')
            shutil.copy(app.results[tid]['result'], directory)
            basename = os.path.basename(app.results[tid]['result'])
            string = '<p><a target="_blank" href="/sde/%s">Download Powerpoint</a>' % (basename)
        elif app.results[tid]['function'] == 'charging':
            string = '<p><a target="_blank" href="/sde/%s">Download SDE File</a>' % (app.results[tid]['result'],)
        print string

        total_time = time.time() - app.results[tid]['start']
        log_file_string = u'<p><a target="_blank" href="/log/%s">log file</a>' % id(app.results[tid]['controller'])
        string = string.decode('utf-8', 'ignore')
        rs = string + u'<p>total simulation time: %.2f seconds' % (total_time,) + log_file_string \
            + progress_information_html_string(progress_info, building_error)
        # if app.results[tid].get('controller') != None:
        #    del app.results[tid]['controller']
        app.results[tid]['finish'] = True

        if app.results[tid].get('finish_time') == None:
            app.results[tid]['finish_time'] = time.time()
        print app.results[tid]
        gc.collect()
        return make_response(rs)


def __make_result_sps(session):
    sdf_extension = session['SPS']
    # if isinstance(sdf_extension, SDFExtension) == False:
    #    return sdf_extension
    scales = sdf_extension.actual_scales
    zs = sdf_extension.result_datasets
    x, y = numpy.meshgrid(scales[1].data, scales[0].data)
    response_string = ''
    for zds in zs:
        if zds.name != 'summary.batteryPower' and zds.name != 'summarySystemSPS.mechanicalPower':
            continue
        print zds.data
        z = numpy.fabs(zds.data)
        fig = plt.contourf(x, y, z, 10, alpha=.75, cmap=cm.coolwarm)
        C = plt.contour(x, y, z, 10, colors='black', linewidth=.5)
        plt.clabel(C, inline=1, fontsize=10)
        # TODO: Unit hackcode
        plt.xlabel(scales[1].name + ' (' + str(scales[1].unit) + ')')
        plt.ylabel(scales[0].name + ' (' + str(scales[0].unit) + ')')
        plt.title(zds.name)
        plt.colorbar(fig, shrink=0.5, aspect=5)
        plt.savefig('temp.svg')

        with open('temp.svg', 'rb') as f:
            data = f.read().encode('base64')
        os.remove('temp.svg')
        response_string += '<img src="data:image/svg+xml;base64,{0}"><br/>'.format(data)
        plt.close('all')
    return response_string


def progress_information_html_string(info, building_error):
    if len(info) == 0:
        return u'<b>Initialize... Please wait</b>'
    revert_prgress_info = zip(*info)
    response_str = u'<p><b>Progress Information:<p>total:'
    response_str += u'%d, successful: %d, failed:%d <p></b>' % (sum(revert_prgress_info[0]),
                                                                sum(revert_prgress_info[1]),
                                                                sum(revert_prgress_info[2]))
    error_list = []
    for i, info in enumerate(info):
        response_str += u'<p>metatask %d: total:<b>%d</b>, successful: <b>%d</b>, failed:<b>%d</b>' % (
            i + 1, info[0], info[1], info[2])
        if info[0] == 0:
            response_str += u'  (Building Model)'
    response_str += '<br/><br/>'

    if building_error != []:
        response_str += u'  (Building Error)'
        error_list = list(set(building_error))
        for e in error_list:
            response_str += '<font color="red"><b>' + e + '<br/></b></font>'
    return response_str + u'<p>'


@app.route('/log/<cid>', methods=['GET'])
@login_required
def get_log_file(cid):
    response = ''
    with open(os.path.join(__conf__['outputPath'], 'tmp_result', 'result-%s.txt' % cid)) as f:
        lines = f.readlines()
        for line in lines:
            line = line.replace(' ', '&nbsp;')
            response += line + '<br/>'
    return make_response(response)


@app.route('/mat/<matfile>', methods=['GET'])
@login_required
def get_mat_file(matfile):
    matfile = os.path.join(__conf__['outputPath'], 'mat', matfile)
    return send_file(matfile,
                     mimetype='application/octet-stream',
                     as_attachment=True,
                     attachment_filename='result.mat')


@app.route('/sde/<sdefile>')
@login_required
def get_sde_file(sdefile):
    directory = os.path.join(__conf__['outputPath'], 'tmp_sdf')
    return send_from_directory(directory,
                               sdefile,
                               mimetype='application/octet-stream',
                               as_attachment=True,
                               attachment_filename=sdefile)


def get_svn_revision_number():
    try:
        info = subprocess.check_output('svn info --username %s --password %s' %
                                       (__conf__['svn']['username'], __conf__['svn']['password']),
                                       cwd=__conf__['edrisBasePath'], shell=True)
        for line in info.splitlines():
            if line.find('Revision: ') >= 0:
                return line.replace('Revision: ', '')
    except Exception:
        info = "error loading revisions"
    return info


@app.route('/report/<tid>', methods=['GET'])
@login_required
def get_report_zip(tid):
    zippath = os.path.join(__conf__['outputPath'], 'report_achieve', 'report' + tid)
    dirpath = os.path.join(__conf__['outputPath'], 'tmp_report', 'report' + tid)
    if not os.path.exists(zippath):
        create_zip_file(zippath, dirpath)
        shutil.rmtree(dirpath)
    return send_file(zippath + '.zip',
                     mimetype='application/octet-stream',
                     as_attachment=True,
                     attachment_filename='report.zip')


def create_zip_file(path, dirpath):
    shutil.make_archive(path, format='zip', root_dir=dirpath)


def run():
    app.run()
