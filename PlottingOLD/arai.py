__author__ = 'mike'
import numpy as np


def arai_points(ax, thellier_obj, parameter, **plt_opt):
    label = plt_opt.pop('label', '')
    markersize = plt_opt.pop('markersize', 2)

    if thellier_obj.has_treatment:
        label = thellier_obj.get_treatment_labels()
        markersize += 2 * thellier_obj.treatments[0].value

    component = parameter.get('component', 'mag')
    idx = np.array([[i, j]
                    for i, v1 in enumerate(thellier_obj.data['ptrm']['temp'].v)
                    for j, v2 in enumerate(thellier_obj.th['temp'].v) if v1 == v2])
    th = thellier_obj.data['th'].filter_idx(idx[:, 1])[component]
    ptrm = thellier_obj.data['ptrm'].filter_idx(idx[:, 0])[component]

    ax.plot(ptrm[component].v, th[component].v,
            '.', linestyle=':', zorder=100,
            markersize=markersize,
            label=label,
            **plt_opt)


def arai_std(ax, thellier_obj, parameter, **plt_opt):
    component = parameter.get('component', 'mag')
    non_plt_opt = ['label', 'marker', 'markersize', 'linestyle', 'ls']
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


def arai_error(ax, thellier_obj, parameter, **plt_opt):
    component = parameter.get('component', 'mag')
    non_plt_opt = ['label', 'marker', 'markersize', 'linestyle', 'ls']
    plt_opt = {i: plt_opt[i] for i in plt_opt if not i in non_plt_opt}

    idx = np.array([[i, j]
                    for i, v1 in enumerate(thellier_obj.data['ptrm']['temp'].v)
                    for j, v2 in enumerate(thellier_obj.th['temp'].v) if v1 == v2])
    th = thellier_obj.data['th'].filter_idx(idx[:, 1])[component]
    ptrm = thellier_obj.data['ptrm'].filter_idx(idx[:, 0])[component]
    ax.errorbar(x=ptrm[component].v, y=th[component].v,
                yerr=th[component].e, linestyle='',
                zorder=0, **plt_opt
    )
    return ax


def arai_line(ax, thellier_obj, parameter, mean_results=True, **plt_opt):
    """
    if the thellier object is from an average measurement, it should use the mean(results) instead of the results(mean)
    By changing the mean_results, this behaviour can can be changed and the results of the means will be calculated
    """
    component = parameter.get('component', 'mag')

    if thellier_obj.sample_obj.is_average:
        print thellier_obj.sample_obj
    thellier_obj.calculate_slope(**parameter)
    # print thellier_obj.results
    slope = thellier_obj.result_slope(**parameter).v
    y_int = thellier_obj.result_y_int(**parameter).v
    x_new = [min(thellier_obj.ptrm[component].v), max(thellier_obj.ptrm[component].v)]
    y_new = slope * x_new + y_int

    plt_opt.update({'linestyle': '-', 'alpha': 1, 'zorder': 0, 'marker': '', 'label': ''})
    ax.plot(x_new, y_new, **plt_opt)


def arai_1_1_line(ax, **plt_opt):
    xlim = ax.get_xlim()
    ax.plot(xlim, xlim[::-1], '-', color='k', zorder=0, **plt_opt)