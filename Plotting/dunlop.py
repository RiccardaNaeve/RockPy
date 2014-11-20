__author__ = 'mike'
import numpy as np

def dunlop(ax, thellier_obj, component='mag', norm_factor=None,
           **plt_opt):
    if not norm_factor: norm_factor = [1.0, 1.0]
    c = ['r', 'g', 'b']
    for i, v in enumerate(['sum', 'th', 'ptrm']):

        plt_opt.update({'label': v})
        plt_opt.update({'color': c[i]})
        if thellier_obj.treatments:
            plt_opt['label'] += ' '.join([j.label for j in thellier_obj.treatments])

        ax.plot(getattr(thellier_obj, v)['temp'].v / norm_factor[0],
                getattr(thellier_obj, v)[component].v / norm_factor[1], **plt_opt)
    return ax


def difference(ax, thellier_obj_A, thellier_obj_B, component='mag', norm_factor=None,
               **plt_opt):
    if not norm_factor: norm_factor = [1.0, 1.0]
    c = ['r', 'g', 'b']
    for i, v in enumerate(['th', 'ptrm']):
        plt_opt.update({'color': c[i+1]})
        aux = getattr(thellier_obj_A, v) - getattr(thellier_obj_B,v)
        aux['mag'] = aux.magnitude(('x', 'y', 'z'))

        ax.plot(aux['temp'].v / norm_factor[0],
                aux[component].v / norm_factor[1], **plt_opt)
    return ax


def derivative(ax, thellier_obj, component='mag', norm_factor=None,
               interpolate=False, diff = 1,
           **plt_opt):
    if not norm_factor: norm_factor = [1.0, 1.0]
    c = ['r', 'g', 'b']
    for i, v in enumerate(['sum', 'th', 'ptrm']):
        plt_opt.update({'label': v})
        plt_opt.update({'color': c[i]})
        if thellier_obj.treatments:
            plt_opt['label'] += ' '.join([j.label for j in thellier_obj.treatments])
        data = getattr(thellier_obj, v)
        if interpolate:
            temps = data['temp'].v
            data = data.interpolate(np.linspace(min(temps),max(temps),100), includesourcedata=True, kind='linear').sort()
        for i in range(diff):
            data = data.derivative(component, 'temp')
        ax.plot(data['temp'].v / norm_factor[0],
                data[component].v / norm_factor[1], **plt_opt)
    return ax
