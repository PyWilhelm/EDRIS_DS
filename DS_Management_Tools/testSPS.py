#!/usr/bin/env python
# -*- coding: utf-8 -*-


from TaskController.BaseClass.Controller import Controller
import json
import os


def start_controller(nocache):
    _dir = os.path.dirname(os.path.abspath(__file__))
    controller = Controller(priority=99, no_cache=nocache)
    with open(_dir + '\\SPS_test_aio.json') as f:
        metatask_data = json.load(f)
    result_future = controller.add_metatask(metatask_data)
    result_future.get()


start_controller(False)
