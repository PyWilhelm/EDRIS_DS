'''
Created on 04.08.2014

@author: q350609

'''
import threading
import time

import json
import types
import pykka
import os
import functools

from multiprocessing import Lock

from conf import __conf__, db
from TaskController.BaseClass.BaseResultSaver import BaseResultSaver
from TaskController.BaseClass.MetataskInterpreter import MetataskInterpreter
import dlog
from __builtin__ import True
from copy import deepcopy
from TaskController.BaseClass.network import Request

logger = dlog.get_logger(__name__)

TIMEOUT = 30
sync_lock = Lock()


def threaded_safe(function):
    @functools.wraps(function)
    def wrapper(*args, **kw):
        sync_lock.acquire()
        try:
            result = function(*args, **kw)
        except Exception as err:
            raise err
        finally:
            sync_lock.release()
        return result
    return wrapper


'''
    @summary:
    #### Controller <-> Scheduler 
        - communication via RESTful AIP
        - push tasks and get query locations
        - check tasks status and get locations of results
        - poll results from scheduler
        - retry features
    #### Controller <-> User
        - add metatask and return a result getter
        - a controller can contain more than one metatask
        - check progress of tasks of the controller
        - force stop the controller
    #### Controller <-> MetataskExecute
        - every MetataskExecute only for exactly one metatask
        - Controller sends metatask to ME, ME expend metatask to list of tasks and then ME invokes
            Controller's API - _push_tasks
        - Once controller get a result, the result is sent to ME, so that the ME determines the
            result marked as successful or failed, and whether the task retry or not.
    #### MetataskExecuter <-> ResultGetter
        - ResultGetter checks the status of ME.
            If the status is "not finished", the RG is blocked and continues the checking loop.
            if the status is "finished", ME generates a reporter instance and sends it to RG.
    #### ResultGetter <-> User
        - method **get()**: if timeout=0, blocking mode; if timeout>0, return None if timeout.
        - Once ME is finished, RG returns the reporter instance to user.
'''


