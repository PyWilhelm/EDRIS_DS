#!/usr/bin/env python
# -*- coding: utf-8 -*-
from TaskController.BBVAP.MetataskOverriderBBVAP import MetataskOverriderBBVAP
from TaskController.BaseClass.Controller import Controller
import json
import threading
import time
import os
from multiprocessing import Queue

import ProjectManage.table_to_pdf as table2pdf
MetataskOverrider = MetataskOverriderBBVAP

from TaskController.BBV import start_controller as bbv_controller


def start_controller(tid, userinput, session={}, controller=None, block=True, revision='unknown'):
    try:
        controller = Controller(priority=3) if controller is None else controller
        session['controller'] = controller
        bbv_input = {'Battery': userinput['Battery']}
        temp_session = {}

        ap1_result_future = bbv_controller(bbv_input, temp_session, controller, block=False)

        print "===============================AP1 result:=================="
        _dir = os.path.dirname(os.path.abspath(__file__))
        result_ap_data_future = calculate(_dir + '\\metatask_BBVAPs.json', userinput, controller, SOH=0)
        result_ap_bol_data_future = calculate(_dir + '\\metatask_BBVAPsBOL.json', userinput, controller, SOH=1)
        result_ap_dauer_future = calculate(_dir + '\\metatask_BBVDauer.json', userinput, controller, SOH=1)
        result_one_c_future = calculate(_dir + '\\metatask_BBVOneC.json', userinput, controller, SOH=1)

        result_data_future = calculate(_dir + '\\metatask_BBVData.json', userinput, controller, SOH=1)

        result_ftp72_future = calculate(_dir + '\\metatask_BBVFTP72.json', userinput, controller, SOH=1)
        result_wltp_future = calculate(_dir + '\\metatask_BBVWLTP.json', userinput, controller, SOH=1)

        result_ftp72_full_future = calculate(_dir + '\\metatask_BBVFTP72Full.json', userinput, controller, SOH=1)
        result_wltp_full_future = calculate(_dir + '\\metatask_BBVWLTPFull.json', userinput, controller, SOH=1)
        result_mkv_full_future = calculate(_dir + '\\metatask_BBVMKVFull.json', userinput, controller, SOH=1)

        ap1_result = ap1_result_future.get(None, 'string')
        result_ap_data = result_ap_data_future.get(None, 'intermediate')
        result_ap_bol_data = result_ap_bol_data_future.get(result_ap_data, 'intermediate')
        result_ap_dauer = result_ap_dauer_future.get(result_ap_bol_data, 'intermediate')
        result_one_c = result_one_c_future.get(result_ap_dauer, 'string')

        result_data = result_data_future.get(None, 'string')

        result_ftp72 = result_ftp72_future.get(None, 'intermediate')
        result_wltp = result_wltp_future.get(result_ftp72, 'string')

        result_ftp72_full = result_ftp72_full_future.get(None, 'intermediate')
        result_wltp_full = result_wltp_full_future.get(result_ftp72_full, 'intermediate')
        result_mkv_full = result_mkv_full_future.get(result_wltp_full, 'string')

        string = ap1_result + '<br/>' + result_one_c + '<br/>' + \
            result_data + '<br/>' + result_mkv_full + '<br/>' + result_wltp
        # string = ap1_result + '<br/>' + result_one_c + '<br/>' + result_data + '<br/>' +  result_wltp
        string = string.decode('utf-8', 'ignore')
        save_and_update(string, userinput, tid, revision)
    except Exception as e:
        import traceback
        print '-----------------------------------------fatal error !!!!!!!!!!!!!!!!!!!!!!!!!!1'
        print traceback.format_exc()
        print '-----------------------------------------fatal error !!!!!!!!!!!!!!!!!!!!!!!!!!1'
        controller.set_error()
        string = str(e)
        session['error'] = True
    session['returnValue'] = string
    controller.stop()
    return True


def save_and_update(html, input_data, tid, revision):
    filedir = input_data['componentname']
    filename = 'report-%s.pdf' % (input_data['componentname'].replace('/', os.sep).split(os.sep)[-1])
    if table2pdf.svn_commit(tid, html, input_data['componentname'],
                            filename, os.path.join(filedir, filename).replace(os.sep, '/'),
                            'automated simulation: add report.pdf', revision):
        return os.path.join(filedir, filename).replace(os.sep, '/')
    else:
        return False


def calculate(json_file, userinput, controller, prev_result=None, SOH=0):
    with open(json_file) as f:
        metatask_data = json.load(f)
    metatask_data = override(metatask_data, userinput, SOH)
    return controller.add_metatask(metatask_data)


def override(metatask_temp, userinput, SOH=0):
    mto = MetataskOverrider(metatask_temp)
    return mto.override_all(userinput, SOH)
