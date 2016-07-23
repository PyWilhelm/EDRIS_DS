#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import math

import PIModelData, PIMVC 
from TaskController.BaseClass.Controller import Controller
import TaskController.PIPlots as pi
import piutils

get_peak_name = lambda x : x + "_peak" 


class PIMasterModel(object):
    def __init__(self, controller=None, edb_paths=None, pi_parameters=None, y_max=None):
        self.pi_parameters = piutils.get_default_pi_parameters() 
        if pi_parameters is not None:
            self.pi_parameters.update(pi_parameters)
        self.edb_paths = edb_paths 

        self.controller = Controller(priority=3) if controller == None else controller
        ops = ['master_op1', 'master_op2', 'master_op3',]
        self.pi_data = [self.get_pi_data(op) for op in ops]
        self.base_op = [piutils.get_base_op(op) for op in ops]
        n_eck = self.pi_data[0].get_parameter('n_eck')
        n_max = self.pi_data[0].get_parameter('n_max')
        self.y_max = y_max

    def get_pi_data(self, op):
        pid = pi.PIData(op, edb_paths=self.edb_paths, pi_parameters=self.pi_parameters)
        pid.start_simulation(self.controller)
        return pid 

    def plot_data(self):
        positions = PIModelData.get_plot_positions()
        plot_data_list = [None] * 5
        bop = self.base_op
        n_eck = self.pi_data[0].get_parameter('n_eck')
        n_max = self.pi_data[0].get_parameter('n_max')
        [unused_n_eck, n_min_star, n_max] = get_rpm_data(n_eck, n_max)

        # AP 1
        plot_data_list[0] = get_pi_plot_data(self.pi_data[0], 'n', bop[0], star_position=[bop[0]['n'], n_min_star, n_max, ], y_max=self.y_max)
        plot_data_list[1] = get_pi_plot_data(self.pi_data[0], 'RCI', bop[0], star_position=[bop[0]['RCI'], 50, 100], y_max=self.y_max)

        # AP 2
        plot_data_list[2] = get_pi_plot_data(self.pi_data[1], 't', bop[2], star_position=[bop[2]['t'], 10, 30,], y_max=self.y_max)

        # AP 3
        plot_data_list[3] = get_pi_plot_data(self.pi_data[2], 'T', bop[1], star_position=[bop[1]['T'], 25, 40], y_max=self.y_max)
        plot_data_list[4] = get_pi_plot_data(self.pi_data[2], 'RCI', bop[1], star_position=[bop[1]['RCI'], 50, 100], y_max=self.y_max)


        return [dict(plot_data=plot_data, position=position) 
                for plot_data, position in zip(plot_data_list, positions)]

    def title_data(self):
        return "Dummy title"

    def hvConsumption_data(self):
        return self.pi_data[0].get_parameter('HV_consumption')/1000

    def ap_data(self):
        positions = PIModelData.get_master_aps_positions()
        return [dict(value=value, position=position) for value, position in zip(self.base_op, positions)]

class PINormalModel(object):
    def __init__(self, base_op, controller=None, edb_paths=None, pi_parameters=None, y_max=None):
        self.pi_parameters = piutils.get_default_pi_parameters() 
        if pi_parameters is not None:
            self.pi_parameters.update(pi_parameters)
        self.edb_paths = edb_paths 
        self.base_op = [base_op]

        self.controller = Controller(priority=3) if controller == None else controller
        self.pi_data = [self.get_pi_data(base_op)]

        n_eck = self.pi_data[0].get_parameter('n_eck')
        n_max = self.pi_data[0].get_parameter('n_max')
        self.y_max = y_max

    def get_pi_data(self, base_op):
        pid = pi.PIData(fixed_op=None, base_op=base_op, edb_paths=self.edb_paths, pi_parameters=self.pi_parameters)
        pid.start_simulation(self.controller)
        return pid 

    def plot_data(self):
        positions = PIModelData.get_plot_positions()[:4]
        plot_data_list = [None] * 5

        bop = self.base_op

        n_eck = self.pi_data[0].get_parameter('n_eck')
        n_max = self.pi_data[0].get_parameter('n_max')
        [unused_n_eck, n_min_star, n_max] = get_rpm_data(n_eck, n_max)

        pid = self.pi_data[0]
        plot_data_list[0] = get_pi_plot_data(pid, 't', bop[0], star_position=get_stars(pid, 't'), y_max=self.y_max)
        plot_data_list[1] = get_pi_plot_data(pid, 'n', bop[0], star_position=get_stars(pid, 'n'), y_max=self.y_max)
        plot_data_list[2] = get_pi_plot_data(pid, 'RCI', bop[0], star_position=get_stars(pid, 'RCI'), y_max=self.y_max)
        plot_data_list[3] = get_pi_plot_data(pid, 'T', bop[0], star_position=get_stars(pid, 'T'), y_max=self.y_max)

        return [dict(plot_data=plot_data, position=position) 
                for plot_data, position in zip(plot_data_list, positions)]

    def title_data(self):
        return "Dummy title"

    def hvConsumption_data(self):
        return self.pi_data[0].get_parameter('HV_consumption')/1000

    def ap_data(self):
        position = PIModelData.get_normal_aps_positions()
        return [dict(value=self.base_op[0], position=position)]

