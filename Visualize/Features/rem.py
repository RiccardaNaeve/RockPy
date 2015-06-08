__author__ = 'mike'
import numpy as np
from matplotlib.lines import Line2D

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