class Controller(object):

    class Task(object):
        '''Task Class, consists of
           @param task (payload, dict object),
           @param actor_ref (executor),
           @param location (url for querying status returned by scheduler),
           @param retry (true if the task is executed secondly),
           @param result_location (url for querying result returned by scheduler)
        '''

        def __init__(self, task, actor_ref, retry=False):
            self.task = task
            self.actor_ref = actor_ref
            self.location = None
            self.retry = retry
            self.result_location = None

    # @dlog.log_with(logger)
    def __init__(self, priority=1, auto=False, no_cache=False, max_age=60 * 60 * 24):
        '''create controller instance
            @param priority: the priority of controller, 
                                the tasks from the controller of higher priority are executed faster.
            @param auto: @deprecated
            @param no_cache: True if no-cache is set, default False
            @param max_age: avaliable if no_cache=False, the max lifetime of cache, default 24 hours

        '''
        self.results = []
        self.task_list = []
        self.actors = []
        self.finish = False
        self.result_saver_class = BaseResultSaver
        self.thread_check_result = None
        self.auto = auto
        self.priority = priority
        self._task_not_sent = []
        self.no_cache = no_cache
        self.max_age = max_age
        self.result_getters = []
        self.errors = []

    @property
    def finish(self):
        return self.__finish

    @finish.setter
    def finish(self, finish):
        import inspect
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)
        self.__finish = finish

    def __del__(self):
        print 'the whole controller exits'

    def active_actors(self):
        return [actor for actor in self.actors if actor.actor_stopped.is_set() != True]

    def add_metatask(self, path_or_dict):
        '''user interface 
            add a new metatask into controller
            @workflow:
                1. start a thread to check results in regular time
                2. interprete the metatask and lookup and get the required classes (task generator and reporter)
                3. create metatask executor
                4. create result getter.
        '''
        if self.thread_check_result is None:
            self.thread_check_result = threading.Thread(target=self.__check_results,
                                                        name='__check_results')
            self.thread_check_result.daemon = True
            self.thread_check_result.start()

        if not isinstance(path_or_dict, types.DictType):
            with open(path_or_dict) as f:
                path_or_dict = json.load(f)
        mt = MetataskInterpreter(path_or_dict).get()
        print mt.reporter
        actor_ref = MetataskExecute.start(metatask_structure=mt,
                                          controller=self)
        self.actors.append(actor_ref)  # [total task number, sucessful, failed]
        actor_ref.tell({'build': actor_ref})
        result_getter = GetResults(actor_ref)
        self.result_getters.append(result_getter)
        return result_getter

    def set_error(self, error):
        self.errors.append(error)

    def get_status(self):
        status_list = []
        error_list = []
        finish = True
        for result_getter in self.result_getters:
            _finish, status, error = result_getter.get_status()
            status_list.append(status)
            finish = _finish if _finish is False else finish
            if error is not None:
                error_list.append(error)
        if self.errors != []:
            error_list = self.errors + error_list

        return finish, status_list, error_list

    def check_progress(self, controller_finish=False):
        '''check progress of whole controller
            @param controller_finish (boolean): true: check the whole controller finished or not
                                                false: check the actual metatasks finished or not
            @return:
            if controller_finish is True: tuple(controller finished, current status)
            else: tuple(metatasks finished, current status, error log)
        '''
        finish, status, error = self.get_status()
        if len(self.actors) == 0:
            finish = False
        if controller_finish:
            return self.finish, status
        if not controller_finish:
            return finish, status, error

    def stop(self, all_stop=False):
        '''force stop controller
        '''
        self.finish = True
        with open(os.path.join(__conf__['outputPath'],
                               'tmp_result', 'result%s.txt' % int(time.time())), 'a') as f:
            f.write(']\n')

    @threaded_safe
    def _push_task(self, new_task, actor_ref, retry=False):
        '''push tasks to scheduler and get locations from scheduler
            called by MetataskExecute
        '''
        self._task_not_sent.append(Controller.Task(new_task, actor_ref, retry=retry))
        if len(self._task_not_sent) >= 100:
            self._flush_tasks()

    @threaded_safe
    def _flush_tasks_safe(self, retry=False):
        return self._flush_tasks(retry=retry)

    def _flush_tasks(self, retry=False):
        while True:
            try:
                req = Request('PUT', '/tasks',
                              headers={'priority': str(self.priority),
                                       'no-cache': str(self.no_cache if not retry else retry),
                                       'max-age': str(self.max_age)},
                              body=json.dumps([t.task for t in self._task_not_sent]))
                response = req.getresponse()
                data = json.loads(response.body)['locations']
                if len(data) != len(self._task_not_sent):
                    # TOOD: Error Handling
                    print 'we have lost some tasks!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
                    raise Exception('Problem the task sent are not all accepted!!')
                for i, t in enumerate(self._task_not_sent):
                    t.location = data[i]
                    t.task['location'] = t.location
                    db.tasks.update({'location': t.location}, t.task, upsert=True, safe=True)
                    t.task = None
                    self.task_list.append(t)
                self._task_not_sent = []
                break
            except:
                import traceback
                traceback.print_exc()

    def _actor_tasks_locations(self, actor_ref):
        return [task.location for task in self.task_list if task.actor_ref == actor_ref]

    # @dlog.log_with(logger)
    @threaded_safe
    def _on_build_error(self, new_task, actor_ref, error_msg):
        '''called by MetataskExecute, once building error occurs, save error log into database.
        '''
        new_task.update(
            {'location': None, 'result': json.dumps({}), 'log': error_msg, 'status': 1})
        db.tasks.insert(new_task, safe=True)

    @staticmethod
    def has_location(location, task_list):
        matching_entry = [task for task in task_list if task.location == location]
        return True if len(matching_entry) > 0 else False

    @dlog.log_with(logger)
    def __check_results(self):
        while not self.finish:
            try:
                if len(self.task_list) == 0:
                    time.sleep(5)
                    continue
                locations = []
                for actor in self.active_actors():  # list of locations of pending tasks
                    locations.extend(actor.ask({'pendingtask': True}))
                if len(locations) == 0:
                    continue
                req = Request('POST', '/tasks', body=json.dumps(locations))
                response = req.getresponse()
                result_dict = json.loads(response.body)  # locations of result
                print('[CHECK RESULTS]', len(result_dict))
                loss_task_list = [
                    location for location in locations if location not in result_dict.keys()]
                if len(loss_task_list) > 0:
                    print 'not good, the following are lost'
                    print(json.dumps(loss_task_list, indent=2))
                    '''
                        TODO: send the tasks again
                    '''
                self.__get_results(result_dict)
                time.sleep(2)
            except:
                print 'waiting for Scheduler'
                import traceback
                print traceback.format_exc()
                time.sleep(TIMEOUT)

    def __check_finish(self, rd):
        return len([t for t in self.task_list
                    if rd.get(t.location, {}).get('status') not in ['ARCHIEV']]) == 0

    # @dlog.log_with(logger)
    def __get_results(self, task_dict):
        locs = [loc for loc in task_dict.keys()
                if task_dict[loc]['status'] in ['FINISHED', 'FAILED']]
        for loc in locs:
            task = [t for t in self.task_list if t.location == loc][0]
            task.result_location = task_dict[loc]['location']
        if len(locs) == 0:
            return
        req = Request('POST', '/results',
                      body=json.dumps([task_dict[loc]['location'] for loc in locs]))
        response = req.getresponse()
        result_dict = json.loads(response.body)
        for loc in result_dict.keys():
            self.__achieve(loc, result_dict[loc])

    # @dlog.log_with(logger)
    def __achieve(self, task_loc, r):
        try:
            r['result'] = json.loads(r['result'])
        except:
            import traceback
            print traceback.format_exc()
            print 'problematic json is'
            print r['result']
        error = self.__detect_error(r)
        matching_tasks = [task for task in self.task_list if task.result_location == task_loc]
        if len(matching_tasks) == 0:
            print 'no matching tasks found!!!!!!!!!!!!!!!!!'
            return
        for task in matching_tasks:
            if not error:
                task.actor_ref.tell({'successful': {'result': r, 'location': task.location}})
            else:
                task.actor_ref.tell({'failed': {'result': r, 'location': task.location}})

    def __detect_error(self, result):
        if len(result['result'].keys()) == 0:
            return True
        try:
            log = json.loads(result['log'])
            if len(log.get('simulateErr', [])) > 0 or len(log.get('resultErr', [])) > 0\
                    or len(log.get('filesystemErr', [])) > 0:
                return True
        except:
            return True
        return False

    def _retry_task(self, location):
        task = None
        for t in self.task_list:
            if t.location == location:
                task = t
        if task is None or task.retry:
            return None
        self.task_list.remove(task)
        task_content = [r for r in db.tasks.find({'location': location})][0]
        try:
            del task_content['location']
            del task_content['_id']
        except:
            pass
        self._push_task(task_content, task.actor_ref, True)
        self._flush_tasks_safe(retry=True)
        locations = self._actor_tasks_locations(task.actor_ref)
        return locations[-1]


