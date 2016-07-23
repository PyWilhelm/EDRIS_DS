# Copyright (C) 2014 Modelon GmbH. All rights reserved.
#
# This file is part of the Simulation Development Tools.
#
# This program and the accompanying materials are made
# available under the terms of the BSD 3-Clause License
# which accompanies this distribution, and is available at
# http://simdevtools.org/LICENSE.txt
#
# Contributors:
#   Torsten Sommer <torsten.sommer@modelon.com> - Initial API and implementation

'''
Generates a UserTab header from an SDF file

@author: Torsten.Sommer
'''

import sys
import numpy as np
import h5py
import h5py._hl
import sdf

def _get_arrays(ds):
    values = ', '.join(map(str, ds.data.flatten()))
    src = 'static double %s[%d]   = { %s };\n' % (ds.name, ds.data.size, values)

    for scale in ds.scales:
        values = ', '.join(map(str, scale.data))
        src += 'static double %s[%d] = { %s };\n' % (scale.name, scale.data.size, values)

    return src

def _calculate_offs(ds):
    offs = np.int_(np.zeros(32))
    offs[ds.value.ndim-1] = 1
    for i in reversed(range(ds.value.ndim-1)):
        offs[i] = offs[i+1] * ds.value.shape[i+1]
    return map(str, offs)

def _get_struct(filename, ds):
    zpad             = ['0'] * (32-ds.value.ndim)
    npad             = ['NULL'] * (32-ds.value.ndim)
    dims             = ', '.join(map(str, ds.value.shape) + zpad)
    
    scs = []
    for i in range(ds.value.ndim):
        scs += [ds.dims[i][0]]
    
    scales           = ', '.join(map(lambda s: s.name[1:], scs) + npad)
    offs             = ', '.join(_calculate_offs(ds))
    scalesQuantities = ', '.join(map(lambda s: '"%s"' % s.attrs['QUANTITY'], scs) + npad)
    scalesUnits      = ', '.join(map(lambda s: '"%s"' % s.attrs['UNIT'], scs) + npad)
    return \
'''
    {
      /* filename */         "%s",
      /* datasetname */      "%s",
      /* rank */             %d,
      /* dims */             {%s},
      /* numel */            %d,
      /* offs */             {%s},
      /* data */             %s,
      /* scales */           {%s},
      /* dataQuantity */     "%s",
      /* dataUnit */         "%s",
      /* scalesQuantities */ {%s},
      /* scalesUnits */      {%s},
    },
''' % (filename, ds.name, ds.value.ndim, dims, ds.value.size, offs, ds.name[1:], scales, ds.attrs['QUANTITY'], ds.attrs['UNIT'], scalesQuantities, scalesUnits)

def _is_scale(ds):
    for attr in ds.attrs:
        if attr == 'CLASS':
            return ds.attrs['CLASS'] == 'DIMENSION_SCALE'
    return False 

if __name__ == '__main__':
    
    # TODO: validate file
    
    filename = sys.argv[1]
    
    arrays = ''
    structs = ''
    nstructs = 0
    
    with h5py.File(filename, 'r') as f:
        for (name, ds) in filter(lambda x: isinstance(x[1], h5py._hl.dataset.Dataset), f.items()):
            values = ', '.join(map(str, ds.value.flatten()))
            arrays += 'static double %s[%d] = { %s };\n' % (ds.name[1:], ds.value.size, values)
             
            if not _is_scale(ds):
                structs += _get_struct(filename, ds)
                nstructs += 1
    
    
    f = open('UserTab.h', 'w')
    
    a = \
'''
#ifndef USERTAB_H
#define USERTAB_H

#include "HDF5TableInternal.h"

#define N_USERTABS %d

%s

static dataset userTabs[N_USERTABS] = {
%s
};

#endif
''' % (nstructs, arrays, structs)
    
    f.write(a)