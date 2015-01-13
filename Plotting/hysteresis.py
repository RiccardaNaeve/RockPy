__author__ = 'mike'


def vigin_branch(ax, hysteresis_obj, norm_factor=[1, 1],
                 plt_idx=0,
                 **plt_opt):
    """
    Plots the virgin branch of a hysteresis
    """
    ls = plt_opt.pop('ls', '-.')
    if hysteresis_obj.virgin:
        ax.plot(hysteresis_obj.virgin['field'].v / norm_factor[0],
                hysteresis_obj.virgin['mag'].v / norm_factor[1],
                linestyle=ls, marker='.',
                **plt_opt)


def up_field_branch(ax, hysteresis_obj, norm_factor=[1, 1],
                    plt_idx=0,
                    **plt_opt):
    """
    Plots the up_field branch of a hysteresis
    """
    ls = plt_opt.pop('ls', '-')
    marker = plt_opt.pop('marker', '.')
    ax.plot(hysteresis_obj.up_field['field'].v / norm_factor[0],
            hysteresis_obj.up_field['mag'].v / norm_factor[1],
            linestyle=ls, marker=marker,
            **plt_opt)


def down_field_branch(ax, hysteresis_obj, norm_factor=[1, 1],
                      plt_idx=0,
                      **plt_opt):
    """
    Plots the down_field branch of a hysteresis
    """
    ls = plt_opt.pop('ls', '-')
    marker = plt_opt.pop('marker', '')

    ax.plot(hysteresis_obj.down_field['field'].v / norm_factor[0],
            hysteresis_obj.down_field['mag'].v / norm_factor[1],
            linestyle=ls, marker=marker,
            **plt_opt)


def zero_lines(ax, **plt_opt):
    color = plt_opt.pop('color', '#808080')
    zorder = plt_opt.pop('zorder', 0)

    ax.axhline(0, color=color, zorder=zorder,
               **plt_opt)
    ax.axvline(0, color=color, zorder=zorder,
               **plt_opt)