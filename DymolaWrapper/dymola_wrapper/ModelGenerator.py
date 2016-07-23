'''
Created on 21.05.2014

@author: Q350609
'''

import datetime
import os, sys, re
import shutil

from DWLibrary.EnvConfiguration import __env_configuration__  #global environment configuration
from SimulatorTestModel.SimulatorTestDymola import SimulatorTestDymola
from dymola_wrapper.ModelBuildQueue import ModelBuildQueue
import DWLibrary.FSHelper

sys.path.append(__env_configuration__.dymola_interface_path)

from dymola.dymola_interface import DymolaInterface

from dymola.dymola_exception import DymolaException


class ModelGenerator(object):
    def __init__(self, tst_class=SimulatorTestDymola):
        tsts_json = __env_configuration__.tsts_json["tests"]
        self.__libraries_required = __env_configuration__.tsts_json["librariesRequired"]
#        self.__testplan = test_class.__init_testplan__(tsts_json)
        self.__model_name_set = tst_class.__init_model_name_set__(tsts_json)

    @property
    def model_name_set(self):
        return self.__model_name_set

    @property
    def model_name_list(self):
        name_list = []
        for model_name in self.__model_name_set:
            name_list.append(model_name)
        return name_list

    def generate_fs(self):
        now = datetime.datetime.now()
        build_directory = __env_configuration__.build_dir
        time_stamp = now.strftime('%Y%m%d%H%M%S%f')
        temporary_directory = os.path.join(build_directory, 'temp' + time_stamp)

        os.makedirs(temporary_directory)

        for model_name in self.__model_name_set:
            self.prepare_directory(model_name, __env_configuration__.build_dir)

        return temporary_directory


    def prepare_directory(self, model_name, build_directory='.'):
        """Prepare the directory for a certain model in the build_directory"""
        file_path = model_name.replace('.', os.sep)
        directory_path = os.path.join(build_directory, os.path.split(file_path)[0])
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
        return directory_path


    def check_libraries(self):
        """Build Dymola model according to the settings"""
        temporary_directory = self.generate_fs()

        model_build_queue = ModelBuildQueue(self.model_name_list, self.__libraries_required,
                                      __env_configuration__.build_dir, temporary_directory)

        model_build_queue.initialize()
        # dymola.ExecuteCommand(u"Advanced.TranslationInCommandLog=true;\n")
        dymola = None
        try:
            dymola = DymolaInterface(__env_configuration__.dymola_path)
            self.load_libraries_mos(dymola)
            errorLog = ''
            for library in self.__libraries_required:
                dymola.checkModel(self.__get_modelica_lib_name(library["library"]))
                errorLog += dymola.getLastError()
            if errorLog != '':
                raise Exception(errorLog)
        except Exception as exception:
            raise exception
        finally:
            if dymola is not None:
                dymola.close()
                dymola = None

    def __get_modelica_lib_name(self, library_entry):
        library_paths = __env_configuration__.libraries_location
        return os.path.split(library_paths[library_entry])[-1]
        

    def build_models(self):
        """Build Dymola model according to the settings"""
        temporary_directory = self.generate_fs()

        model_build_queue = ModelBuildQueue(self.model_name_list, self.__libraries_required,
                                      __env_configuration__.build_dir, temporary_directory)

        model_build_queue.initialize()

        dymola = None
        try:
            dymola = DymolaInterface(__env_configuration__.dymola_path)
            self.load_libraries_mos(dymola)
            while not model_build_queue.is_empty():
                model = model_build_queue.pop()
                print(model)
                result = model.execute_script(dymola) #True: build successfully, False: failed
                if not result:
                    model_build_queue.push_failed_queue(model)
                else:
                    model_build_queue.push_success_queue(model)
            model_build_queue.log_output()
        except Exception as exception:
            raise exception
        finally:
            if dymola is not None:
                dymola.close()
                dymola = None
        return model_build_queue.get_failed_queue()


    def build_dummy_dymola_models(self):
        """Build dummy Dymola model according to the settings"""
        build_directory = __env_configuration__.build_dir
        if not os.path.exists(build_directory):
            os.makedirs(build_directory)
        for model_name in self.__model_name_set:
            model_name = model_name
            self.prepare_directory(model_name, build_directory)

            for file_name in DWLibrary.FSHelper.FSHelper.get_dymosim_files():
                destination_file_name = DWLibrary.FSHelper.FSHelper.file_path_with_prefix(
                        model_name, file_name, build_directory)
                shutil.copyfile(file_name, destination_file_name)

    def load_libraries_mos(self, dymola):
        """ Get the command of loading libraries for the mos script in dymola"""
        for library_to_load in self.__libraries_required:
            library_to_load_name = library_to_load["library"]
            library_path = __env_configuration__.libraries_location[library_to_load_name]
            if library_path.endswith(".mo"):
                mo_file = library_path
            else:
                mo_file = os.path.join(library_path, "package.mo")

            res = dymola.openModel(os.path.abspath(mo_file), False)
            if not res:
                raise DWLibrary.DWError.OpenModelError(dymola.getLastError())

    def check(self):
        return False

