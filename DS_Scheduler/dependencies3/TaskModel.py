import sys
sys.path.append("EDRIS_wrapper-dev-py2.7.egg")

from SimulatorTestModel.SimulatorTestDymola import SimulatorTestDymola
from SimulatorTestModel.SimulatorTest import SimulatorTest

class TaskModel(SimulatorTestDymola):
    def __init__(self, tst_item):
        SimulatorTest.__init__(self, tst_item)
        self.__tstName = tst_item[u"taskName"]
        self.__modelName = tst_item[u"modelName"]
        if u"simulationSettings" in tst_item:
            self.__simulationSettings = tst_item[u"simulationSettings"]
        else:
            self.__simulationSettings = dict()
        if u"staticParameters" in tst_item:
            self.__static_parameters = tst_item[u"staticParameters"]
        else:
            self.__static_parameters = dict()
        if u"dynamicParameters" in tst_item:
            self.__dynamic_parameters = tst_item[u"dynamicParameters"]
        else:
            self.__dynamic_parameters = []
        self.__results = tst_item[u"results"]
        self.__parameters = None

    @property
    def static_parameters(self):
        return self.__static_parameters

    @property
    def dynamic_parameters(self):
        return self.__dynamic_parameters

    @property
    def parameters(self):
        return self.__parameters

    def set_parameters(self, para_dict):
        self.__parameters = self.static_parameters
        for name in para_dict.keys():
            self.__parameters[name] = para_dict[name]
    @property
    def tst_name(self):
        return self.__tstName

    @property
    def model_name(self):
        return self.__modelName

    @property
    def simulation_settings(self):
        return self.__simulationSettings


    @property
    def results(self):
        return self.__results

