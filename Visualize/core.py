__author__ = 'mike'
import numpy as np
import matplotlib.pyplot as plt

def generate_plots(n=3, xsize=5., ysize=5. ):
    """
    Generates a number of subplots that are organized i a way to fit on a landscape plot.
    :param n:
    :param xsize:
    :param ysize:
    :return:
    """
    a = np.floor(n ** 0.5).astype(int)
    b = np.ceil(1. * n / a).astype(int)
    # print "a\t=\t%d\nb\t=\t%d\na*b\t=\t%d\nn\t=\t%d" % (a,b,a*b,n)
    fig = plt.figure(figsize=(xsize * b, ysize * a))
    for i in range(1, n + 1):
        ax = fig.add_subplot(a, b, i)
    # fig.set_tight_layout(True)
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
