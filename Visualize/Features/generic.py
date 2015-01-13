__author__ = 'mike'


def grid(ax, **options):
    line_out = ax.grid(zorder = 0)
    return line_out


def zero_lines(ax, **options):
    x = ax.get_xlim()
    y = ax.get_ylim()
    line_out = []
    line_out.append(ax.hlines(0, x[0], x[1], zorder = 0))
    line_out.append(ax.vlines(0, y[0], y[1], zorder = 0))
    ax.set_xlim(x)
    ax.set_ylim(y)
    return line_out