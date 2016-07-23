import copy
import sdf
import math


def match_name(ds, substr):
    print "substr", substr
    print "ds.name", ds.name
    print substr in ds.name
    return substr in ds.name


def merge_peak_cont(sde_peak, sde_cont, metatask_data):
    hack_datasets = get_hack_datasets_function(metatask_data)
    hack_attrib = get_hack_attrib_function(metatask_data)
    sdf_file = sde_peak.merge_and_save_sdf(sde_cont, hack_datasets, hack_attrib)
    return sdf_file


def get_hack_datasets_function(metatask_data):
    def hack_datasets(datasets):
        datasets = modify_list(datasets, from_celsius, lambda x: match_name(x, "T_P"))
        datasets = modify_list(datasets, from_rpm, lambda x: match_name(x, "w_P"))
        hv_consumption_str = metatask_data["taskGenerator"]["arguments"]["constant"][
            "parameterOfFunction"]["testArguments"]["parameters"].get("HV_consumption")
        if hv_consumption_str is None:
            consumption = 0
        else:
            consumption = float(hv_consumption_str)

        ds_consumption = sdf.Dataset('HV_Consumption', comment='High voltage consumption',
                                     data=consumption, display_name='HV_Consumption',
                                     quantity='Power', unit='W', display_unit='W')
        datasets.append(ds_consumption)

        w_eck = get_info(metatask_data, 'n_eck') / 60 * 2 * math.pi
        ds_w_eck = sdf.Dataset('w_char', comment='Characteristic speed for the electric machine',
                               data=w_eck, display_name='w_char',
                               quantity='AngularVelocity', unit='rad/s', display_unit='rpm')
        datasets.append(ds_w_eck)
        w_max = get_info(metatask_data, 'n_max') / 60 * 2 * math.pi
        ds_w_max = sdf.Dataset('w_max', comment='Maximal speed for the electric machine',
                               data=w_max, display_name='w_max',
                               quantity='AngularVelocity', unit='rad/s', display_unit='rpm')
        datasets.append(ds_w_max)
        return datasets
    return hack_datasets


def get_info(metatask_data, name):
    val_str = metatask_data["taskGenerator"]["arguments"]["constant"]["parameterOfFunction"]["info"].get(name)
    if val_str is None:
        val = 0
    else:
        val = float(val_str)
    return val


def get_hack_attrib_function(metatask_data):
    def hack_attrib(attribs):
        attribs['buildInfo'] = str(pretty_print_build_info(metatask_data))
        return attribs
    return hack_attrib


def pretty_print_build_info(metatask_data):
    build_infos = metatask_data["taskGenerator"]["arguments"]["constant"]["buildingInfo"]
    info_str = u""
    for key in build_infos.keys():
        info_str = info_str + key + u": ["
        for value in recursive_get_dict(build_infos[key], u'value'):
            info_str = info_str + value.split('.')[-1]
            info_str = info_str + u' / '
        info_str = info_str + u"]; "
    return info_str


def from_celsius(ds):
    new_ds = copy.copy(ds)
    new_ds.data = 273.15 + ds.data
    return new_ds


def from_rpm(ds):
    new_ds = copy.copy(ds)
    new_ds.data = ds.data * (2 * 3.1415926535 / 60)
    return new_ds


def modify_list(list_old, modify_function, check_function):
    list_matching = [modify_function(elem) for elem in list_old if check_function(elem)]
    list_new = [elem for elem in list_old if not check_function(elem)]
    return list_new + list_matching


def recursive_get_dict(d, key):
    if key in d:
        yield d[key]
    elif isinstance(d, dict):
        for k in d.keys():
            for result in recursive_get_dict(d[k], key):
                yield result

if __name__ == "__main__":
    import pickle
    import os
    import json
    _dir = os.path.dirname(os.path.abspath(__file__))

    fname_metatask_peak = os.path.join(_dir, 'tests', 'saved_metatask_peak.json')
    fname_metatask_cont = os.path.join(_dir, 'tests', 'saved_metatask_cont.json')
    fname_sde_peak = os.path.join(_dir, 'tests', 'result_1.sde')
    fname_sde_cont = os.path.join(_dir, 'tests', 'result_2.sde')

    with open(fname_metatask_peak, 'r') as f:
        metatask_peak = json.load(f)
    with open(fname_metatask_cont, 'r') as f:
        metatask_cont = json.load(f)
    with open(fname_sde_peak, 'r') as f:
        result_peak = pickle.load(f)
    with open(fname_sde_cont, 'r') as f:
        result_cont = pickle.load(f)

    sdf_merged = merge_peak_cont(result_peak, result_cont, metatask_peak)
