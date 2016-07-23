#!/usr/bin/env python
# -*- coding: utf-8 -*-
from edris_server.conf import conf
import json
import datetime
import hashlib
import logging
from conf import DBI
from edris_server.IdGenerator import IdGenerator
import dlog


db = DBI()
logger = dlog.get_logger(__name__)

calculate_hashvalue = lambda d: hashlib.md5(json.dumps(d).encode('utf-8')).hexdigest()

'''class Controller(object):
    @staticmethod
    def initialize():
        db.controllers.remove()

    @staticmethod
    def add_controller():
        cid = IdGenerator()
        controller = {'cid': cid, 'last_time': datetime.datetime.utcnow()}
        db.controllers.insert(controller, safe=True)
        return cid
'''


class TaskManager(object):

    @staticmethod
    def initialize():
        results = db.tasks.find({'status': conf.TASK['FLYING']})
        for r in results:
            del r['started_time']
            r['status'] = conf.TASK['WAITING']
            db.tasks.update({'tid': r['tid']}, r, safe=True)

    @staticmethod
    # @dlog.log_with(logger)
    def insert_new_task(task, priority=1, no_cache=False, max_age=60 * 60 * 24):
        hashvalue = calculate_hashvalue(task)
        if not no_cache:
            results = db.tasks.find({'hashvalue': hashvalue}).sort([('created_time', -1)]).limit(1)
            for r in results:
                if datetime.datetime.utcnow() - r['created_time'] <= datetime.timedelta(seconds=max_age):
                    return r['tid']
        tid = IdGenerator()
        db.tasks.insert({'message': task,
                         'tid': tid,
                         'hashvalue': hashvalue,
                         'priority': priority,
                         'status': conf.TASK['WAITING'],
                         'created_time': datetime.datetime.utcnow()
                         }, safe=True)
        return tid

    @staticmethod
    # @dlog.log_with(logger)
    def load_to_waiting(tasks_json):
        for task in tasks_json['tests']:
            priority = task.get('priority', 1)
            TaskManager.insert_new_task(task, priority)

    @staticmethod
    # @dlog.log_with(logger)
    def load_to_finish(wid, tid):
        db.tasks.update({'tid': tid}, {'$set': {u'status': conf.TASK['FINISHED'],
                                                u'finish_time': datetime.datetime.utcnow(),
                                                u'wid': wid}}, safe=True)

    @staticmethod
    # @dlog.log_with(logger)
    def load_to_fail(tid, result, log_info, wid=None):
        logging.error('task %s: failed:\n result:\n %s log:\n%s' % (tid, result, log_info))
        db.tasks.update({'tid': tid},
                        {'$set': {'status': conf.TASK['FAILED'], 'finish_time': datetime.datetime.utcnow()}},
                        safe=True)
        TaskManager.save_result(wid, tid, result, log_info)

    @staticmethod
    # @dlog.log_with(logger)
    def load_to_flying(tid, wid):
        db.tasks.update({'tid': tid}, {'$set': {'started_time': datetime.datetime.utcnow(),
                                                'status': conf.TASK['FLYING'],
                                                'wid': wid}}, safe=True)

    @staticmethod
    # @dlog.log_with(logger)
    def load_waiting_tasks(amount=100):
        ls = []
        results = db.tasks.find({'status':
                                 conf.TASK['WAITING']}).sort([('priority', -1),
                                                              ('created_time', 1)]).limit(amount)
        [ls.append(r) for r in results]
        return ls

    @staticmethod
    # @dlog.log_with(logger)
    def reload_to_waiting(task_list):
        for t in task_list:
            db.tasks.update({'tid': t['tid']}, {'$set': {'status': conf.TASK['WAITING']}}, safe=True)

    @staticmethod
    # @dlog.log_with(logger)
    def save_result(wid, tid, result=None, log=None):  # , status=conf.RESULT['WAIT']):
        count = db.task_results.find({'tid': tid}).count()
        rid = IdGenerator()
        if count == 0:
            db.task_results.insert({'rid': rid,
                                    'tid': tid,
                                    'result': result,
                                    # 'status': status,
                                    'log': log,
                                    'wid': wid
                                    }, safe=True)
        else:
            logging.warning('%s war saved' % tid)
            db.task_results.insert({'rid': rid,
                                    'tid': tid,
                                    'result': result,
                                    # 'status': status,
                                    'log': log,
                                    'wid': wid,
                                    'duplicate': count + 1
                                    }, safe=True)

    @staticmethod
    # @dlog.log_with(logger)
    def get_result_bt_tid(tid):
        results = db.task_results.find({'tid': tid})
        for res in results:
            item = {'result': res['result'], 'log': res['log']}
            temp_res = db.tasks.find({'tid': tid})
            for t in temp_res:
                item['message'] = t['message']
            # db.tasks.update({'tid': tid}, {'$set': {'status': conf.TASK['ARCHIEV']}})
            return item
        return None

    @staticmethod
    # @dlog.log_with(logger)
    def check_status_by_tid(tid):
        tasks = db.tasks.find({'tid': tid})
        for t in tasks:
            return TaskManager.status2str(t['status'], 'T')

    @staticmethod
    def get_scheduler_info():
        r = db.tasks.find({'status': {'$in': [conf.TASK['WAITING'],
                                              conf.TASK['FLYING']]}})
        waiting, flying = 0, 0
        for t in r:
            if t['status'] == conf.TASK['WAITING']:
                waiting += 1
            else:
                flying += 1
        return waiting, flying

    @staticmethod
    def status2str(status, stype='T'):
        if stype == 'T':
            if status == conf.TASK['FAILED']:
                return 'FAILED'
            elif status == conf.TASK['FINISHED']:
                return 'FINISHED'
            elif status == conf.TASK['WAITING']:
                return 'PENDING'
            elif status == conf.TASK['FLYING']:
                return 'PROCESSING'
            # elif status == conf.TASK['ARCHIEV']:
            #    return 'ARCHIEV'

    # @staticmethod
    # @dlog.log_with(logger)
    # def set_result_achieve(_id_list_s):
    #    for rid in _id_list_s:
    #        db.task_results.update({'rid': rid}, {'$set': {'status': conf.RESULT['ARCHIEV']}}, safe=True)

    '''@staticmethod
    @dlog.log_with(logger)
    def get_all_tasks_info():
        all_finish = lambda ls:
        True if len([item for item in ls if item['status']!=conf.TASK['FINISHED']]) == 0 else False
        out_of_time = lambda ls: (datetime.datetime.utcnow() - \
                     max([item['finish_time'] for item in ls if item.get('finish_time') != None])).total_seconds() > \
                                    60 * 60 * 6
        results = db.tasks.find()
        rv = {}
        for r in results:
            if rv.get(r['cid']) == None:
                rv[r['cid']] = []
            rv[r['cid']].append({'status': r['status'], 'finish_time': r.get('finish_time')})
        rv_dict = {}
        for key in rv.keys():
            if all_finish(rv[key]) and out_of_time(rv[key]):
                continue
            rv_dict[key] = [0] * 4
            for item in rv[key]:
                rv_dict[key][item['status']] += 1
        return rv_dict
    '''
    @staticmethod
    # @dlog.log_with(logger)
    def get_all_worker_tempo():
        out_of_time = lambda ft: (datetime.datetime.utcnow() - ft).total_seconds() > 60 * 10
        start_time_f = lambda ls: (
            datetime.datetime.utcnow() - min([item['finish_time'] for item in ls])).total_seconds()
        results = db.tasks.find()
        results = [r for r in results if r.get('finish_time') != None and not out_of_time(r['finish_time'])]
        print results, len(results)
        if len(results) == 0:
            return {}
        print results
        w_results = [r for r in db.workers.find()]
        rv = {}
        name_id_dict = {}
        for item in results:
            w_name = [(w['clientname'], item['wid']) for w in w_results if w['wid'] == item['wid']]
            if len(w_name) > 0:
                name_id_dict[w_name[0][0]] = w_name[0][1]
                if rv.get(w_name[0][0]) == None:
                    rv[w_name[0][0]] = 1
                else:
                    rv[w_name[0][0]] += 1
        print json.dumps(rv, indent=2)
        print name_id_dict
        for key in rv.keys():
            start_time = start_time_f([i for i in results if i['wid'] == name_id_dict[key][1]])
            start_time = start_time if start_time < 60 * 10 else 600
            rv[key] = rv[key] / start_time * 60
            print start_time
        print json.dumps(rv, indent=2)
        return rv


