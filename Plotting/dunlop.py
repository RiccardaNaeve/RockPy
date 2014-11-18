__author__ = 'mike'


def dunlop(ax, thellier_obj, component='mag', norm_factor=None,
           **plt_opt):
    if not norm_factor: norm_factor = [1.0, 1.0]
    # print thellier_obj.sample_obj.name, norm_factor
    for i in ['sum', 'th', 'ptrm']:

        plt_opt['label'] = i

        if thellier_obj.treatments:
            plt_opt['label'] += ' '.join([j.label for j in thellier_obj.treatments])

        ax.plot(getattr(thellier_obj, i)['temp'].v / norm_factor[0],
                getattr(thellier_obj, i)[component].v / norm_factor[1], **plt_opt)
    return ax

