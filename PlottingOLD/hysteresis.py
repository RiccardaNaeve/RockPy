__author__ = 'mike'


def virgin_branch(ax, hysteresis_obj, norm_factor=[1, 1],
                 plt_idx=0,
                 **plt_opt):
    """
    Plots the virgin branch of a hysteresis
    """
    ls = plt_opt.pop('ls', '-.')
    marker = plt_opt.pop('marker', '.')
    if hysteresis_obj.data['virgin']:
        std, = ax.plot(hysteresis_obj.data['virgin']['field'].v / norm_factor[0],
                hysteresis_obj.data['virgin']['mag'].v / norm_factor[1],
                linestyle=ls, marker=marker,
                **plt_opt)

    return std.get_color()

def up_field_branch(ax, hysteresis_obj, norm_factor=[1, 1],
                    plt_idx=0,
                    **plt_opt):
    """
    Plots the up_field branch of a hysteresis
    """
    ls = plt_opt.pop('ls', '-')
    marker = plt_opt.pop('marker', '.')
    ax.plot(hysteresis_obj.data['up_field']['field'].v / norm_factor[0],
            hysteresis_obj.data['up_field']['mag'].v / norm_factor[1],
            linestyle=ls, marker=marker,
            **plt_opt)


def down_field_branch(ax, hysteresis_obj, norm_factor=[1, 1],
                      plt_idx=0,
                      **plt_opt):
    """
    Plots the down_field branch of a hysteresis
    """
    ls = plt_opt.pop('ls', '-')
    marker = plt_opt.pop('marker', '.')

    ax.plot(hysteresis_obj.data['down_field']['field'].v / norm_factor[0],
            hysteresis_obj.data['down_field']['mag'].v / norm_factor[1],
            linestyle=ls, marker=marker,
            **plt_opt)


def zero_lines(ax, **plt_opt):
    color = plt_opt.pop('color', 'k')
    zorder = plt_opt.pop('zorder', 0)

    ax.axhline(0, color=color, zorder=zorder,
               **plt_opt)
    ax.axvline(0, color=color, zorder=zorder,
               **plt_opt)


def hysteresis(ax, hysteresis_obj, norm_factor=[1, 1],
               plt_idx=0,
               **plt_opt):
    zero_lines(ax)
    c = virgin_branch(ax, hysteresis_obj, norm_factor, plt_idx, **plt_opt)
    if 'label' in plt_opt:
        plt_opt.pop('label')
    down_field_branch(ax, hysteresis_obj, norm_factor, plt_idx, color = c, **plt_opt)
    up_field_branch(ax, hysteresis_obj, norm_factor, plt_idx, color = c, **plt_opt)
