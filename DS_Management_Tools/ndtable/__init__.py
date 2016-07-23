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
import ctypes
from ctypes import c_double, c_void_p, c_int
import numpy as np

# prepend the path of the DLLs to os.environ['PATH']
def _add2path():
    import os
    if os.name != 'nt':
        return
    try:
        path = os.path.join(os.path.abspath(os.path.dirname(__file__)))
        if path not in os.environ.get('PATH', ''):
            os.environ['PATH'] = os.pathsep.join((path, os.environ.get('PATH', '')))
    except Exception:
        pass

_add2path()
del _add2path

_ndtable = ctypes.cdll.LoadLibrary('ndtable')

# PYTHON_API ModelicaNDTable_h create_table(int ndims, const int *dims, const double *data, const double **scales) {
_create_table = _ndtable.create_table
_create_table.argtypes = [c_int, ctypes.c_void_p, ctypes.c_void_p, (ctypes.c_void_p * 32)]
_create_table.restype = c_void_p

# PYTHON_API int evaluate(
#     ModelicaNDTable_h table, 
#     int ndims, 
#     const double **params, 
#     ModelicaNDTable_InterpMethod_t interp_method,
#     ModelicaNDTable_ExtrapMethod_t extrap_method,
#     int nvalues,
#     double *value);
_evaluate = _ndtable.evaluate
_evaluate.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_void_p]
_evaluate.restype = ctypes.c_int

# PYTHON_API int evaluate_derivative(
#     ModelicaNDTable_h table, 
#     int nparams, 
#     const double params[],
#     const double delta_params[],
#     ModelicaNDTable_InterpMethod_t interp_method,
#     ModelicaNDTable_ExtrapMethod_t extrap_method, 
#     double *value);
_evaluate_derivative = _ndtable.evaluate_derivative
_evaluate_derivative.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_void_p]
_evaluate_derivative.restype = ctypes.c_int

_close_table = _ndtable.close_table
_close_table.argtypes = [ctypes.c_void_p]


