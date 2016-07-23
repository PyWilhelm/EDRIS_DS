'''
Created on 17.03.2014

@author: Torsten.Sommer
'''
import unittest
import sdf
import numpy as np
import math

class Test(unittest.TestCase):

    def test_roundtrip(self):
        
        # create a scale
        ds1 = sdf.Dataset('DS1',
                          comment='dataset 1',
                          data=np.array([0.1, 0.2, 0.3]),
                          display_name='Scale 1',
                          scale_name='Scale 1',
                          quantity='Q1',
                          unit='U1',
                          display_unit='DU1',
                          is_scale=True)
        
        # create a 1D dataset
        ds2 = sdf.Dataset('DS2',
                          comment='dataset 2',
                          data=np.array([1, 2, 3]),
                          display_name='Dataset 2',
                          quantity='Q2',
                          unit='U2',
                          display_unit='DU2',
                          scales=[ds1])
        
        # create a group
        g = sdf.Group(name='/',
                      comment='my comment',
                      attributes={'A1': 'my string', 'A2': 0.1, 'A3': 1},
                      datasets=[ds1, ds2])
        
        # save the group
        sdf.save('test1.sdf', g)

        # load DS2 from the file        
        ds2r = sdf.load('test.sdf', '/DS2')

        # make sure the content is still the same
        self.assertEqual(ds2, ds2r)
        
    def test_3D_example(self):
        
        RPM2RADS = 2 * math.pi / 60
        
        kfric=1                 # [Ws/rad] angular damping coefficient [0;100]
        kfric3=1.5e-6           # [Ws3/rad3] angular damping coefficient (3rd order) [0;10-3]
        psi=0.2                 # [Vs] flux linkage [0.001;10]
        res=5e-3                # [Ohm] resistance [0;100]
        u_ref=200               # [V] reference DC voltage [0;1000]
        k_u=5                   # linear voltage coefficient [-100;100]
    
        tau = np.arange(0, 230+10, 10)
        w = np.concatenate((np.arange(0, 500, 100), np.arange(500, 12e3+500, 500))) * RPM2RADS
        u = np.asarray([200, 300, 400])
    
        # calculate the power losses
        TAU, W, U = np.meshgrid(tau, w, u, indexing='ij')
    
        P_loss = kfric * W + kfric3 * W ** 3 + (res * (TAU / psi) ** 2) + k_u * (U - u_ref)
    
        # create the scales
        ds_tau = sdf.Dataset('tau',
                          comment='Torque',
                          data=tau,
                          scale_name='Torque',
                          quantity='Torque',
                          unit='N.m',
                          is_scale=True)
        
        ds_w = sdf.Dataset('w',
                          comment='Speed',
                          data=w,
                          scale_name='Speed',
                          quantity='AngularVelocity',
                          unit='rad/s',
                          display_unit='rpm',
                          is_scale=True)
        
        ds_u = sdf.Dataset('u',
                          comment='DC voltage',
                          data=u,
                          scale_name='DC voltage',
                          quantity='Voltage',
                          unit='V',
                          is_scale=True)
        
        # create the dataset
        ds_P_loss = sdf.Dataset('P_loss',
                          comment='Power losses',
                          data=P_loss,
                          quantity='Voltage',
                          unit='V',
                          scales=[ds_tau, ds_w, ds_u])
        
        # create a group
        g = sdf.Group(name='/',
                      comment='Example loss characteristics of an e-machine w.r.t. torque, speed and DC voltage',
                      attributes={'AUTHOR': 'John Doe'},
                      datasets=[ds_tau, ds_w, ds_u, ds_P_loss])

        errors = sdf.validate(g)
        self.assertEqual([], errors)
        
        sdf.save('emachine.sdf', g)
        
    def test_validate_group(self):
        g = sdf.Group('8')    
        errors = sdf._validate_group(g, is_root=False)
        self.assertEqual(['Object names must only contain letters, digits and underscores ("_") and must start with a letter'], errors)
        
        g.name = 'G1'
        errors = sdf._validate_group(g, is_root=False)
        self.assertEqual([], errors)

        
    def test_validate_dataset(self):
        ds1 = sdf.Dataset('DS1')
             
        ds1.data = 1
        errors = sdf._validate_dataset(ds1)
        self.assertEqual(['Dataset.data must not be a numpy.ndarray'], errors)
        
        ds1.data = np.array([])
        errors = sdf._validate_dataset(ds1)
        self.assertEqual(['Dataset.data must not be empty'], errors)

        ds1.data = np.array(1).astype(np.float32)
        errors = sdf._validate_dataset(ds1)
        self.assertEqual(['Dataset.data.dtype must be one of numpy.float64 or numpy.int32'], errors)
        
        ds1.data = np.array([1.0, 2.0])
        errors = sdf._validate_dataset(ds1)
        self.assertEqual(['The number of scales does not match the number of dimensions'], errors)

        ds2 = sdf.Dataset('DS2', data=np.array([0,1,2]), is_scale=True)
        ds1.scales = [ds2]
        errors = sdf._validate_dataset(ds1)
        self.assertEqual([], errors)
        
        ds2.data = np.array([[1,2], [3,4]])
        errors = sdf._validate_dataset(ds2)
        self.assertEqual(['Scales must be one-dimensional'], errors)
        
        ds2.data = np.array([0,1,1])
        errors = sdf._validate_dataset(ds2)
        self.assertEqual(['Scales must be strictly monotonic increasing'], errors)
        
if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
