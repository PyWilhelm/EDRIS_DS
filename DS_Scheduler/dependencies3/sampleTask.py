#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, json, shutil, sys, datetime, logging, copy, traceback, numpy
import BaseTask
class sampleTask(BaseTask.BaseTask):

    def _prepare(self):
        self._default_result = {signal['signalName']: str(numpy.finfo(float).eps) for signal in self._parameters['testArguments']['results']}

    def _run(self):
        result, log = self.sample()
        return result, log
    

    def sample(self):
        log_dict = dict()
        log_dict['simulateErr'] = []
        log_dict['resultErr'] = []
        log_dict['filesystemErr'] = []
        start_time = datetime.datetime.utcnow()
        execute_time = start_time - start_time
        load_file_time = start_time - start_time
        final_result = {}
        for signal in self._parameters['testArguments']['results']:
            final_result[signal['signalName']] = '0'
        total_time = datetime.datetime.utcnow() - start_time
        log_dict['timeStatistic'] = [str(total_time), str(execute_time), str(load_file_time)]
        return final_result, log_dict

if __name__ == "__main__":
    sampleTask().run()
