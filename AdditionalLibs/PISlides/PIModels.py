#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import math
import sdf
import SDFManipulation as sdfm
import PIModelData, PIMVC 

get_peak_name = lambda x : '/' + x + "_peak" 

class PIMasterModel(object):
    def __init__(self, filename, ymax=None):
        self.filename = filename

        n_eck = get_rpm_data(self.filename)[0]
        self.base_op = [None] * 3
        self.base_op[0] = dict(t = 10, n = n_eck,  RCI = 10, T = 10, SoH = 100, mode = "mot")
        self.base_op[1] = dict(t = 10, n = n_eck,  RCI = 80, T = 0, SoH = 100, mode = "mot")
        self.base_op[2] = dict(t = 150, n = n_eck,  RCI = 50, T = 25, SoH = 100, mode = "mot")
        self.ymax = ymax
        self._update_base_op()
        self._check_data_consistency()
    
    def _update_base_op(self):
        pass

    def _check_data_consistency(self):
        pass

    def plot_data(self):
        positions = PIModelData.get_plot_positions()
        plot_data_list = [None] * 5

        bop = self.base_op

        [unused_n_eck, n_min_star, n_max] = get_rpm_data(self.filename)

        # AP 1
        plot_data_list[0] = get_pi_plot_data(self.filename, 'n', bop[0], star_position=[bop[0]['n'], n_min_star, n_max, ], ymax=self.ymax)
        plot_data_list[1] = get_pi_plot_data(self.filename, 'RCI', bop[0], star_position=[bop[0]['RCI'], 50, 100], ymax=self.ymax)

        # AP 2
        plot_data_list[2] = get_pi_plot_data(self.filename, 't', bop[2], star_position=[bop[2]['t'], 10, 30,], ymax=self.ymax)

        # AP 3
        plot_data_list[3] = get_pi_plot_data(self.filename, 'T', bop[1], star_position=[bop[1]['T'], 25, 40], ymax=self.ymax)
        plot_data_list[4] = get_pi_plot_data(self.filename, 'RCI', bop[1], star_position=[bop[1]['RCI'], 50, 100], ymax=self.ymax)


        return [dict(plot_data=plot_data, position=position) 
                for plot_data, position in zip(plot_data_list, positions)]

    def title_data(self):
        return "Dummy title"

    def hvConsumption_data(self):
        return get_consumption_data(self.filename)

    def ap_data(self):
        positions = PIModelData.get_master_aps_positions()
        return [dict(value=value, position=position) for value, position in zip(self.base_op, positions)]

def get_consumption_data(filename):
    return get_x(filename, 'HV_Consumption')/1000

def get_rpm_data(filename):
    n_eck = get_x(filename, 'w_char') 
    n_min_star = int(n_eck / 1000 / 2) * 1000
    n_max = get_x(filename, 'w_max') 
    return n_eck, n_min_star, n_max

def get_pi_plot_data(filename, dim_name, base_op, star_position, ymax=None):
    new_dim_name = PIModelData.name_mapping_peak[dim_name] 

    ds_names_original = ['P', 'derating', 'i_ACRMS_P', 'i_DC_P', 'SOC_end', 'v_P']
    dim_names_original = ['t_P', 'RCI_P', 'w_P', 'T_P']
    ds_names = [dsname + '_peak' for dsname in ds_names_original]
    dim_names = [dimname + '_peak' for dimname in dim_names_original]

    converted_op = convert_base_op(base_op, new_dim_name, dim_names)

    sim_results = get_sim_results(filename, converted_op, ds_names, new_dim_name)

    dataset_name = "/" +  new_dim_name 
    x = get_x(filename, dataset_name)
    y = abs(sim_results['P_peak'])/1000
    x_unit = get_x_unit(new_dim_name)

    line_data = dict()
    line_data['x'] = x
    line_data['x_label'] = get_x_label(new_dim_name)
    line_data['x_unit'] = x_unit 
    line_data['y'] = y
    line_data['y_label'] = '$P_{mech}$'
    line_data['y_unit'] = 'kW'
    line_data['color'] = sim_results['derating_peak']

    annotations = get_star_annotation(sim_results, x, x_unit, y, star_position)

    plot_data = dict(line_data = line_data, 
                     star_annotations = annotations, 
                     ymax = ymax)
    return plot_data

def convert_base_op(base_op, scale_name, scale_names):
    converted_op = dict()
    for key in base_op.keys():
        try:
            new_name = PIModelData.name_mapping_peak[key]
        except Exception:
            new_name = key
        if new_name != scale_name and new_name in scale_names:
            converted_op[new_name] = PIModelData.convert_to_si(new_name, base_op[key])
    return converted_op
            

def get_x(filename, ds_name):
    print ds_name
    ds = sdf.load(filename, ds_name)
    return PIModelData.convert_from_si(ds_name, ds.data)

def get_sim_results(filename, converted_op, ds_names, dim_name):
    sim_results = dict()
    sds = sdfm.SplittableDataset()
    for name in ds_names:
        print name
        sds.load_ds_and_scales(filename, name)
        ds = sds.sub_dataset([dim_name], converted_op)
        sim_results[name] = ds.data

    return sim_results

def get_x_label(dim_name):
    label_names = dict(t_P_peak = u't/s', 
                       RCI_P_peak = u'RCI/%', 
                       w_P_peak = u'$n_{mech}$/1/min', 
                       T_P_peak = u'$T_{ees}$/°C')

    return label_names[dim_name]

def get_x_unit(dim_name):
    label_names = dict(t_P_peak = u's', 
                       RCI_P_peak = u'%', 
                       w_P_peak = u' 1/min', 
                       T_P_peak = u'°C')

    return label_names[dim_name]

def get_star_annotation(sim_results, x, x_unit, y, star_position):
    text_template = u'{0}kW@{1}{2}\n{3}A@{4}V@{5}A(AC)'

    star_indices = [_get_index(star, x) for star in star_position]
    annotations = []
    r = sim_results
    for i in star_indices:
        text = text_template.format(int(math.floor(y[i])), 
                                    int(round(x[i])), x_unit, 
                                    int(round(r['i_DC_P_peak'][i])), 
                                    int(round(r['v_P_peak'][i])), 
                                    int(round(r['i_ACRMS_P_peak'][i]))
                                    )
        x_a = x[i]
        y_a = y[i]
        annotations.append((x_a, y_a, text))


    return annotations


def _get_index(element, list_of_elements, tolerance=1e-5):
    try:
        return list_of_elements.index(element)
    except Exception:
        pass
    indices = [i for i, x in enumerate(list_of_elements) if abs(x - element) < tolerance]
    try:
        return indices[0]
    except Exception:
        raise Exception(u"can't find the element " + unicode(element) + u" in list " + unicode(list_of_elements))

if __name__ == "__main__":
    piview = PIMVC.PISlide()
    pimodel = PIMasterModel('test.sdf', ymax=280)
    picontroller = PIMVC.PIController(pimodel, piview)
    picontroller.save("test_new.pptx")
