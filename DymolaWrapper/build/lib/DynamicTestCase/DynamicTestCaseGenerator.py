from dymola_wrapper.ModelGenerator import ModelGenerator
from dymola_wrapper.SimulatorGenerator import SimulatorGenerator
from DWLibrary import DWError
import unittest
import re
from DWLibrary.EnvConfiguration import __env_configuration__


class BuildTest(unittest.TestCase): # pylint: disable=too-many-public-methods
    @classmethod
    def setUpClass(cls):
        cls.model_generator = ModelGenerator()
        if not cls.model_generator.check():
            FailedModelList.failed_model_list = cls.model_generator.build_models()

    def test_check_libraries(self):
        self.model_generator.check_libraries()



class SimulationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass


def create_dynamic_method_simulate_check(tst): # pylint: disable=too-many-public-methods
    """just don't include `test` in the function name here, nose will try to
    run it"""
    def dynamic_tst_method(self):
        """ Dynamically generated method running all the tests at once """

        self.simulator_generator = SimulatorGenerator(tst, 
                                                      build_directory=__env_configuration__.build_dir,
                                                      tsts_directory=__env_configuration__.tsts_dir, 
                                                      is_jenkins=True)
        self.simulator_generator.simulate()
        self.simulator_generator.check_results()
    return dynamic_tst_method

def create_dynamic_method_check_build_models(model_name):
    """ Creates the dynamic method for checking the build results """
    def dynamic_model_method(self):
        """ Dynamically generated method checking built models """
        print(len(FailedModelList.failed_model_list))
        for model in FailedModelList.failed_model_list:
            if(model.model_name == model_name):
                raise DWError.BuildError('BUILD ERROR: \nModel Name: %s\n Error Information:\n%s'
                                     %(model.model_name,model.error_msg))
    return dynamic_model_method

def create_name(index, tst):
    """ dynamically creating the tst names """
    tst_name_escaped = re.sub('[^0-9a-zA-Z]', '_', tst.tst_name)
    name_of_the_class = str('test_test_{0}_'.format(index) + tst_name_escaped)
    return name_of_the_class

def create_model_name(index, model_name, suffix=""):
    """ dynamically creating the test names """
    model_name_escaped = re.sub('[^0-9a-zA-Z]', '_', model_name)
    name_of_the_class = str('test_model_{0}_'.format(index) + model_name_escaped + suffix)
    return name_of_the_class

class FailedModelList():
    failed_model_list = []
