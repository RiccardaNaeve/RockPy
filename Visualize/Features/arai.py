__author__ = 'mike'
import matplotlib.pyplot as plt
from matplotlib import lines
import numpy as np


def arai_points(ax, m_obj, component='mag', **plt_opt):
    idx = m_obj._get_idx_equal_val('ptrm', 'th', 'temp')
    x = m_obj.ptrm.filter_idx(idx[:, 0])
    y = m_obj.th.filter_idx(idx[:, 1])

    marker = plt_opt.pop('marker', 's')
    markersize = plt_opt.pop('markersize', 3)
    linestyle = plt_opt.pop('linestyle', '')

    lines = ax.plot(x[component].v, y[component].v,
            marker=marker,
            linestyle=linestyle,
            markersize=markersize,
            zorder=100,
            label=m_obj.sample_obj.name,
            **plt_opt)

    return lines

def arai_fit(ax, m_obj, component='mag', **plt_opt):
    slope = m_obj.result_slope().v[0]
    intercept = m_obj.result_y_int().v[0]
    x = m_obj.data['ptrm']['mag'].v
    y = x * slope + intercept
    color = plt_opt.pop('color', '#808080')
    markersize = plt_opt.pop('markersize', 3)
    linestyle = plt_opt.pop('linestyle', '--')

    lines = ax.plot(x, y,
            marker='',
            linestyle=linestyle,
            markersize=markersize,
            zorder=100,
            label=m_obj.sample_obj.name,
            **plt_opt)

    return lines

def arai_stdev(ax, m_obj, component='mag', **plt_opt):
    idx = m_obj._get_idx_equal_val('ptrm', 'th', 'temp')
    x = m_obj.ptrm.filter_idx(idx[:, 0])
    y = m_obj.th.filter_idx(idx[:, 1])
    color = plt_opt.pop('color', 'k')
    alpha = plt_opt.pop('alpha', 0.1)
    if not np.all(np.isnan(x[component].e)):
        lines = ax.errorbar(x=x[component].v,
                            xerr=x[component].e,
                            y=y[component].v,
                            yerr=y[component].e,
                            color=color,
                            # alpha=0.3,
                            zorder=2,
                            **plt_opt)
        # ax.fill_between(x[component].v,
        # y[component].v - y[component].e,
        #                 y[component].v + y[component].e,
        #                 color=color,
        #                 alpha= alpha,
        #                 zorder=0,
        #                 **plt_opt)
        return lines


def add_ck_check(ax, thellier_object, component='mag', norm_factor=[1, 1], **plt_opt):
    if not plt_opt: plt_opt = {}

    check_data = thellier_object._get_ck_data()
    idx = thellier_object.data['th'].column_dict[component][0]
    ptrm_idx = thellier_object.data['ptrm'].column_dict[component][0]

    for i in check_data:
        ck_i = i[0][idx] / norm_factor[0]
        th_i = i[1][idx] / norm_factor[0]
        ptrm_j = i[2][ptrm_idx] / norm_factor[1]
        th_j = i[3][idx] / norm_factor[1]
        hline = lines.Line2D([ck_i, ptrm_j], [th_j, th_j])  # ,linewidth=1.2)
        vline = lines.Line2D([ck_i, ck_i], [th_j, th_i])  # , linewidth=1.2)
        ax.add_line(hline)
        ax.add_line(vline)
        ax.plot(ck_i, th_i, '^', markerfacecolor='w')