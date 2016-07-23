'''
Copyright (C) 2014 Modelon GmbH. All rights reserved.

This file is part of the Simulation Development Tools.

This program and the accompanying materials are made
available under the terms of the BSD 3-Clause License
which accompanies this distribution, and is available at
http://opensource.org/licenses/BSD-3-Clause

Contributors:
    Torsten Sommer <torsten.sommer@modelon.com> - Initial API and implementation
'''
import os
import numpy as np
import h5py
from units import convert_unit
import re

__version__ = '0.1.0'

        
class Group(object):
    ''' SDF Group '''
    
    def __init__(self, name, comment=None, attributes=dict(), groups=None, datasets=None):
        ''' Default value of parameters is set to None instead of '[]'
            the function keeps using the same object, in each call. 
            This modifications are 'sticky'. Therefore, we use a placeholder 
            value (e.g. None) instead of modifying the default value.
            Info from http://effbot.org/zone/default-values.htm'''
        self.name = name
        self.comment = comment
        self.attributes = attributes
        self.groups = groups if groups != None else []
        self.datasets = datasets if datasets != None else []
    
class Dataset(object):
    ''' SDF Dataset '''
    
    def __init__(self, name,
                 comment=None,
                 attributes=dict(),
                 data=np.empty(0),
                 display_name=None,
                 scale_name=None,
                 quantity=None,
                 unit=None,
                 display_unit=None,
                 is_scale=False,
                 scales=None # bug fixed. same reason as Class 'Group'
                 ):
        self.name = name
        self.comment = comment
        self.attributes = attributes
        self.data = data
        self._display_name = display_name
        self.quantity = quantity
        self.unit = unit
        self._display_unit = display_unit
        self.is_scale = is_scale
        self.scale_name = scale_name
        self.scales = scales if scales != None else []
        
    @property
    def display_data(self):
        return convert_unit(self.data, self.unit, self.display_unit)
    
    @display_data.setter
    def display_data(self, value):
        self.data = convert_unit(value, self.display_unit, self.unit)

    @property
    def display_name(self):
        return self._display_name if self._display_name else self.name
    
    @display_name.setter
    def display_name(self, value):
        self._display_name = value

    @property
    def display_unit(self):
        return self._display_unit if self._display_unit else self.unit
    
    @display_unit.setter
    def display_unit(self, value):
        self._display_unit = value
        
    def validate(self):
        if self.display_unit and not self.unit:
            return ('ERROR', 'display_unit was set but no unit')
        
        if self.minimum != None and (self.data < self.minimum).any():
            return ('WARNING', 'some values are less than the allowed minimum (%s)' % self.minimum)
        
        if self.maximum != None and (self.data > self.maximum).any():
            return ('WARNING', 'some values are greater than the allowed maximum (%s)' % self.maximum)          
        
        return 'OK'
    
    # some shorthand aliases    
    @property
    def d(self):
        return self.data
    
    dd = display_data
    
    def __str__(self):
        return "dataset(name='%s', data=%s, comment='%s', display_name='%s', quantity='%s', unit='%s', display_unit='%s', is_scale='%s', scale_name='%s')" \
             % (self.name, self.data, self.comment, self.display_name, self.quantity, self.unit, self.display_unit, self.is_scale, self.scale_name) 
        
    def __eq__(self, other):
        equal = self.name == other.name \
            and (self.data == other.data).all() \
            and self.comment == other.comment \
            and self.display_name == other.display_name \
            and self.quantity == other.quantity \
            and self.unit == other.unit \
            and self.display_unit == other.display_unit \
            and self.is_scale == other.is_scale \
            and self.scale_name == other.scale_name \
            # and (self.scales == other.scales)
            
        for ri in range(len(self.scales)):
            equal = equal and self.scales[ri] == other.scales[ri]
                        
        return equal
    
def validate(obj):
    errors = []
    
    if isinstance(obj, Group):
        errors += _validate_group(obj, is_root=True)
    elif isinstance(obj, Dataset):
        errors += _validate_dataset(obj)
    else:
        errors.append('Unknown object type: %s' % type(obj))
    
    return errors

