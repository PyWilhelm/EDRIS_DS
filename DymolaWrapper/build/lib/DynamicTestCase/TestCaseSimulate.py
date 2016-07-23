import unittest

from DynamicTestCase.DynamicTestCaseGenerator import create_dynamic_method_simulate_check
from DynamicTestCase.DynamicTestCaseGenerator import create_model_name, SimulationTest
from SimulatorTestModel.SimulatorTestDymola import SimulatorTestDymola
from DWLibrary.EnvConfiguration import __env_configuration__

tst_class = SimulatorTestDymola

tsts_json = __env_configuration__.tsts_json[u"tests"]
tstplan = tst_class.__init_tstplan__(tsts_json)


for index, tst in enumerate(tstplan):

    print(tst.tst_name, tst.results)
    method = create_dynamic_method_simulate_check(tst)
    method.__name__ = create_model_name(index, tst.model_name, "_sim")
    method.__doc__ = tst.tst_name + ' of model ' + tst.model_name
    setattr(SimulationTest, method.__name__, method)
    del method

if __name__ == '__main__':
    print('unitest begins')
    unittest.main()
