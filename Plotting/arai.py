__author__ = 'mike'
import numpy as np


def arai_points(ax, thellier_obj, parameter, **plt_opt):
    if thellier_obj.has_treatment:
        label = thellier_obj.suffix
    else:
        label = ''
    # print thellier_obj.data
    component = parameter.get('component', 'mag')
    idx = np.array([[i, j]
                    for i, v1 in enumerate(thellier_obj.data['ptrm']['temp'].v)
                    for j, v2 in enumerate(thellier_obj.th['temp'].v) if v1 == v2])
    th = thellier_obj.data['th'].filter_idx(idx[:, 1])[component]
    ptrm = thellier_obj.data['ptrm'].filter_idx(idx[:, 0])[component]

    ax.plot(ptrm[component].v, th[component].v,
            '.-', zorder=100,
            label=label)


def arai_std(ax, thellier_obj, parameter, **plt_opt):
    component = parameter.get('component', 'mag')
    non_plt_opt = ['label', 'marker', 'markersize', 'linestyle','ls']
    plt_opt = {i: plt_opt[i] for i in plt_opt if not i in non_plt_opt}

    idx = np.array([[i, j]
                    for i, v1 in enumerate(thellier_obj.data['ptrm']['temp'].v)
                    for j, v2 in enumerate(thellier_obj.th['temp'].v) if v1 == v2])
    th = thellier_obj.data['th'].filter_idx(idx[:, 1])[component]
    ptrm = thellier_obj.data['ptrm'].filter_idx(idx[:, 0])[component]
    ax.fill_between(ptrm[component].v,
                    th[component].v + th[component].e,
                    th[component].v - th[component].e,
                    alpha=.1, zorder=0, **plt_opt
                    )
    return ax

def arai_line(ax, thellier_obj, parameter, **plt_opt):
    component = parameter.get('component', 'mag')
    thellier_obj.calculate_slope(**parameter)
    # print thellier_obj.results
    slope = thellier_obj.result_slope(**parameter).v
    y_int = thellier_obj.result_y_int(**parameter).v
    x_new = [min(thellier_obj.ptrm[component].v), max(thellier_obj.ptrm[component].v)]
    y_new = slope * x_new + y_int

    plt_opt.update({'linestyle': '--', 'alpha': 0.5, 'zorder': 0, 'marker': '', 'label': ''})
    ax.plot(x_new, y_new, **plt_opt)