class WorkerManager(object):

    @staticmethod
    def initialize():
        db.workers.remove()

    @staticmethod
    # @dlog.log_with(logger)
    def get_new_worker_id(thread_number, clientname):
        worker_id = IdGenerator()
        worker = {'wid': worker_id,
                  'create_time': datetime.datetime.utcnow(),
                  'last_time': datetime.datetime.utcnow(),
                  'status': conf.WORKER['READY'],
                  'thread': thread_number,
                  'clientname': clientname,
                  'tpm': 0}
        db.workers.insert(worker, safe=True)
        return worker_id

    @staticmethod
    def worker_update(wid, thread_number, clientname):
        results = db.workers.find({'wid': wid, 'status': conf.WORKER['READY']})
        if results.count() == 0:
            return WorkerManager.get_new_worker_id(thread_number, clientname)
        delta = datetime.datetime.utcnow() - results[0]['last_time']
        if delta.total_seconds() > conf.schedule_conf['workerTimeout']:
            db.workers.update({'wid': wid}, {'$set': {'last_time': datetime.datetime.utcnow(),
                                                      'thread': thread_number,
                                                      'create_time': datetime.datetime.utcnow(),
                                                      }}, safe=True)
        else:
            db.workers.update({'wid': wid}, {'$set': {'last_time': datetime.datetime.utcnow(),
                                                      'thread': thread_number}}, safe=True)
        return wid

    @staticmethod
    def worker_drop(wid):
        db.workers.update({'wid': wid}, {'$set': {'status': conf.WORKER['DROP']}})

    @staticmethod
    def find_wid(wid):
        results = db.workers.find({'wid': wid, 'status': conf.WORKER['READY']})
        return results.count() == 1

    @staticmethod
    def get_workers():
        r = db.workers.find()
        workers = []
        for w in r:
            workers.append((w['clientname'], w['thread'], w['status']))
        return workers
