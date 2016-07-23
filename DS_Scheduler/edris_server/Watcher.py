#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime

import time
import logging
from edris_server.mq import message_queue

from edris_server import conf, dbm
MQ_SIZE = 1000


def monitor_worker():

    def on_worker_dropped(wid_s):
        message_queue.reschedule_by_wid(wid_s)

    dbm.WorkerManager.initialize()
    while(True):
        time.sleep(5)
        for w in dbm.db.workers.find({'status': conf.WORKER['READY']}):
            t1 = w['last_time']
            t2 = datetime.datetime.utcnow()
            t_delta = t2 - t1
            if t_delta.total_seconds() > conf.schedule_conf['workerTimeout']:
                logging.error('Worker Drop: ' + w['wid'] + ' worker dropped')
                on_worker_dropped(w['wid'])
