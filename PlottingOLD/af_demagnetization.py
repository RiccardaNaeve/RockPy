__author__ = 'mike'
import numpy as np
from matplotlib.lines import Line2D

def field_mom(ax, afdemag_obj, component='mag', norm_factor=None,
              plt_idx=0,
              **plt_opt):

    if norm_factor is None:
        norm_factor = [1, 1]
    ax.plot(afdemag_obj.data['data']['field'].v / norm_factor[0],
            afdemag_obj.data['data'][component].v / norm_factor[1],
            **plt_opt)


def diff_fill(ax, afdemag_obj, component='mag', norm_factor=None,
              smoothing=1, diff=2, plt_idx=0,
              **plt_opt):

    if norm_factor is None:
        norm_factor = [1, 1]

    lim = ax.get_ylim()
    data = afdemag_obj.data
    label = 'd' + str(diff) + ' ' + component + '/d' + str(diff) + ' ' + 'field'

    for i in range(diff):
        data = data.derivative(dependent_var=component, independent_var='field', smoothing=smoothing)

    x = data['field'].v
    x *= norm_factor[0]

    y = data[component].v
    y /= max(abs(y))/lim[1]
    ax.fill_between(x, 0, y, color = '#808080', alpha=0.1, label = label)


def mdf_line(ax, afdemag_obj, component='mag', norm_factor=[1, 1],
             plt_idx=0,
             **plt_opt):
    plt_opt.update({'zorder':0})

    mdf = afdemag_obj.result_mdf()
    ax.axvline(mdf.v, linestyle='--', color='#808080')


def mdf_txt(ax, afdemag_obj, component='mag', norm_factor=[1, 1],
            plt_idx=0, y_shift=0, x_shift=0,
            **plt_opt):
    mdf = afdemag_obj.result_mdf()
    ax.text(x_shift + mdf.v,
            y_shift + 0.5 * (max(afdemag_obj.data[component].v) / norm_factor[1]),
            '%.1f %s' % (mdf.v, 'mT'))  # todo units


def d_log_af(af_demag_obj1, af_demag_obj2, ax,
             component='m', norm_factor=[1, 1],
             **plt_opt):

    #only get af-data for for fields in both objects
    x_aux = af_demag_obj1.data.equal_var(af_demag_obj2.data)
    y_aux = af_demag_obj2.data.equal_var(af_demag_obj1.data)

    name = af_demag_obj1.sample_obj.name

    x = getattr(x_aux, component)
    y = getattr(y_aux, component)

    std, = ax.plot(x[1:] / norm_factor[0], y[1:] / norm_factor[1], 'o-', linewidth = 2, label=name)
    ax.plot(x[0:2] / norm_factor[0:1], y[0:2] / norm_factor[1], 'o--', linewidth = 2, color = std.get_color(), alpha =0.8)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.axis('scaled')
    return ax


def d_log_diff_af(af_demag_obj1, af_demag_obj2, ax,
             component='mag', norm_factor=[1, 1],
             out='show', folder=None, name='output.pdf',
             plt_opt=dict(),
             **options):

    #only get af-data for for fields in both objects
    x = af_demag_obj1.data.derivative(dependent_var=component, independent_var='field')[component].v
    y = af_demag_obj2.data.derivative(dependent_var=component, independent_var='field')[component].v

    name = af_demag_obj1.sample_obj.name

    # x = getattr(x_aux, component)
    # y = getattr(y_aux, component)

    std, = ax.plot(x[1:] / norm_factor[0], y[1:] / norm_factor[1], 'o-', linewidth = 2, label=name)
    ax.plot(x[0:2] / norm_factor[0:1], y[0:2] / norm_factor[1], 'o--', linewidth = 2, color = std.get_color(), alpha =0.8)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.axis('scaled')
    return ax

def d_log_iso_lines(ax):
    x_lim = np.log10(ax.get_xlim())
    y_lim = np.log10(ax.get_ylim())
    x_new = [10**i for i in np.arange(x_lim[0], x_lim[-1]+2)]
    y_new = [10**i for i in np.arange(x_lim[0], x_lim[-1]+2)]

    for j in range(len(x_new)):
        y = np.linspace(y_new[0]/1000, y_new[-1-j],2)
        x = np.linspace(x_new[j]/1000, x_new[-1],2)
        line = Line2D(x,y, linewidth=1, color = 'k', linestyle='--', alpha=0.8, zorder=1)
        if j < len(x_new)-2:
            ax.text(x_new[j], y_new[0]/100*1.2, '$10^{%i}$' % np.log10(np.mean(y/x)/100),
                verticalalignment='bottom', horizontalalignment='left',
                color='k', fontsize=12, rotation = 45)

        ax.add_line(line)

    for j in range(1,len(y_new)):
        y = np.linspace(y_new[j]/1000, y_new[-1],2)
        x = np.linspace(x_new[0]/1000, x_new[-1-j],2)
        line = Line2D(x,y, linewidth=1, color = 'k', linestyle='--', alpha=0.8, zorder=1)
        if j < len(x_new)-2:
            ax.text(x_new[0], y_new[j]/100*1.2, '$10^{%i}$' % np.log10(np.mean(y/x)/100),
                    verticalalignment='bottom', horizontalalignment='left',
                    color='k', fontsize=12, rotation = 45, zorder=1)
            ax.add_line(line)
    return ax

def REM_line(af_demag_obj1, af_demag_obj2, ax,
         component='m', norm_factor=[1, 1],
         out='show', folder=None, name='output.pdf',
         plt_opt=dict(),
         **options):

    irm_aux = af_demag_obj1.data.equal_var(af_demag_obj2.data)
    nrm_aux = af_demag_obj2.data.equal_var(af_demag_obj1.data)

    name = af_demag_obj1.sample_obj.name

    irm = getattr(irm_aux, component)
    nrm = getattr(nrm_aux, component)

    data = nrm[0]/irm[0]
    x_lim = ax.get_xlim()
    ax.plot(x_lim, [data, data], '-',alpha=0.8, linewidth =1, **plt_opt)