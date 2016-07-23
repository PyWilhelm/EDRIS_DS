#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import itertools
from matplotlib import pyplot as plt
from matplotlib.figure import SubplotParams
import functools
import numpy as np
from matplotlib.colors import ListedColormap, BoundaryNorm
import ColorPlot as cp
import random

def plot_pi(plot_data):
    return report_plot(plot_data['line_data'], plot_data['star_annotations'], plot_data['y_max'])

def report_plot(line_data, star_annotations, y_max = None):
    x = line_data["x"]
    xn = line_data["x_label"]
    y = line_data["y"]
    yn = line_data["y_label"]
    yunit = line_data["y_unit"]
    color = line_data["color"]

    
    # padding for the plot
    subplotpars = SubplotParams(left = 0.175, right = 0.80, 
                                bottom = 0.175, top = 0.80, 
                                wspace = 0.2, hspace = 0.2)

    fig = plt.figure(figsize=(5, 5), dpi=300, subplotpars = subplotpars)

    # set colors
    colors_list = [ '#D46A6A', '#669999', '#D4EE9F', '#FFAAAA', '#7788AA', '#9675AB', ]
    random.shuffle(colors_list)
    other_colors = itertools.cycle(colors_list)
    colors = itertools.chain(['#000000'], other_colors) # the first star is always black


    if y_max is None:
        xmin, xmax, ymin, y_max  = min(x), max(x), 0, max(y)
    else: 
        xmin, xmax, ymin, y_max  = min(x), max(x), 0, y_max
    # initialize figure and sub figure

    plot_position = [1, 1, 1]
    ax = fig.add_subplot(*plot_position)
    # plot function
    cmap = ListedColormap(['#000000', '#76B700', '#C3D69B', '#FF0000'])
    norm = BoundaryNorm([-1, 0.5, 1.5, 2.5, 3.5], cmap.N)  # cmap.N is number of items in the colormap
    cp.colorline(x, y, color, cmap=cmap, norm=norm, linewidth=3, alpha=0.8)
    factor_arrow = 0.014142321343243
    x_min_arrow = xmin-(xmax-xmin)*factor_arrow
    x_max_arrow = xmax+(xmax-xmin)*factor_arrow
    y_min_arrow = ymin-abs(y_max-ymin)*factor_arrow
    y_max_arrow = y_max+abs(y_max-ymin)*factor_arrow
    plt.xlim(xmin, x_max_arrow)
    plt.ylim(ymin, y_max_arrow)

    txt_height = 0.10*(plt.ylim()[1] - plt.ylim()[0])
    txt_width = 0.31*(plt.xlim()[1] - plt.xlim()[0])

    x2 = np.array([x, x])
    _x = x2.reshape(1, x2.size)
    y2 = np.array([y, y])
    _y = y2.reshape(1, y2.size)

    _x, _y, text = zip(*star_annotations)

    text_pos = get_text_positions(list(_x), list(_y), txt_width, txt_height)

    # set grid
    ax.grid(linewidth=1)
    ax.xaxis.grid()
    ax.yaxis.grid()

    for side in ['bottom','right','top','left']:
        ax.spines[side].set_visible(False)
        if side == 'bottom':
            ax.spines[side].set_position(('data', ymin))
        if side == 'left':
            ax.spines[side].set_position(('data', xmin))
            
    # set axis style
    ax.xaxis.set_ticks_position('none') 
    ax.yaxis.set_ticks_position('none')

    fig.canvas.draw()
    xticklabel_fontsize = 10 
    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(xticklabel_fontsize) 
    labels = [item.get_text() + yunit 
              for item in ax.get_yticklabels()]
    ax.set_yticklabels(labels)
    plt.grid()
    # set axis label
    ax.text(xmax+(xmax-xmin)*0.02, ymin-(y_max-ymin)*0.01, xn, fontsize=14, stretch = 0)
    ax.text(xmin-(xmax-xmin)*0.1, y_max+(y_max-ymin)*0.04, yn, fontsize=15)
    


    # Axis arrow
    ax.annotate('', (xmin, y_max_arrow), (xmin, ymin),
                ha="center", va="center",
                arrowprops=dict(arrowstyle='->',
                                shrinkA=0,
                                shrinkB=0,
                                linewidth = 3.,
                                fc="b", ec="k"
                                ),
                )
    ax.annotate('', (x_max_arrow , ymin), (xmin, ymin),
                ha="center", va="center",
                arrowprops=dict(arrowstyle='->',
                                shrinkA=0,
                                shrinkB=0,
                                linewidth = 3.,
                                fc="w", ec="k"
                                ),
                )

    for i, ap in enumerate(star_annotations):
        this_color = colors.next()
        ax.plot([ap[0]], [ap[1]], c=this_color , marker='*', markersize=20,lw=0, clip_on=False)
        ax.annotate(ap[2] ,xy=(ap[0], ap[1]), xytext=(ap[0], text_pos[i]+ap[1]), 
                    ha="center", va="center", fontsize = 9, 
                    bbox=dict(boxstyle="Square", fc="w", ec=this_color, alpha=0.8),
                    arrowprops=dict(arrowstyle='->'))

    fig.save = functools.partial(fig.savefig, transparent=True, dpi=300)
    return fig
    
