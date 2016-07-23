#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import logging
import shutil
from edris_server.conf import conf
from pymongo import MongoClient


def clearup():
    while True:
        try:
            db = MongoClient(conf.database_conf['dbmsHost'])['edris_scheduler']
            tasks = db['tasks']
            workers = db['workers']
            task_results = db['results']
            # controllers = db['controller']
            break
        except:
            logging.error('Mongodb starts failed')
    tasks.remove()
    workers.remove()
    task_results.remove()
    [shutil.rmtree(os.path.join(conf.schedule_conf['dependPath'], path))
     for path in os.listdir(conf.schedule_conf['dependPath'])
     if os.path.isdir(os.path.join(conf.schedule_conf['dependPath'], path))]
