__author__ = 'mike'
import numpy as np
import RockPy.Functions.general

def mom_temp(ax, rmp_obj, **plt):
    color = {'up_temp': 'r', 'down_temp': 'b'}
    for seg in rmp_obj._data:
        lines = ax.plot(rmp_obj.data[seg]['temp'].v, rmp_obj.data[seg]['mag'].v, '.-', color=color[seg])
    return lines

def dmom_dtemp(ax, rmp_obj, **plt):
    color = {'up_temp': 'r', 'down_temp': 'b'}
    ymax = max(ax.get_ylim())
    for seg in rmp_obj._data:
        print(seg)
        segm = rmp_obj.data[seg].derivative('mag', 'temp', smoothing=5)
        norm = ymax
        lines = ax.plot(segm['temp'].v, segm['mag'].v / norm , '-', color=color[seg],
                        alpha = 0.2)