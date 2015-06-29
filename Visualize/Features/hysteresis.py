__author__ = 'mike'

def df_branch(ax, hys_obj, **plt_opt):
    """
    Plots the down_field branch of a hysteresis
    """
    ls = plt_opt.pop('ls', '-')
    marker = plt_opt.pop('marker', '')

    line_out = ax.plot(hys_obj.data['down_field']['field'].v,
            hys_obj.data['down_field']['mag'].v,
            ls = ls, marker = marker,
            **plt_opt)

    return line_out, None


def uf_branch(ax, hys_obj, **plt_opt):
    """
    Plots the down_field branch of a hysteresis
    """
    ls = plt_opt.pop('ls', '-')
    marker = plt_opt.pop('marker', '')

    line_out = ax.plot(hys_obj.data['up_field']['field'].v,
            hys_obj.data['up_field']['mag'].v,
            ls = ls, marker = marker,
            **plt_opt)
    return line_out, None

def virgin_branch(ax, hys_obj, **plt_opt):
    """
    Plots the down_field branch of a hysteresis
    """
    ls = plt_opt.pop('ls', '-')
    marker = plt_opt.pop('marker', '')

    line_out = ax.plot(hys_obj.data['virgin']['field'].v,
            hys_obj.data['virgin']['mag'].v,
            ls = ls, marker = marker,
            **plt_opt)
    return line_out, None

def irreversible(ax, hys_obj, **plt_opt):
    ls = plt_opt.pop('ls', '-')
    marker = plt_opt.pop('marker', '')
    irrev = hys_obj.get_irreversible()
    line_out = ax.plot(irrev['field'].v,
            irrev['mag'].v,
            ls = ls, marker = marker,
            **plt_opt)
    return line_out, None

def reversible(ax, hys_obj, **plt_opt):
    """
    Plots the down_field branch of a hysteresis
    """
    ls = plt_opt.pop('ls', '-')
    marker = plt_opt.pop('marker', '')

    rev = hys_obj.get_reversible()

    line_out = ax.plot(rev['field'].v,
            rev['mag'].v,
            ls = ls, marker = marker,
            **plt_opt)

    return line_out, None