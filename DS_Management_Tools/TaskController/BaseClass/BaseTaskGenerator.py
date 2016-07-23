#!/usr/bin/env python
# -*- coding: utf-8 -*-
import copy
import json
import logging
import math
import os
import time
import types
import zipfile
import tempfile

from TaskController.BaseClass.network import Request


class Model():
    '''Model Class, consists of
       @param model (payload, dict object),
       @param tasks (list of tasks),
       @param location (url for querying status returned by BuilderService),
       @param finish (true if the model is already built),
       @param id
    '''

    def __init__(self, model, task):
        self.model = model
        self.tasks = [task]
        self.location = None
        self.finish = None
        self.id = None

    def add_task(self, task):
        self.tasks.append(task)

    def remove_task(self, task):
        if self.tasks.index(task) >= 0:
            self.tasks.remove(task)
            return True
        return False


class BuilderType():
    Dymola = 'dymola'   # dymola mode
    Dummy = 'dummy'     # dummy mode, for testing
    NoBuilder = None    # no builder


class BaseTaskGenerator(object):
    '''
        baseclass for task generator: generate list of tasks based on metatask
        interface:
            __init__(data, builder_class): initialize TG
                data: metatask:
                builder_class: ModelBuilder Class, e.g. DymolaModelBuilder
            generate(): return an iterator.

        rewritten in subclass:
            generate_simple(): return the list of tasks

    '''

    def __init__(self, data, builder_class):
        self.data = data
        self.builder = None
        if builder_class is not None:
            self.builder = builder_class
        self.models = []

    def _check_models_finished(self):
        for m in self.models:
            if m.finish is None:
                return False
        return True

    def generate(self, depend_results=None):
        '''
            @return: iterator of list of tasks once model is built successfully
        '''
        tasks = []
        if depend_results is None:
            tasks = self.generate_simple()
        else:
            tasks = self.generate_optimal(depend_results)
        if self.builder is not None:
            self.build_model(tasks)
        else:
            for task in tasks:
                yield task
            return

        while not self._check_models_finished():
            for model in self.models:
                if model.finish:
                    continue
                finished, zip_filename, log = self._check_model_finished(model)
                if not finished:
                    time.sleep(1)
                    continue
                if zip_filename is None:
                    for task in model.tasks:
                        yield {'error': log, 'task': task}
                    continue
                dependencies = self._unzip_and_remove(zip_filename)
                rename = self._rename_by_mid(dependencies, model.id,
                                             'cache')
                self._upload_files_and_remove(dependencies, rename)
                model.finish = True

                for task in model.tasks:
                    task['dependency'].extend(rename)
                    yield task

    def _rename_by_mid(self, depend, mid, base):
        rename = []
        for d in depend:
            filename = os.path.relpath(d, base)
            filename = mid + filename[filename.find(os.sep):]
            rename.append(filename)
        return rename

    def _check_model_finished(self, model):
        '''check building status; if finished, download achieve file
            @return:
            finished (boolean)
            filename (string)
            building log (stringß)
        '''
        req = Request('GET', model.location, server='builder')
        resp = req.getresponse()
        if resp.status == 203 or resp.status == 404:
            return False, None, None,
        resp_content = json.loads(resp.body)
        if resp_content['result'] is None or '':
            model.finish = True
            return True, None, resp_content['log']
        url = resp_content['result']
        req_download = Request('GET', url, server='builder')
        resp_download = req_download.getresponse()
        if not os.path.exists('cache'):
            os.mkdir('cache')
        fhandle, filename_temp = tempfile.mkstemp(prefix='model_', suffix='',
                                                  dir='cache')
        os.close(fhandle)
        filename = filename_temp + '_file.zip'
        with open(filename, 'wb') as f:
            f.write(resp_download.body)
        while True:
            with open(filename, 'rb') as f:
                data = f.read()
            if len(data) == len(resp_download.body):
                break
        return True, filename, resp_content['log']

    def _unzip_and_remove(self, filename):
        '''unzip the achieve file and remove it
            @return: list of filenames extracted from in the achieve file
        '''
        source_zip = filename
        target_dir, _ = os.path.splitext(filename)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        myzip = zipfile.ZipFile(source_zip)
        myfilelist = myzip.namelist()
        print myfilelist
        for name in myfilelist:
            f_handle = open(os.path.join(target_dir, name), "wb")
            f_handle.write(myzip.read(name))
            f_handle.close()
        myzip.close()
        os.remove(filename)
        return [os.path.join(target_dir, f) for f in myfilelist]

    def _upload_files_and_remove(self, files, rename):
        '''push executable files to scheduler and remove them from cache

        '''
        data = []
        for f, r in zip(files, rename):
            with open(f, 'rb') as fh:
                data = fh.read().encode('base64')
            print f, r
            req = Request('POST', '/upload/' + r, body=data, compress=False)
            req.getresponse()
            # os.remove(f)
        # os.rmdir(os.path.dirname(f))

    def build_model(self, tasks):
        '''push model information to BuilderService
            @param tasks: list of tasks, from which model information exists.
        '''
        self.get_models(tasks)
        add_task_url = '/{0}/models'.format(self.builder)
        req = Request('POST', add_task_url, body=json.dumps([m.model for m in self.models]),
                      server='builder', compress=False)
        print req.getresponse().body
        post_task_response = json.loads(req.getresponse().body)
        for i, resp in enumerate(post_task_response):
            self.models[i].location = resp['location']
            self.models[i].id = resp['id']

    def get_models(self, tasks):
        '''get model information from list of tasks'''
        for t in tasks:
            building_info = copy.deepcopy(t.get('buildingInfo', {}))
            modelname = t['parameterOfFunction']['testArguments']['modelName']
            for m in self.models:
                if m.model['name'] == modelname and m.model['value'] == building_info:
                    m.add_task(t)
                    break
            else:
                self.models.append(Model({'name': modelname, 'value': building_info}, t))

    def check_build_finish(self, task):
        return self.builder.check_build_finish(task)

    def callback_finish_building(self):
        pass

    def generate_simple(self):
        raise NotImplementedError()

    def generate_optimal(self, depend_results):
        raise NotImplementedError()

    def _flatten_variable(self, set_set=True, sort=True):
        def seq(start, stop, step=1):
            n = int(math.ceil(round((stop - start) / float(step))))
            if n >= 1:
                return [start + step * i for i in range(n)]
            else:
                return []

        def compare(a, b):
            a = float(a)
            b = float(b)
            if a > b:
                return 1
            elif a == b:
                return 0
            else:
                return -1
        task_generator = self.data['taskGenerator']
        variable = task_generator['arguments'].get('variable', [])
        for item in variable:
            if isinstance(item['value'], types.UnicodeType) == True \
                    or isinstance(item['value'], types.StringType) == True:
                values = item['value']
                values = values.split(' ')
                values = [v for v in values if len(v) > 0]
                ls1 = []
                for v in values:
                    ls = v.split(':')
                    if len(ls) < 3:
                        ls1.append(v)
                    if len(ls) == 3:
                        ls1.extend(
                            [str(i) for i in seq(float(ls[0]), float(ls[2]), float(ls[1]))])
                        ls1.append(ls[2])
                temp_list = list(set(ls1))
                if len(temp_list) < len(ls1):
                    logging.warning('duplicate values exist!')
                if set_set:
                    item['value'] = temp_list
                if sort:
                    item['value'].sort(compare)