def _validate_group(group, is_root=False):
    errors = []
    
    if not is_root and not re.match(r'[A-Za-z]\w+', group.name):
        errors += ['Object names must only contain letters, digits and underscores ("_") and must start with a letter']
    
    for ds in group.datasets:
        errors += _validate_dataset(ds)
    
    return errors

def _validate_dataset(ds):
    
    if not type(ds.data) is np.ndarray:
        return ['Dataset.data must not be a numpy.ndarray']
    
    elif np.alen(ds.data) < 1:
        return ['Dataset.data must not be empty']
        
    elif not np.issubdtype(ds.data.dtype, np.float64) and not np.issubdtype(ds.data.dtype, np.int32):
        return ['Dataset.data.dtype must be one of numpy.float64 or numpy.int32']
    
    if ds.is_scale:
        if len(ds.data.shape) != 1:
            return ['Scales must be one-dimensional']
        if np.any(np.diff(ds.data) <= 0):
            return ['Scales must be strictly monotonic increasing']
    else: 
        if (len(ds.data.shape) >= 1) and (ds.data.shape[0] > 0) and not (len(ds.data.shape) == len(ds.scales)):
            return ['The number of scales does not match the number of dimensions']        
        
    return []
        
def load(filename, datasetname, quantity=None, unit=None, scaleQuantities=None, scaleUnits=None):
        
    with h5py.File(filename, 'r') as f:
        print f.keys()
        dsobj = f[datasetname]
        
        ds = _create_dataset(dsobj)
                
        # check the quantity
        if quantity and quantity != ds.quantity:
            raise Exception("Dataset '%s' in '%s' has the wrong quantity. Expected '%s' but was '%s'." % (datasetname, filename, quantity, ds.quantity))
        
        # check the unit
        if unit and unit != ds.unit:
            raise Exception("Dataset '%s' in '%s' has the wrong unit. Expected '%s' but was '%s'." % (datasetname, filename, unit, ds.unit))
        
        # check the number of the scale quantities
        if scaleQuantities and len(scaleQuantities) != ds.data.ndim:
            raise Exception("The number of scale quantities must be equal to the number of dimensions.")

        # check the number of the scale units
        if scaleUnits and len(scaleUnits) != ds.data.ndim:
            raise Exception("The number of scale units must be equal to the number of dimensions.")
        
        for ri in range(ds.data.ndim):
            if dsobj.dims[ri]:
                sobj = dsobj.dims[ri][0]
                s = _create_dataset(sobj)
                s.is_scale = True
                s.scale_name = dsobj.dims[ri].keys()[0]
                ds.scales[ri] = s
                
                # check the quantity
                if scaleQuantities and scaleQuantities[ri] and scaleQuantities[ri] != s.quantity:
                    raise Exception("The scale for dimension %d of dataset '%s' in '%s' has the wrong quantity. Expected '%s' but was '%s'." % (ri+1, datasetname, filename, scaleQuantities[ri], s.quantity))
                
                # check the unit
                if scaleUnits and scaleUnits[ri] and scaleUnits[ri] != s.unit:
                    raise Exception("The scale for dimension %d of dataset '%s' in '%s' has the wrong unit. Expected '%s' but was '%s'." % (ri+1, datasetname, filename, scaleUnits[ri], s.unit))
        
        return ds

def save(filename, group):
    ''' save an SDF group to a file '''
    with h5py.File(filename, 'w') as f:
        _write_group(f, group)
            
