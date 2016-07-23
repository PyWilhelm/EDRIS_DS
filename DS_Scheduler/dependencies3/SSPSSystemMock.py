#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Iterative calculation for maximal steady state power/torque until the energy storage system is empty
'''
import os, json, shutil, sys, datetime, logging, copy, traceback, numpy, math
import BaseTask
class SSPS(BaseTask.BaseTask):

    def _prepare(self):
        sys.path.append(os.path.abspath('EDRIS_wrapper.egg'))
        os.environ['DYMOLA_RUNTIME_LICENSE'] = os.path.join(os.getcwd(), 'dymola.lic')
        self._default_result = {signal['signalName']: str(numpy.finfo(float).eps) for signal in self._parameters['testArguments']['results']}

    def _run(self):
        result, log = self.ssps()
        return result, log
    

    def ssps(self):
        finish = False
        get_log_item = lambda tb, e: {'time': str(datetime.datetime.now()), 'type': str(type(e)), 'message': self._flatten(tb)}
        log_dict = dict()
        log_dict['simulateErr'] = []
        log_dict['resultErr'] = []
        log_dict['filesystemErr'] = []
        start_time = datetime.datetime.utcnow()
        execute_time = start_time - start_time
        load_file_time = start_time - start_time
        task = copy.deepcopy(self._parameters)

        final_result = self._default_result 
        temperature = float(task['testArguments']['parameters']['setTemp'])
        rci = float(task['testArguments']['parameters']['setRci'])
        speed = float(task['testArguments']['parameters']['setSpeed'])
        stop_time = float(task['testArguments']['simulationSettings']['StopTime'])
        
        for signal in task['testArguments']['results']:
            try:
                final_result[signal['signalName']] = str(get_value(temperature , rci , speed , stop_time))
            except Exception as e:
                log_dict['resultErr'].append(get_log_item(traceback.format_exc(), e))

        total_time = datetime.datetime.utcnow() - start_time
        log_dict['timeStatistic'] = [str(total_time), str(execute_time), str(load_file_time)]
        return final_result, log_dict

def get_value(temperature , rci , speed , stop_time):
        return  temperature*100  + rci*10 + speed*1000 + stop_time/10
        

if __name__ == "__main__":
    SSPS().run()