class MetataskExecute(pykka.ThreadingActor):

    def __init__(self, metatask_structure, controller):
        super(MetataskExecute, self).__init__()
        self.metatask = metatask_structure.metatask_data
        self.task_generator = metatask_structure.task_generator
        self.reporter = metatask_structure.reporter
        self.input_data = []
        self.output_data = {'successful': [], 'failed': []}
        self.building_failed_tasks = []
        self.building_error = None
        self.build_finish = False
        self.report = None
        self.controller = controller
        self.finish = False

    def __get_new_tasks_by_metatask(self, ref):
        try:
            task_iter = self.task_generator.generate()
            for task in task_iter:
                if task.get('error') is not None:
                    self.building_failed_tasks.append(task['task'])
                    self.building_error = task['error']
                    self.controller._on_build_error(task, ref, task['error'])
                    continue
                self.controller._push_task(task, ref)
            self.controller._flush_tasks_safe()
            task_locations = self.controller._actor_tasks_locations(ref)
            self.input_data.extend(task_locations)
        except Exception:
            import traceback
            print traceback.format_exc()
            self.controller._on_build_error(task, ref, traceback.format_exc())
        finally:
            self.build_finish = True

    def __get_waiting_tasks(self):
        finish_locs = deepcopy(self.output_data['successful'])
        finish_locs.extend(self.output_data['failed'])
        rv = [t for t in self.input_data if t not in finish_locs]
        return rv

    def __retry(self, location):
        new_loc = self.controller._retry_task(location)
        if new_loc is not None:
            index = self.input_data.index(location)
            self.input_data[index] = new_loc
            return True
        return False

    def __achiev(self, loc, result, status):
        db.tasks.update({'location': loc},
                        {'$set': {'result':
                                  json.dumps(result['result']),
                                  'log': result['log'],
                                  'status': status}}, safe=True)

    # @dlog.log_with(logger)
    def __load_results(self, loc_list):
        results = db.tasks.find({'location': {'$in': loc_list}})
        successful = []
        failed = []
        for r in results:
            temp = {'message': {key: r[key] for key in r.keys()
                                if key not in['result', 'log', 'status', 'location']},
                    'result': json.loads(r['result']),
                    'status': r['status'],
                    'log': r.get('log')
                    }
            if temp['status'] == 0:
                successful.append(temp)
            else:
                failed.append(temp)
        failed.extend([{'message': task, 'status': 1, 'log': 'building error'}
                       for task in self.building_failed_tasks])
        return successful, failed

    # @dlog.log_with(logger)
    def on_receive(self, message):
        get_number_of_finish = lambda: len(self.output_data['successful'])\
            + len(self.output_data['failed'])
        if message.get('build') is not None:
            t = threading.Thread(target=self.__get_new_tasks_by_metatask,
                                 args=(message.get('build'),))
            t.daemon = True
            t.start()
        if message.get('retry') is not None:
            waiting_tasks = self.__get_waiting_tasks()
            for task in waiting_tasks:
                self.controller._push_task(task, message.get('retry'))
        if message.get('successful') is not None:
            location = message['successful']['location']
            self.output_data['successful'].append(location)
            self.__achiev(location, message['successful']['result'], status=0)
            return
        elif message.get('failed') is not None:
            location = message['failed']['location']
            retry = self.__retry(location)
            if not retry:
                self.output_data['failed'].append(location)
                self.__achiev(location, message['failed']['result'], status=1)
            return
        elif message.get('pendingtask') is not None:
            return self.__get_waiting_tasks()
        elif message.get('progress') is not None:
            r = [len(self.input_data),
                 len(self.output_data['successful']),
                 len(self.output_data['failed'])]
            if self.build_finish and r[0] == r[1] + r[2] and self.building_error is None:
                return True, r, None
            else:
                return False, r, self.building_error
        elif message.get('check') is not None:
            return get_number_of_finish() == len(self.input_data) if self.build_finish else False
        elif message.get('get') is not None:
            successful, failed = self.__load_results(self.input_data)
            print 'report:----------------------START'
            self.report = self.reporter.set_sim_results(self.metatask,
                                                        # TODO: remove cid from reporter
                                                        int(time.time()),
                                                        successful,
                                                        failed,
                                                        message['get'][2]).set_prev_result(\
                message['get'][0]).report(message['get'][1])
            print 'report:----------------------FINISH\nreport: ', self.report
            return self.report


