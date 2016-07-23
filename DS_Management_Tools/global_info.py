#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess, os, json, shutil

def set_pid(pid):
    if os.path.exists('globalinfo.json') == False:
        with open('globalinfo.json', 'w') as f:
            json.dump({'pid': []}, f)
    with open('globalinfo.json') as f:
        data_info = json.load(f)
    data_info['pid'].append(pid)
    data_info['pid'] = list(set(data_info['pid']))
    with open('globalinfo.json', 'w') as f:
        json.dump(data_info, f)

def kill_processes():
    with open('globalinfo.json') as f:
        data_info = json.load(f)
    global_pid = data_info['pid']
    for pid in global_pid:
        subprocess.call(['taskkill', '/F', '/PID', str(pid)])
    data_info['pid'] = []
    with open('globalinfo.json', 'w') as f:
        json.dump(data_info, f)

def clear_output():
    output = os.path.join(os.path.dirname(__file__), 'output')
    _dirs = ['mat', 'report_achieve', 'temp_build', 'tmp_report', 'tmp_result', 'tmp_sdf']
    [shutil.rmtree(os.path.join(output, _dir)) for _dir in os.listdir(output)]
    [os.makedirs(os.path.join(output, _dir)) for _dir in _dirs]

def clear_all():
    if os.path.exists('globalinfo.json') == True:
        kill_processes()
    clear_output()