def get_rpm_data(n_eck, n_max):
    n_min_star = int(n_eck / 1000 / 2) * 1000
    return n_eck, n_min_star, n_max

def get_stars(pi_data, dim_name):
    ds_name = PIModelData.name_mapping_peak[dim_name] 
    print 'star name', dim_name
    print 'stars are', pi_data.get_default_stars(ds_name)
    if (ds_name is 'w_P_peak') or (ds_name is 'T_P_peak'):
        return pi_data.get_default_stars(ds_name)
    else:
        return PIModelData.convert_from_si(ds_name, pi_data.get_default_stars(ds_name))

def get_pi_plot_data(pi_data, dim_name, base_op, star_position, y_max=None):
    new_dim_name = PIModelData.name_mapping_peak[dim_name] 

    ds_names_original = ['P', 'derating', 'i_ACRMS_P', 'i_DC_P', 'SOC_end', 'v_P']
    dim_names_original = ['t_P', 'RCI_P', 'w_P', 'T_P']
    ds_names = [dsname + '_peak' for dsname in ds_names_original]
    dim_names = [dimname + '_peak' for dimname in dim_names_original]

    sim_results = get_sim_results(pi_data, ds_names, new_dim_name)
    dataset_name = new_dim_name 
    x = get_x(pi_data, dataset_name)
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
                     y_max = y_max)
    return plot_data

def get_x(pi_data, ds_name):
    if (ds_name is 'w_P_peak') or (ds_name is 'T_P_peak'):
        return pi_data.get_scale(ds_name).data
    else:
        return PIModelData.convert_from_si(ds_name, pi_data.get_scale(ds_name).data)

def get_sim_results(pi_data, ds_names, dim_name):
    sim_results = dict()
    for name in ds_names:
        sim_results[name] = pi_data.get_results(name, dim_name).data
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

def start_pi(sim_type, input_data, session={}):
    print 'sim_type'
    print sim_type
    print 'input_data'
    print input_data
    print 'session'
    print session

    pi_parameters = input_data['pi_parameters']
    edb_paths = input_data['edb_paths']
    y_max = input_data['y_max']

    controller = Controller(priority=2)
    session['controller'] = controller 

    if sim_type == 'pi-tool-master':
        pimodel = PIMasterModel(controller=controller, edb_paths=edb_paths, 
                                pi_parameters=pi_parameters, y_max=y_max)
    elif sim_type == 'pi-tool':
        raise Exception('not implemented')
    else:
        raise Exception('not implemented')

    piview = PIMVC.PISlide()
    picontroller = PIMVC.PIController(pimodel, piview)

    import tempfile
    tf = tempfile.NamedTemporaryFile(prefix='pi_master_', suffix='.pptx', delete=False)
    picontroller.save(tf.name) 
    session['result'] = tf.name


if __name__ == "__main__":
    piview = PIMVC.PISlide()
    pi_parameters = {u'n_eck' : 3500, u'n_max': 7000}

    pimodel = PIMasterModel(controller=None, edb_paths=None, pi_parameters=pi_parameters, y_max=100)
    picontroller = PIMVC.PIController(pimodel, piview)
    picontroller.save("test_new.pptx")
