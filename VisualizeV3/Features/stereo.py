__author__ = 'wack'

import numpy as np

'''
stereo features
'''


def stereogrid(ax, stereomap, grid_D_spacing, grid_I_spacing, **plt_opt):
    # set the grid up
    Grid_D = np.arange(-180.0, 180.0, grid_D_spacing)
    Grid_I = np.arange(-90.0, 0.0, grid_I_spacing)

    lines = []

    # draw parallel and meridian grid, labels are off.
    lines.extend(stereomap.drawmeridians(Grid_D))
    lines.extend(stereomap.drawparallels(Grid_I, latmax=90))

    # line dictionary
    return lines, None

def stereogridlabels(ax, stereomap, grid_D_spacing, grid_I_spacing, **plt_opt):
    # draw declination labels
    lines = []
    for D in np.arange(0, 360, grid_D_spacing):
        x = (0.55*np.sin(np.deg2rad(D)))+0.5
        y = (0.55*np.cos(np.deg2rad(D)))+0.5
        lines.append(ax.text(x, y, "%i" % D, transform=ax.transAxes,
                     horizontalalignment='center', verticalalignment='center'))

    # draw inclination labels
    for I in np.arange(grid_I_spacing, 90, grid_I_spacing):
        (x, y) = stereomap(0, -I)
        lines.append(ax.text(x-0.1, y-0.07, "%i" % I, horizontalalignment='center', verticalalignment='center'))

    return lines, None


def stereodirs(ax, stereomap, m_obj, **plt_opt):
    '''
    :param m_obj: plot single direction
    :param plt_opt:
    :return:
    '''
    # example values
    d, i = (30, 50, 120, 150), (-10, -20, -30, -40)
    lines = ax.plot(*stereomap(d, i), **plt_opt)

    return lines, None
