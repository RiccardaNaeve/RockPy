__author__ = 'mike'


def field_mom(ax, afdemag_obj, component='mag', norm_factor=[1, 1],
              plt_idx=0,
              **plt_opt):
    ax.plot(afdemag_obj.data['field'].v / norm_factor[0],
            afdemag_obj.data[component].v / norm_factor[1],
            **plt_opt)


def diff_fill(ax, afdemag_obj, component='mag', norm_factor=[1, 1],
              smoothing=1, diff=2, plt_idx=0,
              **plt_opt):
    lim = ax.get_ylim()
    data = afdemag_obj.data
    label = 'd' + str(diff) + ' ' + component + '/d' + str(diff) + ' ' + 'field'

    for i in range(diff):
        data = data.derivative(dependent_var=component, independent_var='field', smoothing=smoothing)

    x = data['field'].v
    x *= norm_factor[0]

    y = data[component].v
    y /= max(abs(y))
    ax.fill_between(x, 0, y, color = '#808080', alpha=0.1, label = label)


def mdf_line(ax, afdemag_obj, component='mag', norm_factor=[1, 1],
             plt_idx=0,
             **plt_opt):
    mdf = afdemag_obj.result_mdf()
    ax.axvline(mdf.v, linestyle='--', color='#808080')


def mdf_txt(ax, afdemag_obj, component='mag', norm_factor=[1, 1],
            plt_idx=0, y_shift=0, x_shift=0,
            **plt_opt):
    mdf = afdemag_obj.result_mdf()
    ax.text(x_shift + mdf.v,
            y_shift + 0.5 * (max(afdemag_obj.data[component].v) / norm_factor[1]),
            '%.1f %s' % (mdf.v, 'mT'))  # todo units

