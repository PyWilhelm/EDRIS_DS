#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pptx.util import Cm
import math

def get_plot_positions():
    positions = []
    positions.append(dict(left = Cm(0.95), top = Cm(3.12), height = Cm(8.38), width = Cm(8.38),))
    positions.append(dict(left = Cm(8.70), top = Cm(3.12),  height = Cm(8.38), width = Cm(8.38),))
    positions.append(dict(left = Cm(16.52), top = Cm(3.12), height = Cm(8.38), width = Cm(8.38),))
    positions.append(dict(left = Cm(0.95), top = Cm(10.74), height = Cm(8.38), width = Cm(8.38),))
    positions.append(dict(left = Cm(8.70), top = Cm(10.74),  height = Cm(8.38), width = Cm(8.38),))
    return positions

def get_master_aps_positions():
    positions = [None] * 3
    positions[0] = dict(left = Cm(0.88), top = Cm(2.93), height = Cm(0.81), width = Cm(14.82),)
    positions[1] = dict(left = Cm(0.88), top = Cm(10.51), height = Cm(0.81), width = Cm(14.82),)
    positions[2] = dict(left = Cm(16.74), top = Cm(2.93), height = Cm(1.06), width = Cm(7.76),)
    return positions

def get_normal_aps_positions():
    position = dict(left = Cm(0.88), top = Cm(2.93), height = Cm(0.81), width = Cm(22.82),)
    return position

name_mapping_peak = dict(t = 't_P_peak', n = 'w_P_peak',  RCI = 'RCI_P_peak', T = 'T_P_peak')

def convert_to_si(name, value):
    if 'w_P_peak' in name  or 'w_P_cont' in name or 'w_max' in name  or 'w_char' in name:
        value = value * 2 * math.pi / 60
    if 'T_P_peak' in name  or 'T_P_cont' in name :
        value = value + 273.15
    if 'RCI_P' in name:
        value = value / 100.
    return value

def convert_from_si(name, value):
    if 'w_P_peak' in name  or 'w_P_cont' in name or 'w_max' in name  or 'w_char' in name:
        value = value / 2 / math.pi * 60
    if 'T_P_peak' in name  or 'T_P_cont' in name :
        value = value - 273.15
    if 'RCI_P' in name:
        value = value * 100.
    return value

