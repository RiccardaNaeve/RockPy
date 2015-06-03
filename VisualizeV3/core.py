__author__ = 'mike'
import numpy as np
import matplotlib.pyplot as plt

def scatter_xy(ax, m_obj, x_dtype, y_dtype, x_component, y_component, **plt_opt):
    pass

def generate_plots(n=3, xsize=5., ysize=5. , tight_layout=False):
    """
    Generates a number of subplots that are organized i a way to fit on a landscape plot.

    Parameter
    ---------
       n: int
          number of plots to be generated
       xsize: float
          size along x for each plot
       ysize: float
          size along y for each plot
       tight_layout: bool
          using tight_layout (True) or not (False)

    Returns
    -------
       fig matplotlib figure instance
    """
    a = np.floor(n ** 0.5).astype(int)
    b = np.ceil(1. * n / a).astype(int)
    # print "a\t=\t%d\nb\t=\t%d\na*b\t=\t%d\nn\t=\t%d" % (a,b,a*b,n)
    fig = plt.figure(figsize=(xsize * b, ysize * a))
    for i in range(1, n + 1):
        ax = fig.add_subplot(a, b, i)
    fig.set_tight_layout(tight_layout)
    return fig

def get_subplot(fig, i):
    """
    Returns the axis object i from the figure that has been created with generate_plots
    :param fig:
    :param i:
    :return:
    """
    n = len(fig.axes)
    a = np.floor(n ** 0.5).astype(int)
    b = np.ceil(1. * n / a).astype(int)
    ax = fig.add_subplot(a, b, i + 1)
    return ax

def get_min_max_all_ax(fig):
    """
    gets the minimim and maximum for xlim and of ylim
    """
    xout = []
    yout = []

    #get xlimits
    for ax in fig.axes:
        xout.append(ax.get_xlim())
        yout.append(ax.get_ylim())

    xout = np.array(xout)
    yout = np.array(yout)
    return [np.min(xout), np.max(xout)], [np.min(yout), np.max(yout)]

def set_lim_all_ax(fig, xlim=None, ylim=None):
    """
    Sets the ylimits for all plots of the specified figure

    Parameters
    ----------
    """

    for ax in fig.axes:
        if xlim:
            ax.set_xlim(xlim)
        if ylim:
            ax.set_ylim(ylim)

def create_heat_color_map(value_list, reverse=False):
    """
    takes a list of values and creates a list of colors from blue to red (or reversed if reverse = True)

    :param value_list:
    :param reverse:
    :return:
    """
    r = np.linspace(0, 255, len(value_list)).astype('int')
    r = [hex(i)[2:-1].zfill(2) for i in r]
    # r = [i.encode('hex') for i in r]
    b = r[::-1]

    out = ['#%2s' % r[i] + '00' + '%2s' % b[i] for i in range(len(value_list))]
    if reverse:
        out = out[::-1]
    return out