__author__ = 'mike'


def grid(ax):
    ax.grid()
    ax.hlines(0.5, 0, 10)
    ax.hlines(0.1, 0, 10)
    ax.vlines(5, 0, 0.6)
    ax.vlines(1.5, 0, 0.6)
    ax.text(0.6, 0.55, 'SD', fontdict={'size': 14, 'color': '#909090'})
    ax.text(2.6, 0.3, 'PSD', fontdict={'size': 14, 'color': '#909090'})
    ax.text(5.9, 0.05, 'MD', fontdict={'size': 14, 'color': '#909090'})