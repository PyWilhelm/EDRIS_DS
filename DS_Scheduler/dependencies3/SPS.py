#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, json, shutil, sys, datetime, logging, copy, traceback, numpy
import BaseTask
class SPS(BaseTask.BaseTask):

    def _prepare(self):
        sys.path.append(os.path.abspath('EDRIS_wrapper.egg'))
        os.environ['DYMOLA_RUNTIME_LICENSE'] = os.path.join(os.getcwd(), 'dymola.lic')
        self._default_result = {signal['signalName']: str(numpy.finfo(float).eps) 
                                for signal in self._parameters['testArguments']['results']}

    def _run(self):
        result, log = self.sps()
        return result, log
    

    def sps(self):
        finish = False
        get_log_item = lambda tb, e: {'time': str(datetime.datetime.now()), 'type': str(type(e)), 'message': self._flatten(tb)}
        log_dict = dict()
        log_dict['simulateErr'] = []
        log_dict['resultErr'] = []
        log_dict['filesystemErr'] = []
        start_time = datetime.datetime.utcnow()
        execute_time = start_time - start_time
        load_file_time = start_time - start_time
        remove_file_time = start_time - start_time
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

                    
                current_time3 = datetime.datetime.utcnow()
                result_path = None
                try:
                    result_path, sim_outputs = simulator_generator.simulate()
                    current_time1 = datetime.datetime.utcnow()
                    execute_time = execute_time + current_time1 - current_time3
                    
                    results = MyDyMat.DymolaMat(result_path, mat_names_list, mat_descr_list)
                    mat_names_list = results.names
                    mat_descr_list = results.descr
                    result_signal = results.data('time')
                    
                    current_time2 = datetime.datetime.utcnow()
                    load_file_time = load_file_time + current_time2 - current_time1
                    if result_signal[-1] == float(task['testArguments']['simulationSettings']['StopTime']):
                        for signal in test.results:
                            try:
                                final_result[signal['signalName']] = str(results.data(signal['signalName'])[-1])
                            except Exception as e:
                                log_dict['resultErr'].append(get_log_item(traceback.format_exc(), e))
                        if current_value > 0:
                            min_value = current_value
                        else:
                            max_value = current_value      
                    else:
                        if current_value > 0:
                            max_value = current_value
                        else:
                            min_value = current_value      
                    try:
                        shutil.rmtree(os.path.dirname(result_path))
                    except Exception as e:
                        log_dict['filesystemErr'].append(get_log_item(traceback.format_exc(), e))
                    current_time3 = datetime.datetime.utcnow()
                    remove_file_time = remove_file_time + current_time3 - current_time2
                except Exception as e:
                    log_dict['simulateErr'].append(str(task))                
                    log_dict['simulateErr'].append(get_log_item(traceback.format_exc(), e))
                    finish = True

        total_time = datetime.datetime.utcnow() - start_time
        log_dict['timeStatistic'] = [str(total_time), str(execute_time), str(load_file_time), str(remove_file_time)]
        return final_result, log_dict

if __name__ == "__main__":
    SPS().run()
