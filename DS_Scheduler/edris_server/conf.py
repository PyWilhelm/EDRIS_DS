#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import sys
import time
import httplib
import os
from pymongo import MongoClient


class Conf(object):

    def __init__(self):
        self.WORKER = {'READY': 0,
                       'BUSY': 1,
                       'DROP': 2,
                       'OTHER': 3}

        self.TASK = {
            'WAITING': 0,
            'FINISHED': 2,
            'FAILED': 3,
            'FLYING': 1
        }

        # self.RESULT = {'WAIT' : 0,
        #               'ARCHIEV' : 1,
        #               'FAIL' : 2
        #               }

        self.schedule_conf = None
        self.database_conf = None
        self.security_conf = None
        self.server_conf = None
        local_config = 'configuration_local\\scheduler_conf.json'
        default_config = 'configuration\\scheduler_conf.json'
        if os.path.exists(local_config):
            __conf_file__ = local_config
        else:
            __conf_file__ = default_config
        with open(__conf_file__) as f:
            json_data = json.load(f)
            self.schedule_conf = json_data['scheduleConf']
            self.database_conf = json_data['databaseConf']
            self.security_conf = json_data['securityConf']
            self.server_conf = json_data['serverConf']
        self.schedule_conf['dependPath'] = os.path.abspath(
            self.schedule_conf['dependPath'])
        print self.schedule_conf['dependPath']
        # Jenkins mode
        if len(sys.argv) > 1:
            if sys.argv[1] == 'jenkins':
                self.server_conf['port'] += 1
                # self.server_conf['host'] = socket.gethostbyaddr('localhost')[0]
                port = self.database_conf['dbmsHost'].split(
                    ':')[-1].replace('/', '')
                self.database_conf['dbmsHost'] = self.database_conf[
                    'dbmsHost'].replace(port, str(int(port) + 1))
                print 'Jenkins Mode'


conf = Conf()

retry = 5


class DBI():

    def __init__(self):
        self.db = None

    def get_db(self, string):
        global retry
        while retry > 0:
            try:
                self.db = self.db if self.db is not None else MongoClient(conf.database_conf['dbmsHost'])
                if self.db.alive():
                    retry = 5
                    return self.db['edris_scheduler']
                else:
                    raise Exception()
            except:
                import traceback
                traceback.print_exc()

                print 'DB not ready', string
                time.sleep(5)
                retry -= 1
        if retry == 0:
            conn = httplib.HTTPConnection(
                conf.server_conf['host'], conf.server_conf['port'])
            conn.request('GET', '/shutdown')
            data = conn.getresponse().read()
            print data
            conn.close()
            retry = -1

    @property
    def tasks(self):
        return self.get_db('tasks')['tasks']

    @property
    def workers(self):
        return self.get_db('workers')['workers']

    @property
    def task_results(self):
        return self.get_db('task_results')['results']

    @property
    def controllers(self):
        return self.get_db('controllers')['controllers']
