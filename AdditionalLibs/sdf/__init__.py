import os
import numpy as np
import h5py
from units import convert_unit
import re

__version__ = '0.1.0'

class _StructuralElement(object):
    """ Base class for SDF Groups and Datasets  """
    
    def __init__(self, name, comment=None, attributes=dict()):
        self.name = name
        self.comment = comment
        self.attributes = attributes
        
class Group(_StructuralElement):
    """ SDF Group """
    
    def __init__(self, name, comment=None, attributes=dict(), datasets=[]):
        _StructuralElement.__init__(self, name, comment, attributes)
        self.datasets = datasets
    
class Dataset(_StructuralElement):
    """ SDF Dataset """
    
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
                 scales=[]
                 ):
        _StructuralElement.__init__(self, name, comment, attributes)
        
        self.data = data
        self._display_name = display_name
        self.quantity = quantity
        self.unit = unit
        self._display_unit = display_unit
        self.is_scale = is_scale
        self.scale_name = scale_name
        self.scales = scales
        
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
    
    assert isinstance(obj, _StructuralElement)
    
    if type(obj) is Group:
        errors = errors + _validate_group(obj, is_root=True)
    
    if type(obj) is Dataset:
        errors = errors + _validate_dataset(obj)
    
    return errors

def _validate_group(group, is_root=False):
    errors = []
    
    if not is_root and not re.match(r'[A-Za-z]\w+', group.name):
        errors = errors +  ['Object names must only contain letters, digits and underscores ("_") and must start with a letter']
    
    for ds in group.datasets:
        errors = errors + _validate_dataset(ds)
    
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
        
def load(filename, datasetname):
        
    with h5py.File(filename, 'r') as f:
        dsobj = f[datasetname]
        
        ds = _create_dataset(dsobj)
            
        for ri in range(ds.data.ndim):
            if dsobj.dims[ri]:
                sobj = dsobj.dims[ri][0]
                s = _create_dataset(sobj)
                s.is_scale = True
                s.scale_name = dsobj.dims[ri].keys()[0]
                ds.scales[ri] = s
        
        return ds
    
def load_all(filename):
    ds_list = []
    with h5py.File(filename, 'r') as f:
        names = f.keys()
        for datasetname in names:
            dsobj = f[datasetname]
            ds = _create_dataset(dsobj)
            for ri in range(ds.data.ndim):
                if dsobj.dims[ri]:
                    sobj = dsobj.dims[ri][0]
                    s = _create_dataset(sobj)
                    s.is_scale = True
                    s.scale_name = dsobj.dims[ri].keys()[0]
                    ds.scales[ri] = s
            ds_list.append(ds)
    return_ds_list = []
    for ds_index, ds in enumerate(ds_list):
        scale_names = [scale.name for scale in ds.scales if scale != None]
        scales = [ds for ds in ds_list if ds.name in scale_names]
        ds.scales = scales
        return_ds_list.append(ds)
    return return_ds_list
            
    


def save(filename, group):
    with h5py.File(filename, 'w') as f:
        if(group.comment != None):
            f.attrs['COMMENT'] = np.string_(group.comment)
        
        for key, value in group.attributes.items():
            if type(value) is str:
                value = np.string_(value)   
            f.attrs[key] = value
        scales = [ds for ds in group.datasets if ds.is_scale]
        non_scales = [ds for ds in group.datasets if not ds.is_scale]
        for ds in scales + non_scales :
            print "ds.name", ds.name
            print "ds.is_scale", ds.is_scale
            print "ds.scales", [scale.name for scale in ds.scales]
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
       
    for ri in range(len(ds.scales)):
        s = ds.scales[ri]
        sobj = f[s.name]
        dsobj.dims.create_scale(sobj, s.scale_name)
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
