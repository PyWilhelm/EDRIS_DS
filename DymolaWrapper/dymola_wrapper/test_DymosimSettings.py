'''
Created on 21.05.2014

@author: Q350609
'''

import unittest
import dymola_wrapper.DymosimSettings as dys

class TestDymosimSettings(unittest.TestCase):
    def test_round_tripping(self):
        ds = dys.DymosimSettings()
        example_settings = {'StopTime' : 999, 'memkey': 3, 'lxd' : 4}
        example_parameters = {'StartSOC' : 0.463}
        ds.set_simulation_settings(example_settings)
        ds.set_parameters(example_parameters)
        dsin_path = ds.write_dsin()
        loaded_ds = dys.DymosimSettings(dsin_path)
        ss = loaded_ds.get_simulation_settings()
        ps = loaded_ds.get_parameters()

        for key in list(example_settings.keys()):
            self.assertEqual(ss[key], example_settings[key])
        loaded_ds.write_dsin('dsin_new.txt')
    
        # Unimplemented
        #for key in example_parameters.keys():
        #    self.assertEqual(ps[key], example_parameters[key])

