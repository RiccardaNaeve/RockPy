__author__ = 'mike'
import numpy as np


def arai(ax, thellier_obj, parameter, **plt_opt):
    component = parameter.get('component', 'mag')
    idx = np.array([[i, j]
                    for i, v1 in enumerate(thellier_obj.ptrm['temp'])
                    for j, v2 in enumerate(thellier_obj.th['temp']) if v1 == v2])
    ax.plot(thellier_obj.ptrm[component][idx[:, 0]], thellier_obj.th[component][idx[:, 1]])


def arai_line(ax, thellier_obj, parameter, **plt_opt):
    component = parameter.get('component', 'mag')

    slope = thellier_obj.result_slope(**parameter)
    y_int = thellier_obj.result_y_int(**parameter)

    x_new = [min(thellier_obj.ptrm[component]), max(thellier_obj.ptrm[component])]
    y_new = slope * x_new + y_int

    ax.plot(x_new, y_new, color='#808080', alpha=0.8)