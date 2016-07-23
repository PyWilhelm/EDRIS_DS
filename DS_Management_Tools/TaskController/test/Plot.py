#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import itertools
from matplotlib import pyplot as plt
import numpy as np
import os
import functools


class PISlide(object):

    def __init__(self, data, layout):
        self.powerpoint_template = os.path.join(os.path.dirname(__file__), "base_pi.pptx")
        self.data = data
        self.layout = layout

    def _create_text_box(self):
        pass

    def save_as_powerpoint(self, filename):
        dirname = os.path.dirname(filename)


class PILayout(object):

    def __init__(self, options):
        self.text_boxes = options['text_boxes']
        self.plot_position = options['plot_position']


def report_plot(x, y, aps, xn, yn, title, ymax=None):
    print 'x = ', x
    print 'y = ', y
    print 'aps = ', aps

    fig = plt.figure(figsize=(4, 4), dpi=300)

    colors = itertools.cycle(['b', 'g', 'r', 'c', 'm', 'y', 'k'])
    if ymax is None:
        xmin, xmax, ymin, ymax = min(x), max(x), min(y), max(y)
    else:
        xmin, xmax, ymin, ymax = min(x), max(x), min(y), ymax
    # initialize figure and sub figure

    plot_position = [1, 1, 1]
    ax = fig.add_subplot(*plot_position)
    # plot function
    ax.plot(x, y, c='black', lw=5, alpha=0.8)
    print 'plt.ylim()', plt.ylim()
    print 'plt.xlim()', plt.xlim()
    txt_height = 0.10 * (plt.ylim()[1] - plt.ylim()[0])
    txt_width = 0.31 * (plt.xlim()[1] - plt.xlim()[0])
    x2 = np.array([x, x])
    _x = x2.reshape(1, x2.size)
    y2 = np.array([y, y])
    _y = y2.reshape(1, y2.size)
    _x, _y, text = zip(*aps)
    text_pos = get_text_positions(list(_x), list(_y), txt_width, txt_height)

    # set grid
    ax.grid(linewidth=1)
    ax.xaxis.grid()
    ax.yaxis.grid()
    for side in ['bottom', 'right', 'top', 'left']:
        ax.spines[side].set_visible(False)
        if side == 'bottom':
            ax.spines[side].set_position(('data', ymin))
        if side == 'left':
            ax.spines[side].set_position(('data', xmin))

    # set axis style
    ax.xaxis.set_ticks_position('none')
    ax.yaxis.set_ticks_position('none')

    plt.grid()
    factor_arrow = 0.014142321343243
    x_min_arrow = xmin - (xmax - xmin) * factor_arrow
    x_max_arrow = xmax + (xmax - xmin) * factor_arrow
    y_min_arrow = ymin - (ymax - ymin) * factor_arrow
    y_max_arrow = ymax + (ymax - ymin) * factor_arrow
    plt.xlim(x_min_arrow, x_max_arrow)
    plt.ylim(y_min_arrow, y_max_arrow)
    ax.annotate('', (xmin, y_max_arrow), (xmin, y_min_arrow),
                ha="center", va="center",
                arrowprops=dict(arrowstyle='->',
                                shrinkA=0,
                                shrinkB=0,
                                linewidth=3.,
                                fc="w", ec="k"
                                ),
                bbox=dict(boxstyle="square", fc="w"))
    ax.annotate('', (x_max_arrow, ymin),
                (x_min_arrow, ymin),
                ha="center", va="center",
                arrowprops=dict(arrowstyle='->',
                                shrinkA=0,
                                shrinkB=0,
                                linewidth=3.,
                                fc="w", ec="k"
                                ),
                bbox=dict(boxstyle="square", fc="w"))
    # set axis label
    ax.text(xmax + (xmax - xmin) * 0.05, ymin - (ymax - ymin) * 0.03, xn, fontsize=16)
    ax.text(xmin - (xmax - xmin) * 0.1, ymax + (ymax - ymin) * 0.04, yn, fontsize=16)

    for i, ap in enumerate(aps):
        this_color = colors.next()
        ax.plot([ap[0]], [ap[1]], c=this_color, marker='*', markersize=20, lw=0)
        ax.annotate(ap[2], xy=(ap[0], ap[1]), xytext=(ap[0] - (xmax - xmin) * 0.05, text_pos[i] + ap[1]),
                    ha="center", va="center",
                    bbox=dict(boxstyle="Square", fc="w", ec=this_color, alpha=0.8),
                    arrowprops=dict(arrowstyle='->'))
    fig.save = functools.partial(fig.savefig, transparent=False, bbox_inches='tight', pad_inches=0.5)
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
    return [pos_list[i % 2][i] * ((-1) ** i) for i in range(len(x_data))]


def __get_text_positions(x_data, y_data, txt_width, txt_height):
    a = zip(y_data, x_data)
    text_positions = list(y_data)
    for index, (y, x) in enumerate(a):
        local_text_positions = [i for i in a if i[0] > (y - txt_height)
                                and (abs(i[1] - x) < txt_width) and i != (y, x)]
        print local_text_positions
        if local_text_positions:
            sorted_ltp = sorted(local_text_positions)
            if abs(sorted_ltp[0][0] - y) < txt_height:  # True == collision
                differ = np.diff(sorted_ltp, axis=0)
                a[index] = (sorted_ltp[-1][0] + txt_height, a[index][1])
                text_positions[index] = sorted_ltp[-1][0] + txt_height
                for k, (j, m) in enumerate(differ):
                    # j is the vertical distance between words
                    if j > txt_height * 2:  # if True then room to fit a word in
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
            det_max = max([det1, det2]) if max([det1, det2]) > 0 else txt_height
            final.append(det_min if det_min > 0 else det_max)
    return final


if __name__ == "__main__":
    x1 = np.arange(0.0, 1.1, 0.1) * 1.0324
    y = np.arange(0.0, 11, 1) * 1.0324
    text = ['160kW@30s\n-312A@423V@103A(AC)', '160kW@30s\n-312A@423V@103A(AC)', '160kW@30s\n-312A@423V@103A(AC)']
    new_fig = report_plot(x1, y, zip(x1[1:10:4], y[1:10:4], text), u'$deg$ (°C)', '$P_{mech}$', '   ')
    # new_fig.savefig('temp.png', transparent=False, bbox_inches='tight', pad_inches=0.5,)
    new_fig.save('func.png')
