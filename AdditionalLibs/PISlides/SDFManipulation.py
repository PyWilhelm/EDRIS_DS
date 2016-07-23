#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sdf
import numpy as np
import copy

class SplittableDataset(object):
    def __init__(self, sdf_ds=None):
        self._dataset = None
        self._scales = []
        self.dataset = sdf_ds

    @property
    def dataset(self):
        return self._dataset

    @dataset.setter
    def dataset(self, value):
        if value is not None:
            new_scales = []
            for scale in value.scales:
                scale.scales = []
                new_scales.append(scale)
            value.scales = new_scales
        self._dataset = value


    def load_ds_and_scales(self, filename, dsname):
        ds = sdf.load(filename, dsname)
        self.dataset = ds

    def sub_dataset(self, sub_scales_name, non_scales_value_dict):

        sub_scales = [scale for scale in self._dataset.scales if scale.name in sub_scales_name]
        #new_sdf._actual_scales = sub_scales
        
        new_ds = copy.deepcopy(self._dataset)
        nd_array = new_ds.data
        new_ndarray = self._extract_dimensions(nd_array, sub_scales, non_scales_value_dict)

        new_ds.data = new_ndarray 
        new_ds.scales = sub_scales
        return new_ds


    def _extract_dimensions(self, nd_array, sub_scales, non_scales_value_dict):
        indexes_sub_scales = [self._get_scale_index_from_name(scale.name) for scale in sub_scales]
        indexes_non_scales = [self._get_scale_index_from_name(name) for name in non_scales_value_dict.keys()]
        indexes_tuple = ()
        for i, scale in enumerate(self._dataset.scales):
            if i in indexes_sub_scales:
                indexes_tuple = indexes_tuple + (slice(None, None),)
            elif i in indexes_non_scales:
                value = non_scales_value_dict[self._dataset.scales[i].name]
                try:
                    value = convert(value)
                except:
                    pass
                indexes_tuple = indexes_tuple + (SplittableDataset._get_value_index_at_scale(scale, value),)
            else:
                raise Exception('not cannot find the scale in input ' + scale.name + ':' + str(scale.data))
        nd_array_sliced = nd_array[indexes_tuple]
        if len(indexes_sub_scales) == 2:
            if (indexes_sub_scales[0] > indexes_sub_scales[1]):
                nd_array_sliced = np.transpose(nd_array_sliced) 
        return nd_array_sliced 

    @staticmethod
    def _get_value_index_at_scale(scale, value):
        item_index = np.where(scale.data==value)
        item_index_rough = np.where(abs(scale.data-value)<1e-5)
        if (item_index is not None) and (item_index[0].size > 0): 
            return item_index[0][0]
        elif (item_index_rough is not None) and (item_index_rough[0].size > 0): 
            return item_index_rough[0][0]
        else:
            raise Exception('not cannot find the value ' + str(value) + " in scale " + scale.name + ':' + str(scale.data))

    def _get_scale_index_from_name(self, scale_name):
        for i, scale in  enumerate(self._dataset.scales):
            if scale_name == scale.name:
                return  i
        raise Exception('not cannot find the scale with name' + scale_name)


if __name__ == "__main__":
    
    sds = SplittableDataset()
    sds.load_ds_and_scales('test.sdf', '/P_cont')
    ds = sds.sub_dataset(['RCI_P_cont', 'T_P_cont'], {'w_P_cont' :314.159265352})


    # create a group
    g = sdf.Group(name='/',
                  comment='my comment',
                  attributes={},
                  datasets=ds.scales + [ds]  )
    
    # save the group
    sdf.save('test_2.sdf', g)

