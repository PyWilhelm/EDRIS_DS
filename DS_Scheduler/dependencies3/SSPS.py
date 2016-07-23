#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Iterative calculation for maximal steady state power/torque until the energy storage system is empty
'''
import os, json, shutil, sys, datetime, logging, copy, traceback, numpy
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
        import MyDyMat
        from dymola_wrapper.SimulatorGenerator import SimulatorGenerator
        from SimulatorTestModel import SimulatorTestDymola, SimulatorTest
        task = copy.deepcopy(self._parameters)
        mat_names_list = None
        mat_descr_list = None
        for parameter in task['functionArguments'].keys():
            max_value = float(task['functionArguments'][parameter]["maxValue"])
            min_value = float(task['functionArguments'][parameter]["minValue"])
            err_range = float(task['functionArguments'][parameter]["errorRange"])
            final_result = self.get_default_result()
            if max_value * min_value < 0:
                log_dict['simulateErr'].append('max_value and min_value cannot have different signs.')
                finish = True

            while max_value - min_value >= err_range and not finish:
                current_value = (max_value + min_value) / 2.0
                task['testArguments']['parameters'][parameter] = str(current_value)
                task['testArguments']['testName'] = task['testArguments']['modelName'].split('.')[-1] + 'test ' + parameter
                test = SimulatorTestDymola.SimulatorTestDymola(task['testArguments'])

                simulator_generator = SimulatorGenerator(test, build_directory=os.path.abspath('.'),
                                                        tsts_directory=os.path.abspath('.'),
                                                        sub_directory=(parameter + "=" + str(current_value)))

                    
                current_time1 = datetime.datetime.utcnow()
                result_path = None
                try:
                    result_path, sim_outputs = simulator_generator.simulate()
                    current_time2 = datetime.datetime.utcnow()
                    execute_time = execute_time + current_time2 - current_time1
    
                    current_time1 = datetime.datetime.utcnow()
                    
                    results = MyDyMat.DymolaMat(result_path, mat_names_list, mat_descr_list)
                    mat_names_list = results.names
                    mat_descr_list = results.descr
                    
                    current_time2 = datetime.datetime.utcnow()
                    load_file_time = load_file_time + current_time2 - current_time1

                    time_signal = results.data('time')
                    rci_signal = results.data('_signalBus_Main.batteryBus.controller.RCI')
                    derating_signal = results.data('summary.deratingStatus')

                    rci_end = rci_signal[-1]
                    rci_end_set = float(task['testArguments']['parameters']['RCIend_terminate'])
                    derating_end = derating_signal[-1] 
                    time_end = time_signal[-1]
                    stop_time_set = float(task['testArguments']['simulationSettings']['StopTime'])

                    if has_error(rci_end, rci_end_set, derating_end, time_end, stop_time_set):
                        finish = True
                        final_result = self._default_result 
                    elif time_too_short(time_end, stop_time_set):
                        current_point_problematic = True
                        final_result = self._default_result 
                        if current_value > 0:
                            min_value = current_value
                        else:
                            max_value = current_value      
                    elif too_high(rci_end, rci_end_set, derating_end):
                        if current_value < 0:
                            min_value = current_value
                        else:
                            max_value = current_value      
                    elif too_low(rci_end, rci_end_set):
                        for signal in test.results:
                            try:
                                final_result[signal['signalName']] = str(results.data(signal['signalName'])[-1])
                            except Exception as e:
                                log_dict['resultErr'].append(get_log_item(traceback.format_exc(), e))
                        if current_value > 0:
                            min_value = current_value
                        else:
                            max_value = current_value      

                    try:
                        shutil.rmtree(os.path.dirname(result_path))
                    except Exception as e:
                        log_dict['filesystemErr'].append(get_log_item(traceback.format_exc(), e))
                except Exception as e:
                    log_dict['simulateErr'].append(get_log_item(traceback.format_exc(), e))
                    finish = True

        total_time = datetime.datetime.utcnow() - start_time
        log_dict['timeStatistic'] = [str(total_time), str(execute_time), str(load_file_time)]
        return final_result, log_dict

def too_high(rci_end, rci_end_set, derating_end):
    derated = has_derating(derating_end)
    empty = rci_end <= rci_end_set
    if derated or (not empty):
        return True
    else:
        return False

def too_low(rci_end, rci_end_set):
    empty = rci_end <= rci_end_set
    if empty:
        return True
    else:
        return False

def is_empty(rci_end, rci_end_set):
    return rci_end <= rci_end_set * (1+0.001)
    
def has_derating(derating_end):
    if (derating_end > 0) and (derating_end != 3):
        return True
    else:
        return False

def time_too_short(time_end, stop_time_set):
    reached_end = time_end == stop_time_set 
    if reached_end: 
        return True
    else:
        return False

def has_error(rci_end, rci_end_set, derating_end, time_end, stop_time_set):
    reached_end = time_end == stop_time_set 
    derated = has_derating(derating_end)
    empty = rci_end <= rci_end_set
    if reached_end and derated and (not empty):
        return True
    else:
        return False
        

if __name__ == "__main__":
    SSPS().run()