class GetResults(object):
    # @dlog.log_with(logger)

    def __init__(self, actor_ref):
        self.actor_ref = actor_ref
        self.result = None
        self.status = dict(finished=False, status=[], error=[])

    def _update_status(self):
        s = self.status
        s['finished'], s['status'], s['error'] = self.actor_ref.ask({'progress': True})

    def get_status(self):
        if self.actor_ref.actor_stopped.is_set() != True:
            self._update_status()
        s = self.status
        return s['finished'], s['status'], s['error']

    def get(self, prev_result=None, method='', timeout=0, retry_timeout=0, sdf=True):
        '''get result
            @param prev_result: previous result, used to merge
            @param method: Reporter parameter
            @param timeout: timeout (sec.) to block this method, 0: always blocking
            @param retry_timeout: timer to retry, if < 1, set to 1 sec. (i.e. min value is 1)

        '''
        now = time.time()
        if self.result is None:
            if timeout == 0:
                while not self.actor_ref.ask({'check': ''}):
                    time.sleep(1)
                    delta = time.time() - now
                    if retry_timeout > 0 and delta > retry_timeout:
                        self.actor_ref.tell({'retry': self.actor_ref})
            else:
                while not self.actor_ref.ask({'check': ''}):
                    delta = time.time() - now
                    if retry_timeout > 0 and delta > retry_timeout:
                        self.actor_ref.tell({'retry': True})
                    time.sleep(1 if timeout >= 1 else timeout)
                    timeout -= 1
                    if timeout < 0:
                        return None
            self.result = self.actor_ref.ask({'get': [prev_result, method, sdf]})
        if self.actor_ref.actor_stopped.is_set() != True:
            self._update_status()
            self.actor_ref.stop()
        return self.result
