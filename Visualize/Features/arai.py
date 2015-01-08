__author__ = 'mike'
import matplotlib.pyplot as plt
from matplotlib import lines


def arai_points(ax, thellier_object, component='mag', **plt_opt):
    ax.plot(thellier_object.ptrm[component], thellier_object.th[component])


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