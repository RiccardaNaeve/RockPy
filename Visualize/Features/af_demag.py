__author__ = 'mike'
import RockPy
# RockPy.
def field_mom(ax, afdemag_obj, component='mag', **plt_opt):
    marker = plt_opt.pop('marker', '.')
    linestyle = plt_opt.pop('linestype', '-')

    lines = ax.plot(afdemag_obj.data['data']['field'].v,
                    afdemag_obj.data['data'][component].v,
                    linestyle=linestyle, marker=marker,
                    # label=' '.join([afdemag_obj.sample_obj.name, afdemag_obj.mag_method,
                                    # afdemag_obj.get_series_labels(),
                                    # afdemag_obj.suffix]),
                    **plt_opt)
    return lines