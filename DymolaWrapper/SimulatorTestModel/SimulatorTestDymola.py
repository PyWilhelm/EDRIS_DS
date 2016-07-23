from SimulatorTestModel.SimulatorTest import SimulatorTest

class SimulatorTestDymola(SimulatorTest):
    def __init__(self, tst_item, verbose=False):
        SimulatorTest.__init__(self, tst_item)
        self.__tstName = tst_item["testName"]
        self.__modelName = tst_item["modelName"]
        if "simulationSettings" in tst_item:
            self.__simulationSettings = tst_item["simulationSettings"]
        else:
            self.__simulationSettings = dict()
        if "parameters" in tst_item:
            self.__parameters = tst_item["parameters"]
        else:
            self.__parameters = dict()
        self.__results = tst_item["results"]
        if verbose == True:
            print((tst_item["results"]))

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

