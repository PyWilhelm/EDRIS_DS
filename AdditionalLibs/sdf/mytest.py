import unittest
import sdf
import numpy as np
import h5py

dss = sdf.load_all('report-1408008132.580000.sdf')
print len(dss)
for ds in dss:
    print ds.name, ds.data, ds.scales