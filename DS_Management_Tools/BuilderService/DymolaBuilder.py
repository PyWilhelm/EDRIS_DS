from threading import Thread
import logging
import copy
import time
import os
import json
import shutil
import tempfile

from BuildingTools.BuildWrapper import ModelGenerator
from BuildingTools.ScriptGenerator import ModelSDS
from conf import __conf__
from trollius import From, Return
import trollius as aio


class BaseBuilder(object):
    _tasks = {}

    def add_task(self, key, task, no_cache=False):
        raise NotImplementedError('builder not implemented/loaded. Task failed with: ' + json.dumps(task))

    def _get_cache(self, key):
        return self._tasks.get(key)


class DummyDymolaBuilder(BaseBuilder):

    def add_task(self, key, task, no_cache=False):
        if not no_cache:
            task_cache = self._get_cache(key)
            if task_cache is not None:
                print('use_cache')
                return TaskGetter(task_cache)

        base_buildpath = __conf__['buildSetting']['path']
        source_file = os.path.join(os.path.dirname(__file__), 'dummy_sps.zip')

        relpath = task['name'].replace('.', os.path.sep)
        destination = os.path.join(base_buildpath, relpath)
        if not os.path.exists(destination):
            try:
                os.makedirs(base_buildpath)
            except Exception as err:
                print err
        print source_file, destination
        if not os.path.exists(destination):
            os.makedirs(destination)
        shutil.copy(source_file, destination)
        resulted_path = os.path.join(
            destination, os.path.basename(source_file))
        resulted_task = copy.deepcopy(task)
        resulted_task['log'] = ''
        resulted_task['result'] = resulted_path
        self._tasks[key] = resulted_task
        return TaskGetter(resulted_task)


@aio.coroutine
def dymola_builder(queue, dymola_instance):
    while True:
        task = yield From(queue.get())
        aio.async(check_dymola(dymola_instance))
        res = yield From(build_model(dymola_instance, task))
        task = res


@aio.coroutine
def check_dymola(dymola_instance):
    try:
        dymola_instance.cd()
    except Exception:
        try:
            dymola_instance.exit()
        except:
            pass
        dymola_instance = start_dymola()


@aio.coroutine
def build_model(dymola_instance, task):
    state = dict(finished=False)
    t = Thread(target=build_thread, args=(dymola_instance, task, state))
    t.start()

    while (not state['finished']):
        yield From(aio.sleep(0.1))
    raise Return(task)  # return task in asyncio for python3


def build_thread(dymola_instance, task, state):
    libraries = __conf__['libraryPath']
    modelica_path = __conf__['edrisComponentsPath']
    base_buildpath = __conf__['buildSetting']['path']

    temporary_directory = tempfile.mkdtemp(prefix='dymola_build_')
    model_generator = ModelGenerator(task, dymola_instance, temporary_directory,
                                     modelica_path, libraries)

    try:
        _, log = model_generator.build_model()
    except Exception as err:
        task['log'] = unicode(err)
        task['result'] = None
        raise Return(task)
    task['log'] = log
    source = model_generator.get_directory_path()
    destination = os.path.join(base_buildpath, model_generator.get_relpath())
    shutil.make_archive(destination, 'zip', source)
    print "base build path", temporary_directory
    task['result'] = destination + '.zip'
    state['finished'] = True


def main_event_loop(queue, loop, dymola_instances):
    aio.set_event_loop(loop)
    for d_instance in dymola_instances:
        aio.async(dymola_builder(queue, d_instance))
    loop.run_forever()


def start_dymola():
    from dymola.dymola_interface import DymolaInterface
    dymola_path = __conf__['buildSetting']['dymolaPath']
    return DymolaInterface(dymola_path)


class DymolaBuilder(object):

    def __init__(self, instances=4):
        logging.warn('init dymola builder')
        DymolaBuilder._initial_paths()
        self.dymola_instances = [start_dymola() for _ in range(instances)]
        self.loop = aio.get_event_loop()
        aio.set_event_loop(self.loop)
        self.queue = aio.Queue(maxsize=0, loop=self.loop)
        arguments = (self.queue, self.loop, self.dymola_instances)
        self.main = Thread(target=main_event_loop, args=arguments)
        self.main.start()
        logging.warn('started thread loop asyncio')

    @staticmethod
    def _initial_paths():
        base_buildpath = __conf__['buildSetting']['path']
        try:
            shutil.rmtree(base_buildpath)
        except Exception as err:
            print err
        if not os.path.exists(base_buildpath):
            try:
                os.makedirs(base_buildpath)
            except Exception as err:
                print err

    def add_task(self, key, task, no_cache=False):
        if not no_cache:
            task_cache = self._get_cache(key)
            if task_cache is not None:
                return TaskGetter(task_cache)
        self._tasks[key] = task
        aio.set_event_loop(self.loop)
        self.loop.call_soon_threadsafe(aio.async, self.queue.put(task))

        return TaskGetter(task)

    def stop(self):
        for instance in self.dymola_instances:
            instance.exit()
        self.loop.stop()
        self.loop.close()
        self.main.join()


class TaskGetter(object):

    def __init__(self, task):
        self.task = task

    def get(self):
        if self.task.get('result') is not None:
            return self.task
        else:
            return None


def get_build_task(task):
    building_info = copy.deepcopy(task.get('buildingInfo', {}))
    modelname = task['parameterOfFunction']['testArguments']['modelName']
    return get_building_info(modelname, building_info)


def get_building_info(modelname, building_info):
    modelsds = ModelSDS(building_info)
    print modelname, building_info
    script = modelsds.generate_model_script()
    print script
    build_task = {'name': modelname, 'value': script}
    return build_task
