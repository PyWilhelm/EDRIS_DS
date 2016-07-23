import os
import logging

from DWLibrary.FSHelper import FSHelper
from DWLibrary import DWError
from DWLibrary import EnvConfiguration
class ModelBuildQueue():
    def __init__(self, model_name_list, libraries_required, build_directory, temporary_directory):
        #the parameter testplan should be the list of the SimulatorTest instances
        self.__queue = []
        self.__success_queue = []
        self.__failed_queue = []
        self.__model_name_list = set(model_name_list)
        self.__libraries_required = libraries_required
        self.__build_directory = build_directory
        self.__temporary_directory = temporary_directory
        self.__length = 0

    def initialize(self):
        for model_name in self.__model_name_list:
            self.__queue.append(Model(model_name, self.__build_directory, self.__temporary_directory))
        self.__length = len(self.__queue)

    def pop(self):
        return self.__queue.pop(0)

    def push(self, model):
        self.__queue.append(model)
        return self

    def is_empty(self):
        return len(self.__queue) == 0

    def is_failed_queue_empty(self):
        return len(self.__failed_queue) == 0

    def push_failed_queue(self, model):
        self.__failed_queue.append(model)

    def push_success_queue(self, model):
        self.__success_queue.append(model)

    def get_failed_queue(self):
        return self.__failed_queue

    def log_output(self):
        models_dict_file = os.path.join(self.__build_directory, EnvConfiguration.__models_dict_file_name__)
        with open(models_dict_file, 'w+') as fh:
            msg = u'Building Process is finished. \nSuccessful Models: '
            for m in self.__success_queue:
                msg += m.model_name
                msg += u'\n'
                fh.write(m.model_name + '\n')
        msg += u'\nFailed Models: '
        for m in self.__failed_queue:
            msg += m.model_name
            msg += u'\n'
        logging.warning(msg)




class Model():

    def __init__(self, model_name, build_directory, temporary_directory):
        self.__build_times = 0
        self.__model_name = model_name
        self.__pre_script = self.get_pre_mos(temporary_directory)
        self.__post_script = self.get_post_mos(build_directory, temporary_directory)
        self.__error_msg = None

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
        for useful_data in FSHelper.get_dymosim_files():
            useful_data_path = os.path.join(temporary_directory, useful_data)
            mos_string += (u"Modelica.Utilities.Files.remove(\"" +
                          useful_data_path +
                          u"\");\n")
        return mos_string

    def get_pre_mos(self, temporary_directory):
        mos_string = ("cd(\"" + temporary_directory.replace("\\", "\\\\") + "\");\n")
        mos_string += self.get_clear_up_mos(temporary_directory)
        mos_string += u"clearlog();\n"
        mos_string += u"Advanced.TranslationInCommandLog=true;\n"
        return mos_string

    def get_post_mos(self, build_directory, temporary_directory):
        file_path = self.__model_name.replace('.', os.sep)
        directory_path = os.path.abspath(os.path.join(build_directory,
                                         os.path.split(file_path)[0]))
        file_name_without_extension = os.path.split(file_path)[1]

        mos_string = u''
        for useful_data in FSHelper.get_dymosim_files():
            new_file_path = os.path.join(directory_path,
                                         file_name_without_extension +
                                            u"_" + useful_data)
            useful_data_path = os.path.join(temporary_directory,
                                            useful_data)
            mos_string += (u"Modelica.Utilities.Files.copy(\"" +
                           useful_data_path.replace("\\", "\\\\") +
                           u"\", \"" +
                           new_file_path.replace("\\", "/") +
                           u"\", true);\n")
        return mos_string

    def set_build_times(self):
        if self.__build_times < 2:
            self.__build_times += 1
        else:
            raise DWError.BuildError('Building Error. Model name ' + self.__model_name)

    def execute_script(self, dymola):
        self.set_build_times()
        dymola.ExecuteCommand(self.__pre_script)
        result = dymola.translateModel(self.__model_name)
        print('##########THE %s Time Building######%s########' % (self.__build_times, self.__model_name))
        if not result:
            self.__error_msg = dymola.getLastError()
            return False
        else:
            dymola.ExecuteCommand(self.__post_script)
            print('##########THE %s Time Building Success######%s########' % (self.__build_times, self.__model_name))
            return True

