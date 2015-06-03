__author__ = 'mike'
import numpy as np
import RockPy.Functions.general


def mom_temp(ax, rmp_obj, **plt_opt):
    color = {'up_temp': 'r', 'down_temp': 'b'}
    marker = plt_opt.pop('marker', '')
    ls = plt_opt.pop('ls', '-')

    for seg in rmp_obj.data:
        lines = ax.plot(rmp_obj.data[seg]['temp'].v, rmp_obj.data[seg]['mag'].v,
                        marker=marker,
                        ls=ls,
                        color=color[seg])
    return lines


def dmom_dtemp(ax, rmp_obj, **plt_opt):
    color = {'up_temp': 'r', 'down_temp': 'b'}
    marker = plt_opt.pop('marker', '')
    ls = plt_opt.pop('ls', '-')
    alpha = plt_opt.pop('alpha', 0.5)

    for seg in rmp_obj._data:
        segm = rmp_obj.data[seg].derivative('mag', 'temp', smoothing=3)
        lines = ax.plot(segm['temp'].v, -segm['mag'].v,
                        marker=marker,
                        ls=ls,
                        color=color[seg],
                        alpha=alpha)