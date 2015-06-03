__author__ = 'mike'


def one_to_one_line(ax, **plt_opt):
    """
    Plots the down_field branch of a hysteresis
    """
    ls = plt_opt.pop('ls', '--')
    color = plt_opt.pop('color', '#808080')

    line_out = ax.plot([1,-1], [0, 1],
                       ls = ls,
                       color = color,
                       ** plt_opt)

    return line_out, None

def henkel(ax, coe, irm, reference = 'coe', **plt_opt):
    """
    Plots the down_field branch of a hysteresis
    """
    if reference == 'coe':
        irm = irm.data['remanence'].interpolate(-coe.data['remanence']['field'].v)
        coe = coe.data['remanence']
    if reference == 'irm':
        coe = coe.data['remanence'].interpolate(-irm.data['remanence']['field'].v)
        irm = irm.data['remanence']
    if reference == 'none':
        coe = coe.data['remanence']
        irm = irm.data['remanence']

    ls = plt_opt.pop('ls', '-')
    marker = plt_opt.pop('marker', '.')
    line_out = ax.plot(coe['mag'].v, irm['mag'].v,
                       ls = ls, marker=marker,
                       ** plt_opt)
    return line_out, None
