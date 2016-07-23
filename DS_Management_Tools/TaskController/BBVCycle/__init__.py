#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''from TaskController.BaseClass.DymolaModelBuilder import DymolaModelBuilder
from TaskController.BBVCycle.Reporter import ReporterBBVCycle
from TaskController.BaseClass.DymolaOneTaskGenerator import DymolaOneTaskGenerator
from TaskController.BaseClass.BaseController import BaseController
import TaskController.SPS
from BuildingTools.ScriptGenerator import ModelSDS

ModelBuilder = DymolaModelBuilder
Reporter = ReporterBBVCycle
TaskGenerator = TaskGenerator


def start_controller(metatask_data, modelname, userinput, library, build=False):
    metatask_data = override(metatask_data, modelname, userinput, library)
    if build:
        classes = [TaskGenerator, Reporter, ModelBuilder, False]    
    else:
        classes = [TaskGenerator, Reporter, None, False]  
    c = BaseController(*classes)
    c.prepare(metatask_data)
    successful, failed = c.run()
'''
