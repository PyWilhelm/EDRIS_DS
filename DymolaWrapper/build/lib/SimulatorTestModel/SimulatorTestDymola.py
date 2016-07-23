from SimulatorTestModel.SimulatorTest import SimulatorTest

class SimulatorTestDymola(SimulatorTest):
    def __init__(self, tst_item, verbose=False):
        SimulatorTest.__init__(self, tst_item)
        self.__tstName = tst_item[u"testName"]
        self.__modelName = tst_item[u"modelName"]
        if u"simulationSettings" in tst_item:
            self.__simulationSettings = tst_item[u"simulationSettings"]
        else:
            self.__simulationSettings = dict()
        if u"parameters" in tst_item:
            self.__parameters = tst_item[u"parameters"]
        else:
            self.__parameters = dict()
        self.__results = tst_item[u"results"]
        if verbose == True:
            print(tst_item[u"results"])

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
    def parameters(self):
        return self.__parameters

    @property
    def results(self):
        return self.__results

