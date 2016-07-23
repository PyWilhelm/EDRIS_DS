'''
Created on 21.05.2014

@author: Q350609tests_dir
'''

import os
import subprocess
import shutil
import DyMat

from DWLibrary.FSHelper import FSHelper
from dymola_wrapper.DymosimSettings import DymosimSettings

import DWLibrary.DWError as EDRISError
import DWLibrary.DymolaCompare

class SimulatorGenerator():
    def __init__(self, tst, build_directory='.',
                 tsts_directory='.', sub_directory='', is_jenkins=False):
        self.__tst = tst
        self.__build_directory = build_directory
        self.__tsts_directory = tsts_directory
        self.__sub_directory = sub_directory
        self.__is_jenkins = is_jenkins

    def simulate(self):

        #if not self.found_model():
        #    raise EDRISError.ModelNotFoundError('The Model %s is not found!' % self.__tst.model_name)

        #Simulate according to the test data
        dsin_txt_path = FSHelper.file_path_with_prefix(self.__tst.model_name,
                                                       "dsin.txt",
                                                       self.__build_directory)
        default_dymosim_settings = DymosimSettings()

        result_file_name = 'newResult.mat'
        if self.__sub_directory != '':
            tst_specific_directory = os.path.join(self.__tsts_directory,
                                                  self.__tst.tst_name,
                                                  self.__sub_directory)
        else:
            tst_specific_directory = os.path.join(self.__tsts_directory,
                                                  self.__tst.tst_name)
        if not os.path.exists(tst_specific_directory):
            os.makedirs(tst_specific_directory)
        dsin_new_path = os.path.join(tst_specific_directory, 'dsin.txt')

        default_dymosim_settings.set_simulation_settings(self.__tst.simulation_settings)
        default_dymosim_settings.set_parameters(self.__tst.parameters)

        default_dymosim_settings.write_dsin(dsin_new_path)
        out_result_file_path = os.path.join(tst_specific_directory,
                                            result_file_name)


        old_pwd = os.getcwd()
        if not os.path.exists(dsin_new_path):
            raise DWLibrary.DWError.SimulationError("dsin.txt not found")
        os.chdir(tst_specific_directory)
        p = subprocess.Popen([FSHelper.get_dymosim_path(self.__tst.model_name, self.__build_directory, is_jenkins=self.__is_jenkins),
                             '-f', 'nolog',
                             dsin_new_path, out_result_file_path],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        return_message = p.communicate()
        return_value = p.returncode
        os.chdir(old_pwd)

        if return_value != 0:
            raise DWLibrary.DWError.SimulationError("Simulation failed:" + return_message[0] + return_message[1])
        return out_result_file_path, return_message

    def check_results(self):
        """ Check the according results in test with the reference signal, see if
        they match each other """

        test_specific_directory = os.path.join(self.__tsts_directory, self.__tst.tst_name)

        reference_result_path = os.path.join(test_specific_directory,
                                            'referenceResult.mat')
        new_result_path = os.path.join(test_specific_directory, 'newResult.mat')
        if not os.path.exists(new_result_path):
            raise DWLibrary.DWError.FileNotFound(new_result_path)

        if not os.path.exists(reference_result_path):
            shutil.copyfile(new_result_path, reference_result_path)
            raise DWLibrary.DWError.FileNotFound(reference_result_path)
        else:
            reference_result = DyMat.DymolaMat(reference_result_path)
            new_result = DyMat.DymolaMat(new_result_path)
            DWLibrary.DymolaCompare.compare_all_signals(self.__tst.results, reference_result,
                                               new_result)