def get_text_positions(x_data, y_data, txt_width, txt_height):
    x2 = np.array([x_data, x_data])
    _x = x2.reshape(1, x2.size)[0]
    y2 = np.array([y_data, y_data])
    _y = y2.reshape(1, y2.size)[0]
    pos_list1 = __get_text_positions(_x, _y, txt_width, txt_height)
    pos_list2 = __get_text_positions(_x * (-1), _y * (-1), txt_width, txt_height)
    pos_list = [pos_list1, pos_list2]
    position = 0    
    return [pos_list[i%2][i]*((-1)**i) for i in range(len(x_data))]
        
def __get_text_positions(x_data, y_data, txt_width, txt_height):
    a = zip(y_data, x_data)
    text_positions = list(y_data)
    for index, (y, x) in enumerate(a):
        local_text_positions = [i for i in a if i[0] > (y - txt_height) 
                            and (abs(i[1] - x) < txt_width) and i != (y,x)]
        #print local_text_positions
        if local_text_positions:
            sorted_ltp = sorted(local_text_positions)
            if abs(sorted_ltp[0][0] - y) < txt_height: #True == collision
                differ = np.diff(sorted_ltp, axis=0)
                a[index] = (sorted_ltp[-1][0] + txt_height, a[index][1])
                text_positions[index] = sorted_ltp[-1][0] + txt_height
                for k, (j, m) in enumerate(differ):
                    #j is the vertical distance between words
                    if j > txt_height * 2: #if True then room to fit a word in
                        a[index] = (sorted_ltp[k][0] + txt_height, a[index][1])
                        text_positions[index] = sorted_ltp[k][0] + txt_height
                        break
    final = []
    half = len(text_positions) / 2
    for index, y in enumerate(y_data):
        if index < half:
            det1 = text_positions[index] - y
            det2 = text_positions[index + half] - y
            det_min = min([det1, det2]) 
            det_max = max([det1, det2]) if max([det1, det2])>0 else txt_height
            final.append(det_min if det_min>0 else det_max)
    return final

if __name__ == "__main__":
    line_data = dict()
    x1 = np.arange(0.0, 1.1, 0.1) * 1.0324
    y = np.arange(0.0, 11, 1)* 1.0324
    line_data['x'] = np.arange(0.0, 1.1, 0.1) * 1.0324
    line_data['x_label'] = u't (°C)'
    line_data['y'] = np.arange(0.0, 11, 1)* 1.0324
    line_data['y_label'] = '$P_{mech}$ (kW)'
    line_data['y_unit'] = 'kW'
    line_data['color'] = np.arange(0.0, 11, 1)
    
    text = ['160kW@30s\n-312A@423V@103A(AC)', '160kW@30s\n-312A@423V@103A(AC)', '160kW@30s\n-312A@423V@103A(AC)']
    annotations = zip(x1[1:10:4], y[1:10:4], text) 
    new_fig = report_plot(line_data, annotations)
    new_fig.save('func.png')
