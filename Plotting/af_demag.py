__author__ = 'mike'


def field_mom(ax, afdemag_obj, component='mag', norm_factor=[1, 1],
              plt_idx=0,
              **plt_opt):
    ax.plot(afdemag_obj.data['field'].v / norm_factor[0],
            afdemag_obj.data[component].v / norm_factor[1],
            **plt_opt)


def mdf_line(ax, afdemag_obj, component='mag', norm_factor=[1, 1],
             plt_idx=0,
             **plt_opt):
    mdf = afdemag_obj.result_mdf()
    ax.axvline(mdf.v, linestyle='--', color='#808080')


def mdf_txt(ax, afdemag_obj, component='mag', norm_factor=[1, 1],
            plt_idx=0, y_shift=0, x_shift=0,
            **plt_opt):
    mdf = afdemag_obj.result_mdf()
    ax.text(x_shift+ mdf.v,
            y_shift + 0.5 * (max(afdemag_obj.data[component].v) / norm_factor[1]),
            '%.1f %s' % (mdf.v, 'mT'))  # todo units