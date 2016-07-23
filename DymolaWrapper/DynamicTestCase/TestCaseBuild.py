import unittest

from DynamicTestCase.DynamicTestCaseGenerator import create_dynamic_method_check_build_models
from DynamicTestCase.DynamicTestCaseGenerator import create_model_name, BuildTest
from SimulatorTestModel.SimulatorTestDymola import SimulatorTestDymola
from DWLibrary.EnvConfiguration import __env_configuration__


tst_class = SimulatorTestDymola


import json

tsts_json = __env_configuration__.tsts_json["tests"]
#print json.dumps(tsts_json, indent=2)

modelnameset = tst_class.__init_model_name_set__(tsts_json)

for index, model_name in enumerate(modelnameset):
    method = create_dynamic_method_check_build_models(model_name)
    method.__doc__ = model_name
    method.__name__ = create_model_name(index, model_name, "_build")
    setattr(BuildTest, method.__name__, method)
    del method

if __name__ == '__main__':
    print('unitest begins')
    unittest.main()
