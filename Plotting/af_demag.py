__author__ = 'mike'


def field_mom(ax, afdemag_obj, component='mag', norm_factor=[1, 1],
              plt_idx=0,
              **plt_opt):
    ax.plot(afdemag_obj.data['field'].v / norm_factor[0],
            afdemag_obj.data[component].v / norm_factor[1],
            **plt_opt)


def mdf_line(ax, norm_factor=[1, 1],
             plt_idx=0,
             **plt_opt):
    ax.axhline(0.5 * norm_factor[1], color='#808080')