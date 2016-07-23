'''
Created on 21.05.2014

@author: Q350609
'''

import json
import os, sys
import logging
import sys
from DWLibrary.AutomaticEdrisTaskgen import generate_new_tests

__configuration_file_name__ = "../Configuration/environmentalConfiguration.json"
__models_dict_file_name__ = 'models.cfg'


class EnvConfiguration():
    def __init__(self, json_data = None):
        if json_data != None:
            self.__env_configuration = json_data
        else:
            if os.environ.get('DYMOLA_TEST_ENV') != None:
                env_configuration_file_name = os.environ.get('DYMOLA_TEST_ENV')
            else:
                env_configuration_file_name = __configuration_file_name__
            try:
                self.__env_configuration = JsonReader(env_configuration_file_name).read()
            except Exception:
                self.__env_configuration = dict()
        self.__directory = dict()

    @property
    def working_dir(self):
        if not 'workingDirectory' in self.__directory:
            if os.environ.get('J_DYMOLA_WD') != None:
                self.__directory['workingDirectory'] = os.environ.get('J_DYMOLA_WD')
                if not os.path.exists(self.__directory['workingDirectory']):
                    os.makedirs(self.__directory['workingDirectory'])
            else:
                self.__directory['workingDirectory'] = os.path.abspath(
                                self.__env_configuration[u"workingDirectory"])
        return self.__directory['workingDirectory']

    @property
    def build_dir(self):
        if not 'buildDirectory' in self.__directory:
            self.__directory['buildDirectory'] = os.path.abspath(os.path.join(self.working_dir,
                                                                              'buildDirectory'))
        return self.__directory['buildDirectory']

    @property
    def tsts_dir(self):
        if not 'testsDirectory' in self.__directory:
            self.__directory['testsDirectory'] = os.path.abspath(os.path.join(self.working_dir,
                                                                              'testsDirectory'))
        return self.__directory['testsDirectory']

    @property
    def publish_dir(self):
        if not 'publishDirectory' in self.__directory:
            publish_direction = os.path.abspath(self.__env_configuration[u"publishDirectory"])
            self.__directory['publishDirectory'] = os.path.abspath(os.path.join(publish_direction,
                                                                                'testsDirection'))
        return self.__directory['publishDirectory']

    @property
    def tsts_json(self):
        if not 'testsJson' in self.__directory:
            self.__directory['testsJson'] = JsonReader(self.__env_configuration[u"testsJsonFilePath"]).read()
            #FIXME: maybe it is better to put it outside of the file
            self.__directory['testsJson'] = generate_new_tests(self.__env_configuration[u"testsJsonFilePath"], 
                                                               self.__env_configuration[u"librariesLocation"])
        return self.__directory['testsJson']

    @property
    def libraries_location(self):
        return self.__env_configuration[u'librariesLocation']

    @property
    def dymola_path(self):
        return self.__env_configuration[u"dymolaPath"]


    @property
    def dymola_interface_path(self):
        return self.__env_configuration[u"dymolaInterfacePath"]


class JsonReader():
    def __init__(self, file_name):
        self._file_name = file_name
        self._json_dict = None

    def read(self):
        with open(self._file_name, "r") as file_handle:
            self._json_dict = json.load(file_handle)
        return self._json_dict

'''
global singleton pattern
'''
__env_configuration__ = EnvConfiguration()

logging.basicConfig(stream=sys.stderr ,level=logging.WARNING)
