#!/usr/bin/env python
# -*- coding: utf-8 -*-

from multiprocessing import Lock
import threading
import time
import datetime
import logging
from edris_server import dbm
from edris_server.conf import conf
import dlog
import functools
import json
import md5


sync_lock = Lock()

# FIXME: MAX_NUMBER_PROCESSING
MAX_PROCESSING_TIMEOUT = conf.schedule_conf['taskTimeout']
MAX_PROCESSING_AMOUNT = conf.schedule_conf['maxWaitingTask']
MAX_LOAD_AMOUNT = conf.schedule_conf['maxWaitingTask']

logger = dlog.get_logger(__name__)


def threaded_safe(function):
    @functools.wraps(function)
    def wrapper(*args, **kw):
        sync_lock.acquire()
        try:
            result = function(*args, **kw)
        except Expection as err:
            raise err
        finally:
            sync_lock.release()
        return result
    return wrapper


class MessageQueue(object):
    # @dlog.log_with(logger)

    def __init__(self, retry=2):
        self.__waiting = []
        self.__processing = dict()
        self.retry = retry
        self.monitor_thread = threading.Thread(target=self.monitor_tasks, name='monitor_thread')
        self.monitor_thread.daemon = True

    # @dlog.log_with(logger)
    def start(self):
        dbm.TaskManager.initialize()
        self.monitor_thread.start()

    # @dlog.log_with(logger)
    @threaded_safe
    def load_tasks(self):
        ls = dbm.TaskManager.load_waiting_tasks(MAX_LOAD_AMOUNT - len(self.__waiting))
        self.__waiting.extend(ls)

    # @dlog.log_with(logger)
    @threaded_safe
    def clearup_waiting_tasks(self, priority):
        low_priority = [t for t in self.__waiting if t['priority'] < priority]
        dbm.TaskManager.reload_to_waiting(low_priority)
        self.__waiting = [t for t in self.__waiting if t['priority'] >= priority]

    # @dlog.log_with(logger)
    def monitor_tasks(self):
        while True:
            now = datetime.datetime.utcnow()
            for tid in self.__processing.keys():
                task = self.__processing[tid]
                start = task['start']
                timedelta = now - start
                if timedelta.total_seconds() > MAX_PROCESSING_TIMEOUT:
                    '''LOGGING RETRY'''
                    self.reschedule_by_tid(tid, {}, {'id': tid, 'log': {'message': 'timeout', 'type': 'timeout'}})
            time.sleep(10)

    # @dlog.log_with(logger)
    def get_task(self, wid_s):
        if dbm.WorkerManager.find_wid(wid_s) == False:
            raise Exception('the worker not registered')

        if len(self.__waiting) == 0:
            self.load_tasks()
            if len(self.__waiting) == 0:
                raise Exception('No more waiting tasks')
        if len(self.__processing) > MAX_PROCESSING_AMOUNT:
            raise Exception('Cannot run more tasks')
        task = self.__waiting.pop(0)
        # FIXME: refactor the state indicator
        task['status'] += 1         # status in [FLYING, FLYING+RETRY]
        task['wid'] = wid_s
        task['start'] = datetime.datetime.utcnow()
        self.__processing[task['tid']] = task
        dbm.TaskManager.load_to_flying(task['tid'], wid_s)
        return task

    # @dlog.log_with(logger)
    @threaded_safe
    def reschedule_by_wid(self, wid_s):
        dbm.WorkerManager.worker_drop(wid_s)
        for tid in self.__processing.keys():
            task = self.__processing[tid]
            if task['wid'] == wid_s:
                del self.__processing[tid]
                del task['wid']
                self.__waiting.insert(0, task)

    # @dlog.log_with(logger)
    @threaded_safe
    def reschedule_by_tid(self, tid_s, result, log, wid=None):
        try:
            task = self.__processing[tid_s]
            if task['status'] < conf.TASK['FLYING'] + self.retry:
                logging.warning('***set status to RETRY*** %s' % (tid_s))
                self.__waiting.append(task)
            else:
                logging.warning('***set status to Fail*** %s' % (tid_s))
                dbm.TaskManager.load_to_fail(tid_s, result, log, wid=wid)
            del self.__processing[tid_s]
        except:
            import traceback
            logging.error('Reschedule ERROR: ' + traceback.format_exc())

    # @dlog.log_with(logger)
    def fail_by_tid(self, wid, tid_s, result, fail_code):
        self.reschedule_by_tid(tid_s, result, fail_code, wid=wid)

    # @dlog.log_with(logger)
    @threaded_safe
    def acknowledge(self, wid_s, tid_s, data, log):
        dbm.TaskManager.save_result(wid_s, tid_s, data, log)
        dbm.TaskManager.load_to_finish(wid_s, tid_s)
        if tid_s in self.__processing.keys():
            del self.__processing[tid_s]


message_queue = MessageQueue()
