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

def dunlop_std(ax, thellier_obj, component='mag', norm_factor=None,
           **plt_opt):
    if not norm_factor: norm_factor = [1.0, 1.0]
    c = ['r', 'g', 'b']
    for i, v in enumerate(['sum', 'th', 'ptrm']):
        ax.fill_between(getattr(thellier_obj, v)['temp'].v / norm_factor[0],
                        (getattr(thellier_obj, v)[component].v + getattr(thellier_obj, v)[component].e) / norm_factor[1],
                        (getattr(thellier_obj, v)[component].v - getattr(thellier_obj, v)[component].e) / norm_factor[1],
                        color = c[i], alpha=0.05)
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

def difference_std(ax, thellier_obj_A, thellier_obj_B, component='mag', norm_factor=None,
               **plt_opt):
    if not norm_factor: norm_factor = [1.0, 1.0]

    c = ['r', 'g', 'b']

    for i, v in enumerate(['th', 'ptrm']):
        plt_opt = {'color': c[i+1]}

        aux = getattr(thellier_obj_A, v) - getattr(thellier_obj_B,v)

        vars = aux['variable'].v

        e1 = getattr(thellier_obj_A, v)
        idx1 = [i1 for i1,v1 in enumerate(e1['variable'].v) if v1 in vars]
        e1 = e1.filter_idx(idx1)
        e2 = getattr(thellier_obj_B, v)
        idx2 = [i2 for i2,v2 in enumerate(e2['variable'].v) if v2 in vars]
        e2 = e2.filter_idx(idx2)
        error = e1[component].e + e2[component].e

        aux['mag'] = aux.magnitude(('x', 'y', 'z'))

        ax.fill_between(aux['temp'].v / norm_factor[0],
                        (aux[component].v+error)/ norm_factor[1],
                        (aux[component].v-error)/ norm_factor[1],
                        color = c[i+1],
                        alpha =0.05,
                        )
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
