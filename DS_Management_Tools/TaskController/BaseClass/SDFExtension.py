#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sdf
import json
import logging
import copy
import types
import time
import os
import pickle
import numpy as np
from conf import __conf__


def convert(inputdata):
    if isinstance(inputdata, dict):
        return dict((convert(key), convert(value)) for key, value in inputdata.iteritems())
    elif isinstance(inputdata, list):
        return [convert(element) for element in inputdata]
    else:
        if not type(inputdata) in [types.FloatType, types.IntType, types.BooleanType]:
            inputdata = inputdata.decode('utf-8', 'ignore')
        try:
            inputdata = float(inputdata)
        except:
            pass
        return inputdata


class SDFExtension(object):

    def __init__(self, scale_method):
        self._scale_method = scale_method
        self._actual_scales = []
        self._sdf_scales = []
        self._result_datasets = []
        self._attributes = dict()
        self._name_mapping = dict()

    def __getitem__(self, name):
        rv_list = [ds for ds in self._result_datasets if ds.name == name]
        if len(rv_list) > 0:
            return rv_list[0].data
        else:
            raise Exception('key %s: not found' % name)

    def get_scale(self, name):
        rv_list = [ds for ds in self._actual_scales if ds.name == name]
        if len(rv_list) > 0:
            return rv_list[0].data
        else:
            raise Exception('key %s: not found' % name)

    def sub_sdf(self, sub_scales_name, non_scales_value_dict):
        new_sdf = SDFExtension('full')
        sub_scales = [scale for scale in self._actual_scales if scale.name in sub_scales_name]
        new_sdf._actual_scales = sub_scales
        new_sdf._sdf_scales = [
            scale for scale in self._sdf_scales if scale.name.replace('scale_index_', '') in sub_scales_name]
        for ds in self._result_datasets:
            ds = copy.deepcopy(ds)
            nd_array = ds.data
            new_ndarray = self._extract_dimensions(nd_array, sub_scales, non_scales_value_dict)
            ds.data = new_ndarray
            new_sdf._result_datasets.append(ds)
        return new_sdf

    def _extract_dimensions(self, nd_array, sub_scales, non_scales_value_dict):
        indexes_sub_scales = [self._get_scale_index_from_name(scale.name) for scale in sub_scales]
        indexes_non_scales = [self._get_scale_index_from_name(name) for name in non_scales_value_dict.keys()]
        indexes_tuple = ()
        for i, scale in enumerate(self._actual_scales):
            if i in indexes_sub_scales:
                indexes_tuple = indexes_tuple + (slice(None, None),)
            elif i in indexes_non_scales:
                value = non_scales_value_dict[self._actual_scales[i].name]
                try:
                    value = convert(value)
                except:
                    pass
                indexes_tuple = indexes_tuple + (SDFExtension._get_value_index_at_scale(scale, value),)
            else:
                raise Exception('not cannot find the scale in input ' + scale.name + ':' + str(scale.data))
        nd_array_sliced = nd_array[indexes_tuple]
        if len(indexes_sub_scales) == 2:
            if (indexes_sub_scales[0] > indexes_sub_scales[1]):
                nd_array_sliced = np.transpose(nd_array_sliced)
        return nd_array_sliced

    @staticmethod
    def _get_value_index_at_scale(scale, value):
        item_index = np.where(scale.data == value)
        if (item_index is not None) and (item_index[0].size > 0):
            return item_index[0][0]
        else:
            raise Exception('not cannot find the value' + str(value) +
                            " in scale " + scale.name + ':' + str(scale.data))

    def _get_scale_index_from_name(self, scale_name):
        for i, scale in enumerate(self._actual_scales):
            if scale_name == scale.name:
                return i
        raise Exception('not cannot find the scale with name' + scale_name)

    @property
    def actual_scales(self):
        return self._actual_scales

    @property
    def result_datasets(self):
        return self._result_datasets

    def set_scales(self, scales=[{'name': 'scalename', 'value': [], 'comment': '',
                                  'quantity':'', 'unit': '', 'display_unit': ''}]):
        _scales = []
        for scale in scales:
            attributes = None
            self.add_name_mapping(scale)
            if scale.get('build') == True:
                attributes = {i: json.dumps(value) for i, value in enumerate(scale['value'])}
                _scales.append(sdf.Dataset(scale['name'], unit=scale.get('unit'), comment='building_info',
                                           data=np.array(attributes.keys()),
                                           display_unit=scale.get('displayUnit'), quantity=scale.get('quantity'),
                                           display_name=scale['name'], scale_name=scale['name'], attributes=attributes,
                                           is_scale=True))
            else:
                _scales.append(sdf.Dataset(scale['name'], unit=scale.get('unit'), data=np.array(scale['value']),
                                           display_unit=scale.get('displayUnit'), quantity=scale.get('quantity'),
                                           comment=scale.get('comment'),
                                           display_name=scale['name'], scale_name=scale['name'],
                                           is_scale=True))
        self._actual_scales = _scales
        if self._scale_method.find('full') >= 0:
            self._full_factorial()
        elif self._scale_method.find('simple') >= 0:
            self._simple_variation()
        elif self._scale_method.find('changeone') >= 0:
            self._changeone_factorial()

    def set_result_dataset(self, result_parameters):
        new_value_array = lambda obj: np.zeros([scale.data.size
                                                for scale in obj._sdf_scales])\
            if len(obj._sdf_scales) > 0 else np.zeros([1])
        for r in result_parameters:
            self.add_name_mapping(r)
            self._result_datasets.append(sdf.Dataset(r['signalName'], unit=r.get('unit'), data=new_value_array(self),
                                                     attributes=self._attributes,
                                                     display_unit=r.get('displayUnit'), quantity=r.get('quantity'),
                                                     comment=r.get('comment'),
                                                     display_name=r['signalName'], scales=self._sdf_scales))

    def add_name_mapping(self, sdf_parameter_struct):

        if 'name' in sdf_parameter_struct:
            key_name = sdf_parameter_struct['name']
        elif 'signalName' in sdf_parameter_struct:
            key_name = sdf_parameter_struct['signalName']
        else:
            raise Exception(
                "the following sdf_parameter_struct structure don't have proper keys " + str(sdf_parameter_struct))

        if 'sdfName' in sdf_parameter_struct:
            self._name_mapping[key_name] = sdf_parameter_struct['sdfName']
        elif 'signalName' in sdf_parameter_struct:
            self._name_mapping[key_name] = sdf_parameter_struct['signalName']
        elif 'name' in sdf_parameter_struct:
            self._name_mapping[key_name] = sdf_parameter_struct['name']
        else:
            raise Exception(
                "the following sdf_parameter_struct structure don't have proper keys " + str(sdf_parameter_struct))

    def add_value(self, variable_data, result_data):
        if variable_data is None or variable_data == []:
            index = 0
        else:
            index = self._get_index(variable_data)
        logging.info('index' + str(index) + str(variable_data))
        for key in result_data.keys():
            match_dataset = [ds for ds in self._result_datasets if ds.name == key][0]
            # if self._scale_method.find('changeone') >= 0 and max(index) == 0:
            # match_dataset.data[0: ] = result_data[key]
            # else:
            match_dataset.data[index] = result_data[key]

    def save(self):
        # attributes = {'generate_method': self._scale_method.decode('utf-8', 'ignore')}
        name = os.path.join(__conf__['outputPath'], 'tmp_sdf', 'report-%f.sde' % (time.time(),))
        with open(name, 'w') as f:
            pickle.dump(self, f)
        return name

    def get_sdf_datasets(self):
        datasets = []
        actual_scales = []
        for dataset in copy.deepcopy(self._actual_scales):
            dataset.name = self._name_mapping[dataset.name]
            dataset.display_name = dataset.name
            dataset.scale_name = dataset.name
            actual_scales.append(dataset)
            datasets.append(dataset)

        for dataset in copy.deepcopy(self._result_datasets):
            dataset.name = self._name_mapping[dataset.name]
            dataset.display_name = dataset.name
            dataset.scales = actual_scales
            datasets.append(dataset)
        return datasets

    def save_as_sdf(self):
        # TODO: plausibility checks

        datasets = self.get_sdf_datasets()
        _group = sdf.Group(name='/', comment='my comment',
                           attributes=self._attributes, datasets=datasets)

        filename = os.path.join(__conf__['outputPath'], 'tmp_sdf', 'report-%f.sdf' % (time.time(),))
        sdf.save(filename, _group)
        return filename

    def merge_and_save_sdf(self, other_sde, modify_ds=lambda x: x, modify_attrib=lambda x: x, comment=""):
        datasets_new = modify_ds(self.get_sdf_datasets() + other_sde.get_sdf_datasets())
        attributes = copy.deepcopy(self._attributes)
        attributes.update(other_sde._attributes)
        attributes_new = modify_attrib(attributes)

        _group = sdf.Group(name='/', comment=comment,
                           attributes=attributes_new, datasets=datasets_new)

        filename = os.path.join(__conf__['outputPath'], 'tmp_sdf', 'report-%f.sdf' % (time.time(),))
        sdf.save(filename, _group)
        return filename

    @staticmethod
    def load(filename):
        with open(filename, 'r') as f:
            return pickle.load(f)

    def lookup(self, variable_data):
        index = self._get_index(variable_data)
        return {ds.name: ds.data[index] for ds in self._result_datasets}

    def slice(self, variable_data):
        if self._scale_method.find('full') < 0:
            raise Exception('slice function can be used only for full factorial')

    def _full_factorial(self):
        self._sdf_scales = [sdf.Dataset('scale_index_' + scale.name, comment='',
                                        data=np.array(range(scale.data.size)),
                                        display_name='scale_index_' + scale.name,
                                        scale_name='scale_index_' + scale.name,
                                        is_scale=True)
                            for scale in self._actual_scales]

    def _simple_variation(self):
        if len(self._actual_scales) == 0:
            return
        scale_length = self._actual_scales[0].data.size
        simple_scale = sdf.Dataset('scale_index', comment='', data=np.array(range(scale_length)),
                                   display_name='scale_index', scale_name='scale_index',
                                   is_scale=True)
        self._sdf_scales = [simple_scale]

    def _changeone_factorial(self):
        scale_length = max([scale.data.size for scale in self._actual_scales])
        changeone_length_scale = sdf.Dataset('scale_length_index', comment='',
                                             data=np.array(range(scale_length)),
                                             display_name='scale_length_index',
                                             scale_name='scale_length_index',
                                             is_scale=True)
        changeone_depth_scale = sdf.Dataset('scale_depth_index', comment='',
                                            data=np.array(range(len(self._actual_scales))),
                                            display_name='scale_depth_index',
                                            scale_name='scale_depth_index',
                                            is_scale=True)
        self._sdf_scales = [changeone_length_scale, changeone_depth_scale]

    def _get_index(self, variable_data):
        with open('variable.json', 'a+') as f:
            f.write(json.dumps(variable_data))
        if variable_data is None or variable_data == []:
            return (0,)
        index = []
        for var in variable_data:
            match_scales = [scale for scale in self._actual_scales if scale.name == var['name']]
            if len(match_scales) == 0 or len(match_scales) > 1:
                logging.error('not match the correct scale!' + str(match_scales))
                raise Exception('not match the correct scale!' + str(match_scales))
            match_scale = match_scales[0]
            if var.get('build'):
                keys = []
                for key in match_scale.attributes.keys():
                    if match_scale.attributes[key] == json.dumps(var['value']):
                        keys.append(key)
                index.append(np.array(keys))
            else:
                logging.info('value' + str(var['value']))
                logging.info('match_scale' + str(match_scale.data))
                index.append(np.where(match_scale.data == var['value'])[0])
        logging.info('index first' + str(index))

        if self._scale_method.find('full') >= 0:
            index = tuple([i[0] for i in index])
        elif self._scale_method.find('simple') >= 0:
            get_intersection = lambda list1, list2: [i for i in list1 if i in list2]
            intersection_index = reduce(get_intersection, index)
            if len(intersection_index) != 1:
                logging.error('not macht the correct index!' + str(variable_data))
                raise Exception('not macht the correct index!' + str(variable_data))
            else:
                index = (intersection_index[0],)
        elif self._scale_method.find('changeone') >= 0:
            if max(index) == 0:
                index = (0, 0)
            else:
                index = [i[0] for i in index]
                index = (max(index), index.index(max(index)))
            with open('index.json', 'a+') as f:
                f.write(json.dumps(variable_data))
                f.write(str(index))
                f.write('\n')

        return index
