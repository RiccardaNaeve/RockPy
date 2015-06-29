__author__ = 'mike'

def backfield(ax, coe_obj, **plt_opt):
    """
    Plots the down_field branch of a hysteresis
    """
    ls = plt_opt.pop('ls', '-')
    marker = plt_opt.pop('marker', '')

    line_out = ax.plot(coe_obj.data['data']['field'].v,
            coe_obj.data['data']['mag'].v,
            ls = ls, marker = marker,
            **plt_opt)

    return line_out, None