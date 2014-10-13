__author__ = 'mike'


def dunlop(ax, thellier_obj, parameter, style='screen', plt_idx=0,
           **plt_opt):
    component = parameter.get('component', 'mag')
    ax.plot(thellier_obj.sum['temp'], thellier_obj.sum[component], **plt_opt)
    ax.plot(thellier_obj.th['temp'], thellier_obj.th[component], **plt_opt)
    ax.plot(thellier_obj.ptrm['temp'], thellier_obj.ptrm[component], **plt_opt)
    return ax