class NDTable(object):
    """ 
        An n-dimensional lookup table
    
        Attributes
        ----------
        data : ndarray
            The values to interpolate.
        scales : tuple of ndarrays
            The scales for `data`. There must be one scale for every dimension of `data`. 
            The values must be strictly monotonic increasing.
    """
    
    _interp_methods = {'nearest': 1, 'linear': 2, 'akima': 3}
    _extrap_methods = {'hold': 1, 'linear': 2}
    
    def __init__(self, data, scales):
        
        # convert the arguments to float64 arrays
        to_double = lambda v: np.asanyarray(v, dtype=np.float64, order='C')
        data = to_double(data)
        scales = map(to_double, scales)

        # check the arguments
        assert data.ndim <= 32, 'Max. number of dimensions is 32'
        assert len(scales) == data.ndim, 'The number of scales must match the number of dimensions'
        for i, scale in enumerate(scales):
            assert np.all(np.isfinite(scale)), 'The scale for dimension %d is not finite' % i
            assert scale.ndim == 1, 'Scales must be one-dimensional'
            assert scale.size == data.shape[i], 'The scale for dimension %d does not match the shape of data' % i
        
        dims = np.asarray(data.shape, np.int32)
        scales_ = (ctypes.c_void_p * 32)()
        for i, scale in enumerate(scales):
            scales_[i] = scale.ctypes.get_as_parameter()
        self._table = _create_table(ctypes.c_int(data.ndim), dims.ctypes.get_as_parameter(), data.ctypes.get_as_parameter(), scales_)
        
        # save close function from garbage collection
        self._close_table = _close_table

    def evaluate(self, points, interp='linear', extrap='hold'):
        """
            Evaluate the lookup table at the coordinates in `points`.
            
            Returns an array of the same shape as the coordinates in `points`.
            
            Parameters
            ----------
            points : tuple of ndarrays
                The coordinates of the points to evaluate.
            interp : string, optional
                The interpolation method (one of 'nearest', 'linear' or 'akima')
                Default is 'linear'.
            extrap : string, optional
                The extrapolation method (one of 'hold' or 'linear')
                Default is 'hold'.
        
            Returns
            -------
            samples : ndarray
                The evaluated points.
        
            Example
            --------
            >>> import numpy as np
            >>> import ndtable
            >>> x = y = np.linspace(-1, 1, 3)
            >>> x, y
                (array([-1.,  0.,  1.]), array([-1.,  0.,  1.]))
            >>> X, Y = np.meshgrid(x, y, indexing='ij')
            >>> Z = X * Y
            >>> Z
                array([[ 1., -0., -1.],
                       [-0.,  0.,  0.],
                       [-1.,  0.,  1.]])
            >>> lut = ndtable.NDTable(Z, (x, y))
            >>> x2 = y2 = np.linspace(-1, 1, 5)
            >>> x2, y2
                (array([-1. , -0.5,  0. ,  0.5,  1. ]), array([-1. , -0.5,  0. ,  0.5,  1. ]))
            >>> X2, Y2 = np.meshgrid(x2, y2, indexing='ij')
            >>> Z2 = lut.evaluate((X2, Y2))
            >>> Z2
                array([[ 1.  ,  0.5 ,  0.  , -0.5 , -1.  ],
                       [ 0.5 ,  0.25,  0.  , -0.25, -0.5 ],
                       [ 0.  ,  0.  ,  0.  ,  0.  ,  0.  ],
                       [-0.5 , -0.25,  0.  ,  0.25,  0.5 ],
                       [-1.  , -0.5 ,  0.  ,  0.5 ,  1.  ]])
        
        """

        points = list(points)
        
        for i, _ in enumerate(points):
            points[i] = np.asarray(points[i], np.float64)

        shape = points[0].shape

        for p in points[1:]:
            assert p.shape == shape, 'The arrays in points must have the same shape'
        
        assert interp in self._interp_methods, 'Unknown interpolation method "%s"' % interp
        assert extrap in self._extrap_methods, 'Unknown extrapolation method "%s"' % extrap
        
        interp_method = c_int(self._interp_methods[interp])
        extrap_method = c_int(self._extrap_methods[extrap])
        
        values = np.empty(shape)
        params = (ctypes.c_void_p * len(points))()
        for i, param in enumerate(points):
            params[i] = param.ctypes.get_as_parameter()
        
        ret = _evaluate(ctypes.c_void_p(self._table), 
                        c_int(len(params)),
                        params, 
                        interp_method, 
                        extrap_method,
                        c_int(values.size),
                        values.ctypes.get_as_parameter())
        
        assert ret == 0, 'An error occurred during interpolation'
        
        return values

    def evaluate_derivative(self, points, deltas, interp='linear', extrap='hold'):

        points = list(points)
        deltas = list(deltas)
        
        for i, _ in enumerate(points):
            points[i] = np.asarray(points[i], np.float64)
            deltas[i] = np.asarray(deltas[i], np.float64)

        shape = points[0].shape

        for p in points[1:]:
            assert p.shape == shape, 'The arrays in points must have the same shape'
        
        assert interp in self._interp_methods, 'Unknown interpolation method "%s"' % interp
        assert extrap in self._extrap_methods, 'Unknown extrapolation method "%s"' % extrap
        
        interp_method = c_int(self._interp_methods[interp])
        extrap_method = c_int(self._extrap_methods[extrap])
        value = c_double()
        
        out = np.empty(shape)
        params = np.empty(len(points))
        delta_params = np.empty(len(points))
        
        for index in np.ndindex(shape):
            for i, point in enumerate(points):
                params[i] = point[index]
            for i, delta in enumerate(deltas):
                delta_params[i] = delta[index]
                
            _evaluate_derivative(ctypes.c_void_p(self._table), 
                                 c_int(params.size), 
                                 params.ctypes.get_as_parameter(), 
                                 delta_params.ctypes.get_as_parameter(),
                                 interp_method, 
                                 extrap_method, 
                                 ctypes.byref(value))
            out[index] = value.value
            
        return out

    def __del__(self):
        self._close_table(self._table)
