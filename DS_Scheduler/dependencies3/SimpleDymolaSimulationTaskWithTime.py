#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, json, shutil, sys, datetime, logging, copy, traceback, numpy
import BaseTask
class SimpleDymolaSimulationTaskWithTime(BaseTask.BaseTask):

    def _prepare(self):
        sys.path.append(os.path.abspath('EDRIS_wrapper.egg'))
        os.environ['DYMOLA_RUNTIME_LICENSE'] = os.path.join(os.getcwd(), 'dymola.lic')
         

    def _run(self):
        result, log = self.simpleDymolaSimulation()
        return result, log
    

    def simpleDymolaSimulation(self):
        finish = False
        get_log_item = lambda tb, e: {'time': str(datetime.datetime.now()), 'type': str(type(e)), 'message': self._flatten(tb)}
        log_dict = dict()
        log_dict['simulateErr'] = []
        log_dict['resultErr'] = []
        log_dict['filesystemErr'] = []
        log_dict['simulationLogs'] = []
        start_time = datetime.datetime.utcnow()
        execute_time = start_time - start_time
        load_file_time = start_time - start_time

        import MyDyMat
        from dymola_wrapper.SimulatorGenerator import SimulatorGenerator
        from SimulatorTestModel import SimulatorTestDymola, SimulatorTest
        task = copy.deepcopy(self._parameters)
        mat_names_list = None
        mat_descr_list = None
        final_result = dict()
        task['testArguments']['testName'] = task['testArguments']['modelName'].split('.')[-1] + 'test'
        test = SimulatorTestDymola.SimulatorTestDymola(task['testArguments'])

        simulator_generator = SimulatorGenerator(test, build_directory=os.path.abspath('.'),
                                                tsts_directory=os.path.abspath('.') )

            
        current_time1 = datetime.datetime.utcnow()
        result_path = None
        try:
            result_path, sim_outputs = simulator_generator.simulate()
            log_dict['simulationLogs'].append(sim_outputs)
            current_time2 = datetime.datetime.utcnow()
            execute_time = execute_time + current_time2 - current_time1

            current_time1 = datetime.datetime.utcnow()
            
            results = MyDyMat.DymolaMat(result_path, mat_names_list, mat_descr_list)
            mat_names_list = results.names
            mat_descr_list = results.descr
            current_time2 = datetime.datetime.utcnow()
            load_file_time = load_file_time + current_time2 - current_time1
            for signal in test.results:
                try:
                    final_result[signal['signalName']] = self.dump_results(results.data(signal['signalName']))

                except Exception as e:
                    log_dict['resultErr'].append(get_log_item(traceback.format_exc(), e))
            try:
                shutil.rmtree(os.path.dirname(result_path))
            except Exception as e:
                log_dict['filesystemErr'].append(get_log_item(traceback.format_exc(), e))
        except Exception as e:
            log_dict['simulateErr'].append(str(task))
            log_dict['simulateErr'].append(get_log_item(traceback.format_exc(), e))

        total_time = datetime.datetime.utcnow() - start_time
        log_dict['timeStatistic'] = [str(total_time), str(execute_time), str(load_file_time)]
        return final_result, log_dict

    @staticmethod
    def dump_results(result):
        return json.dumps(result.tolist())

if __name__ == "__main__":
    SimpleDymolaSimulationTask().run()
