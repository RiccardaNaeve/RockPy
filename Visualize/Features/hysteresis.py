__author__ = 'mike'

def df_branch(ax, hys_obj, **plt_opt):
    """
    Plots the down_field branch of a hysteresis
    """
    ls = plt_opt.pop('ls', '-')
    marker = plt_opt.pop('marker', '')

    line_out = ax.plot(hys_obj.down_field['field'].v,
            hys_obj.down_field['mag'].v,
            ls = ls, marker = marker,
            **plt_opt)

    return line_out, None

def uf_branch(ax, hys_obj, **plt_opt):
    """
    Plots the down_field branch of a hysteresis
    """
    ls = plt_opt.pop('ls', '-')
    marker = plt_opt.pop('marker', '')

    line_out = ax.plot(hys_obj.up_field['field'].v,
            hys_obj.up_field['mag'].v,
            ls = ls, marker = marker,
            **plt_opt)
    return line_out, None

def virgin_branch(ax, hys_obj, **plt_opt):
    """
    Plots the down_field branch of a hysteresis
    """
    ls = plt_opt.pop('ls', '-')
    marker = plt_opt.pop('marker', '')

    line_out = ax.plot(hys_obj.virgin['field'].v,
            hys_obj.virgin['mag'].v,
            ls = ls, marker = marker,
            **plt_opt)
    return line_out, None

def irrev(ax, hys_obj, **plt_opt):
    ls = plt_opt.pop('ls', '-')
    marker = plt_opt.pop('marker', '')

    # ax.plot(hys_obj.up_field['field'].v,
    #         hys_obj.up_field['mag'].v,
    #         ls = ls, marker = marker,
    #         **plt_opt)
