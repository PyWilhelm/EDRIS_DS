#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import nose
import unittest
import os
from TaskController.BaseClass.Controller import Controller
from TaskController import SSPS

import sdf


class TestTaskControllers(unittest.TestCase):

    def setUp(self):
        self.controller = Controller(priority=1000)

    def test_sps_mock(self):
        result = SSPS.start_controller(
            tid=100, input_data=None, controller=self.controller, block=False, method='SystemMock')
        result_sde = result.get()

        print result_sde.save_as_sdf()

        raise Exception("dummy exception")

    def tearDown(self):
        self.controller.stop()

    def assert_results(self, sdf_filename, variable_name, position, value, message='assertion failed'):
        ds = sdf.load(sdf_filename, variable_name)
        # value = ds.data[position]
        self.assertAlmostEqual(first, second, places=7, msg=message, delta=None)

if __name__ == '__main__':
    module_name = sys.modules[__name__].__file__
    result = nose.run(argv=[sys.argv[0], module_name, '--with-xunit', ])
    os._exit(1)
