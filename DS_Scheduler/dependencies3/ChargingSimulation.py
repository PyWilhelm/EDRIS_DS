#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, json, shutil, sys, datetime, logging, copy, traceback, numpy
import BaseTask, SimpleDymolaSimulationTask


class ChargingSimulation(SimpleDymolaSimulationTask.SimpleDymolaSimulationTask):

    def prepareChargingSimulation(self):
        for functionArgumentsKey in self._parameters["functionArguments"].keys():
            for parametersKey in self._parameters["functionArguments"][functionArgumentsKey].keys():
                self._parameters["testArguments"]["parameters"][parametersKey] \
                = self._parameters["functionArguments"][functionArgumentsKey][parametersKey]
        
    def _run(self):
        result, log = self.chargingSimulation()
        return result, log
    

    def chargingSimulation(self):
        self.prepareChargingSimulation()
        return self.simpleDymolaSimulation()

if __name__ == "__main__":
    ChargingSimulation().run()
