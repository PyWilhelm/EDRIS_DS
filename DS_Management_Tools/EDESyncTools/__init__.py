#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import shutil
import yaml

from conf import __conf__, get_project_list, get_yaml_data


def check_modified(source_path, local_file_path):
    if os.path.exists(source_path):
        last_modified_time = os.path.getmtime(source_path)
    else:
        print 'the source file is not existed! Please check info.yaml'
    if os.path.exists(local_file_path):
        local_file_time = os.path.getmtime(local_file_path)
    else:
        return True
    return last_modified_time > local_file_time


def sync(local_path, source_path):
    source_path = os.path.join(__conf__['edePath'], source_path)
    local_file_path = os.path.join(local_path, __conf__['syncPath'], os.path.basename(source_path))
    if check_modified(source_path, local_file_path):
        shutil.copyfile(source_path, local_file_path)
        print 'modified since last synchronization and copy'
    else:
        print 'not modified since last synchronization'


def run():
    project_list = get_project_list()
    for project_path in project_list:
        yaml_data = get_yaml_data(project_path, 'Information')
        sync(project_path, yaml_data['EDE_Link'])
