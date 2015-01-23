__author__ = 'mike'


def zero_line(ax, **plt_opt):
    ax.axhline(0, color='#808080',
               **plt_opt)


def backfield(ax, backfield_obj, norm_factor=[1, 1],
              **plt_opt):

    ls = plt_opt.pop('ls', '-')
    marker = plt_opt.pop('marker', '.')
    ax.plot(backfield_obj.remanence['field'].v / norm_factor[0],
            backfield_obj.remanence['mag'].v / norm_factor[1],
            linestyle=ls, marker=marker,
            **plt_opt)