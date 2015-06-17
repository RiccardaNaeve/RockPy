__author__ = 'mike'
import matplotlib.pyplot as plt
from matplotlib import lines
import numpy as np
import RockPy.core


def arai_points(ax, m_obj, component='mag', tmin=0, tmax=700, **plt_opt):
    """
    Feature to plot the points in an arai diagram. Points used for calculation of best fit slope
    are filled, points not used for calculation or nor filled
    :param ax:
    :param m_obj:
    :param component:
    :param tmin:
    :param tmax:
    :param plt_opt:
    :return:
    """

    idx = m_obj._get_idx_equal_val('ptrm', 'th', 'temp')
    x = m_obj.ptrm.filter_idx(idx[:, 0])
    y = m_obj.th.filter_idx(idx[:, 1])

    x_fill = x.filter((tmin <= x['temp'].v) & (tmax >= x['temp'].v))
    y_fill = y.filter((tmin <= y['temp'].v) & (tmax >= y['temp'].v))

    x_nofill = x.filter(RockPy.core.compare_array(x['temp'].v, x_fill['temp'].v, AinB=False))
    y_nofill = y.filter(RockPy.core.compare_array(y['temp'].v, y_fill['temp'].v, AinB=False))

    marker = plt_opt.pop('marker', 's')
    markersize = plt_opt.pop('markersize', 3)
    linestyle = plt_opt.pop('linestyle', '')
    label = plt_opt.pop('label', '')

    if x_nofill:
        # unfilled markers inside the analysis interval
        nofill_line = ax.plot(x_nofill[component].v, y_nofill[component].v,
                        marker=marker,
                        fillstyle='none',
                        markersize=markersize,
                        linestyle=linestyle,
                        zorder=100,
                        label=label,
                        **plt_opt)

    # filled markers inside the analysis interval
    fill_lines = ax.plot(x_fill[component].v, y_fill[component].v,
                    marker=marker,
                    markersize=markersize,
                    linestyle=linestyle,
                    zorder=100,
                    label=label,
                    **plt_opt)
    return [nofill_line, fill_lines]


def arai_fit(ax, m_obj, component='mag', tmin=0, tmax=700, **plt_opt):
    calculation_parameter = dict(component=component, tmin=tmin, tmax=tmax)
    slope = m_obj.calculate_result(result = 'slope', parameter=calculation_parameter).v[0]
    intercept = m_obj.calculate_result(result = 'y_int', parameter=calculation_parameter).v[0]

    ptrm = m_obj.ptrm.filter((tmin <= m_obj.ptrm['temp'].v) & (tmax >= m_obj.ptrm['temp'].v))

    x = ptrm['mag'].v
    y = x * slope + intercept

    color = plt_opt.pop('color', '#808080')
    marker = plt_opt.pop('marker', '')
    markersize = plt_opt.pop('markersize', 3)
    linestyle = plt_opt.pop('linestyle', '--')

    lines = ax.plot(x, y,
            marker='',
            linestyle=linestyle,
            color = color,
            # markersize=markersize,
            zorder=100,
            # label=m_obj.sample_obj.name,
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


def add_ck_check(ax, m_obj, component='mag', **plt_opt):
    if not plt_opt: plt_opt = {}

    check_data = m_obj._get_ck_data()
    th_idx = m_obj.data['th'].column_dict[component][0]
    ptrm_idx = m_obj.data['ptrm'].column_dict[component][0]

    plt_opt.pop('marker')
    plt_opt.pop('ls')
    # color = plt_opt.pop('color', 'k')

    for i in check_data:
        ck_i = i[0][th_idx]
        th_i = i[1][th_idx]
        ptrm_j = i[2][ptrm_idx]
        th_j = i[3][th_idx]
        hline = lines.Line2D([ck_i, ptrm_j], [th_j, th_j], **plt_opt)  # ,linewidth=1.2)
        vline = lines.Line2D([ck_i, ck_i], [th_j, th_i], **plt_opt)  # , linewidth=1.2)
        ax.add_line(hline)
        ax.add_line(vline)

        ax.plot(ck_i, th_i,
                marker = '^',
                markerfacecolor='w',
                **plt_opt)
