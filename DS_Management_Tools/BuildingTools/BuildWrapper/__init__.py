#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 21.05.2014

@author: Q350609
'''
import os
import sys
import hashlib
import traceback
import time
import shutil
import datetime
from BuildingTools.BuildWrapper.DWLibrary.FSHelper import FSHelper
from BuildingTools.BuildWrapper.DWLibrary import DWError


sys.path.append('dymola.egg')

from dymola.dymola_interface import DymolaInterface

from dymola.dymola_exception import DymolaException


class ModelGenerator(object):

    def __init__(self, tsts_data, dymola_interface, build_directory, base_path, libraries=None,
                 translate_fmu=False, fmu_type='all', temp_dir='', fmu_name=''):
        self.__libraries_required = libraries
        self.__model = tsts_data
        self.build_directory = build_directory
        self.__fmu_name = fmu_name
        self.sub_dir = hashlib.md5(self.__model['name'] + self.__model['value']).hexdigest()
        self.dymola_interface = dymola_interface
        self.base_path = base_path
        self.fmu = translate_fmu
        self.__temp_dir = temp_dir
        self.__fmu_type = fmu_type

    def generate_fs(self):
        now = datetime.datetime.now()
        build_directory = self.build_directory
        time_stamp = now.strftime('%Y%m%d%H%M%S%f')
        if self.fmu == False:
            temporary_directory = os.path.join(build_directory, 'temp' + time_stamp)
            os.makedirs(temporary_directory)
            self.prepare_directory(self.__model['name'], build_directory, self.sub_dir)
            temporary_directory = os.path.join(build_directory, 'temp' + time_stamp)
        else:
            temporary_directory = os.path.join(self.__temp_dir, 'temp' + time_stamp)
            os.makedirs(temporary_directory)
        return temporary_directory

    def prepare_directory(self, model_name, build_directory=u'.', sub_dir=''):
        """Prepare the directory for a certain model in the build_directory"""
        file_path = model_name.replace('.', os.sep)
        directory_path = os.path.join(build_directory, file_path, sub_dir)
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
        return directory_path

    def build_model(self):
        return_value = False
        """Build Dymola model according to the settings"""

        temporary_directory = self.generate_fs()
        dymola = self.dymola_interface
        log = ''
        try:

            if self.__libraries_required is not None:
                self.load_libraries_mos(dymola)
            model = Model(self.__model['name'], self.__model['value'],
                          self.build_directory, temporary_directory,
                          self.sub_dir,
                          self.fmu, self.__fmu_type, self.__fmu_name)
            result = model.execute_script(dymola)  # True: build successfully, False: failed
            if not result:
                log = dymola.getLastError()
                print log
            else:
                return_value = True
            shutil.rmtree(temporary_directory)
        except OSError as e:
            print traceback.format_exc()
        except Exception as e:
            print traceback.format_exc()
            raise e
        return return_value, log

    def get_directory_path(self):
        file_path = self.__model['name'].replace('.', os.sep)
        directory_path = os.path.abspath(os.path.join(self.build_directory,
                                                      file_path, self.sub_dir))
        return directory_path

    def get_relpath(self):
        return os.path.relpath(self.get_directory_path(), self.build_directory)

    def get_files_path(self):
        directory_path = self.get_directory_path()
        files_path = [os.path.join(directory_path, f) for f in FSHelper.get_dymosim_files()]
        return files_path
    # Pack it together!

    def remove_files(self):
        file_path = self.__model['name'].replace('.', os.sep)
        directory_path = os.path.abspath(os.path.join(self.build_directory,
                                                      file_path, self.sub_dir))
        shutil.rmtree(directory_path)

    def build_dummy_dymola_models(self):
        """Build dummy Dymola model according to the settings"""
        build_directory = self.build_directory
        if not os.path.exists(build_directory):
            os.makedirs(build_directory)
        for model_name in self.__model_name_set:
            model_name = model_name
            self.prepare_directory(model_name, build_directory)

            for file_name in FSHelper.get_dymosim_files():
                destination_file_name = FSHelper.file_path_with_prefix(
                    model_name, file_name, build_directory)
                shutil.copyfile(file_name, destination_file_name)

    def load_libraries_mos(self, dymola):
        """ Get the command of loading libraries for the mos script in dymola"""
        for library_to_load_name in self.__libraries_required.keys():
            library_path = self.__libraries_required[library_to_load_name]
            if library_path.endswith(".mo"):
                mo_file = library_path
            else:
                mo_file = os.path.join(library_path, "package.mo")
            mo_file = os.path.join(self.base_path, mo_file)
            res = dymola.openModel(mo_file, False)
            if not res:
                print "mo_file not found:", mo_file
                raise DWError.OpenModelError(dymola.getLastError())

    def check(self):
        return False


class Model():

    def __init__(self, model_name, model_script,  build_directory, temporary_directory, sub_dir='', fmu=False, fmu_type='all', fmu_name=''):
        self.__build_times = 0
        self.__model_name = model_name
        self.__fmu = fmu
        self.__fmu_name = model_name.replace('_', '_0').replace('.', '_') + '.fmu'
        self.__fmu_final_name = fmu_name
        self.__fmu_type = fmu_type
        self.__pre_script = self.get_pre_mos(temporary_directory)
        self.__post_script = self.get_post_mos(build_directory, temporary_directory, sub_dir)
        self.__error_msg = None
        self.__script = model_script

    @property
    def error_msg(self):
        return self.__error_msg

    @property
    def model_name(self):
        return self.__model_name

    def __str__(self):
        return u'model name is %s,\n ' % self.__model_name

    def get_clear_up_mos(self, temporary_directory):
        """ Get the command of data clean up for the mos script in dymola"""

        mos_string = ""
        if not self.__fmu:
            for useful_data in FSHelper.get_dymosim_files():
                useful_data_path = os.path.join(temporary_directory, useful_data)
                mos_string += (u"Modelica.Utilities.Files.remove(\"" +
                               useful_data_path.replace("\\", "\\\\") +
                               u"\");\n")
        return mos_string

    def get_pre_mos(self, temporary_directory):
        mos_string = ("cd(\"" + temporary_directory.replace("\\", "\\\\") + "\");\n")
        # mos_string += self.get_clear_up_mos(temporary_directory)
        mos_string += u"clearlog();\n"
        mos_string += u"Advanced.TranslationInCommandLog=true;\n"
        return mos_string

    def get_post_mos(self, build_directory, temporary_directory, sub_dir=''):
        file_path = self.__model_name.replace('.', os.sep)
        if self.__fmu == False:
            directory_path = os.path.abspath(os.path.join(build_directory,
                                                          file_path, sub_dir))
        else:
            directory_path = os.path.abspath(build_directory)
        mos_string = u''
        if not self.__fmu:
            for useful_data in FSHelper.get_dymosim_files():
                new_file_path = os.path.join(directory_path,
                                             useful_data)
                useful_data_path = os.path.join(temporary_directory,
                                                useful_data)
                mos_string += (u"Modelica.Utilities.Files.copy(\"" +
                               useful_data_path.replace("\\", "\\\\") +
                               u"\", \"" +
                               new_file_path.replace("\\", "/") +
                               u"\", true);\n")
        else:
            new_file_path = os.path.join(directory_path,
                                         self.__fmu_final_name)
            useful_data_path = os.path.join(temporary_directory,
                                            self.__fmu_name)
            print useful_data_path, new_file_path
            mos_string += (u"Modelica.Utilities.Files.copy(\"" +
                           useful_data_path.replace("\\", "\\\\") +
                           u"\", \"" +
                           new_file_path.replace("\\", "/") +
                           u"\", true);\n")
        mos_string += ('cd("..");\n')
        return mos_string

    def set_build_times(self):
        if self.__build_times < 2:
            self.__build_times += 1
        else:
            raise DWError.BuildError('Building Error. Model name ' + self.__model_name)

    def execute_script(self, dymola):
        self.set_build_times()
        dymola.ExecuteCommand(self.__pre_script)
        print self.__model_name + self.__script
        if not self.__fmu:
            result = dymola.translateModel(self.__model_name + self.__script)
        else:
            result = dymola.translateModelFMU(self.__model_name + self.__script, fmiType=self.__fmu_type)
        if not result:
            self.__error_msg = dymola.getLastError()
            return False
        else:
            dymola.ExecuteCommand(self.__post_script)
            print '##########THE %s Time Building Success######%s########' % (self.__build_times, self.__model_name)
            print '********************', str(dymola.getLastError()), '***********'
            return True
