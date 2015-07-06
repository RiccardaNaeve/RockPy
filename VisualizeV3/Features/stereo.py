__author__ = 'wack'

import numpy as np
from RockPy.Measurements.anisotropy import Anisotropy
from RockPy.Functions.general import XYZ2DIL

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
    lines = []
    # get data from measurement object
    d = m_obj._data['data']
    # check if there is vectorial data
    if d.column_exists('X') and d.column_exists('Y') and d.column_exists('Z'):
        # calculate declination and inclination for each data point
        DIL = np.array(map(XYZ2DIL, d[('X', 'Y', 'Z')].v))
        d = DIL[:, 0]  # declinations
        i = DIL[:, 1]  # inclinations
        iabs = np.fabs(i)

        # plot lines without markers
        plt_opt['markerfacecolor'] = 'white'
        plt_opt['marker'] = ''
        lines.append(ax.plot(*stereomap(d, -iabs), **plt_opt))

        #plot markers upper hemisphere with negative inclinations (hollow)
        dil_neg = DIL[DIL[:, 1] < 0.0]
        d = dil_neg[:, 0]
        i = dil_neg[:, 1]
        plt_opt['marker'] = 'o'
        lines.append(ax.plot(*stereomap(d, i), **plt_opt))

        #plot markers lower hemisphere with positive incliantions (filled)
        dil_pos = DIL[DIL[:, 1] >= 0.0]
        d = dil_pos[:, 0]
        i = dil_pos[:, 1]
        plt_opt['markerfacecolor'] = 'black'
        lines.append(ax.plot(*stereomap(d, -i), **plt_opt))

    return lines, None