def _write_group(f, g):
    for subgroup in g.groups:
        _write_group(f, subgroup)

    if isinstance(g.comment, basestring):
        f.attrs['COMMENT'] = np.string_(g.comment.encode('utf8'))
    
    for key, value in g.attributes.items():
        if not isinstance(value, np.string_) and isinstance(value, basestring):
            value = np.string_(value.encode('utf8'))   
        f.attrs[key] = value
        
    ''' resort the sequence of datasets, so that scale datasets are written firstly. '''
        
    resorted_ds = [ds for ds in g.datasets if ds.is_scale == True] + [ds for ds in g.datasets if ds.is_scale == False]
    
    #for ds in g.datasets:
    #    _write_dataset(f, ds)
    for ds in resorted_ds:
        _write_dataset(f, ds)
    
            
def _write_dataset(f, ds):
    
    f[ds.name] = ds.data
    dsobj = f[ds.name]
    
    if ds.comment:
        dsobj.attrs['COMMENT'] = np.string_(ds.comment)
        
    if ds._display_name:
        dsobj.attrs['DISPLAY_NAME'] = np.string_(ds.display_name)
    
    if ds.quantity:
        dsobj.attrs['QUANTITY'] = np.string_(ds.quantity)
    
    if ds.unit:
        dsobj.attrs['UNIT'] = np.string_(ds.unit)
    
    if ds.display_unit != ds.unit:
        dsobj.attrs['DISPLAY_UNIT'] = np.string_(ds.display_unit)
        
    if ds.is_scale:
        dimname = ds.scale_name
        if dimname is None:
            dimname = ''
        dsid = dsobj.id
        h5py.h5ds.set_scale(dsid, dimname)
    
    for ri in range(len(ds.scales)):
        s = ds.scales[ri]
        sobj = f[s.name]
        scale_name = s.scale_name
        if scale_name is None:
            scale_name = ''
        dsobj.dims.create_scale(sobj, scale_name)
        dsobj.dims[ri].attach_scale(sobj)
        
    return dsobj

def _create_dataset(dsobj):
    name = os.path.split(dsobj.name)[1]
    ds = Dataset(name, data=dsobj.value)
    
    for attr in dsobj.attrs:
        if attr == 'COMMENT':
            ds.comment = dsobj.attrs[attr]
        elif attr == 'DISPLAY_NAME':
            ds.display_name = dsobj.attrs[attr]
        elif attr == 'QUANTITY':
            ds.quantity = dsobj.attrs[attr]
        elif attr == 'UNIT':
            ds.unit = dsobj.attrs[attr]
        elif attr == 'DISPLAY_UNIT':
            ds.display_unit = dsobj.attrs[attr]
        elif attr == 'NAME':
            ds.scale_name = dsobj.attrs[attr]
        elif attr == 'CLASS' and dsobj.attrs[attr] == 'DIMENSION_SCALE':
            ds.is_scale = True
        elif attr == 'REFERENCE_LIST':
            pass
        elif attr == 'DIMENSION_LIST':
            pass        
        else:
            ds.attributes[attr] = dsobj.attrs[attr]
            
    ds.scales = [None] * ds.data.ndim
            
    return ds


def load_sdf(filename, group='/'):
    ''' load the whole sdf file in memory as a group instance'''
    ds_obj_list = []
    ds_list = []
    group_attrs = {}
    group_name = ''
    comment = ''
    with h5py.File(filename, 'r') as f:
        group_attrs = {key: f.attrs[key] for key in f.attrs.keys() if key != 'COMMENT'}
        comment = f.attrs.get('COMMENT')
        for ds_name in f.keys():
            ds_obj_list.append(f[ds_name])
        ds_list = [_create_dataset(dsobj) for dsobj in ds_obj_list]
        for ds in ds_list:
            if ds.is_scale == False:
                dsobj = ds_obj_list[ds_list.index(ds)]
                for ri in range(ds.data.ndim):
                    
                    if dsobj.dims[ri]:
                        sobj = dsobj.dims[ri][0]
                        index = ds_obj_list.index(sobj)
                        if index < 0:
                            raise Exception('load error!')
                        ds.scales[ri] = ds_list[index]
            else:
                ds.scales = []
            
    g = Group(name=group, comment=comment,
                      attributes=group_attrs,
                      datasets=ds_list)
    return g
    
    