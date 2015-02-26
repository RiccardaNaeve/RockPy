__author__ = 'wack'

import base
import RockPy.Measurements.anisotropy
import matplotlib.pylab as plt
from mpl_toolkits.basemap import Basemap
import numpy as np


class Stereo(base.Generic):
    #_required = ['anisotropy']

    def initialize_visual(self):
        super(Stereo, self).initialize_visual()
        #self._required = RockPy.Measurements.anisotropy.Anisotropy
        # create instance of basemap with south polar projection to 90 = E
        self.stereomap = Basemap(projection='spstere', boundinglat=0, lon_0=180, resolution='l', round=True, suppress_ticks=True, rsphere=1)
        self.grid_D_spacing = 30
        self.grid_I_spacing = 15
        self.standard_features = []
        self.single_features = [self.feature_stereogrid, self.feature_stereogridlabels]
        self.add_plot()
        self.ax = self.figs[self.name][0].gca()
        self.xlabel = ''
        self.ylabel = ''

    ''' Features '''

    def feature_stereogrid(self, **plt_opt):
        # set the grid up
        Grid_D = np.arange(-180.0, 180.0, self.grid_D_spacing)
        Grid_I = np.arange(-90.0, 0.0, self.grid_I_spacing)

        # draw parallel and meridian grid, labels are off.
        self.stereomap.drawmeridians(Grid_D)
        self.stereomap.drawparallels(Grid_I, latmax=90)

    def feature_stereogridlabels(self, **plt_opt):
        # draw declination labels
        for D in np.arange(0, 360, self.grid_D_spacing):
            x = (0.45*np.sin(np.deg2rad(D)))+0.5
            y = (0.45*np.cos(np.deg2rad(D)))+0.5
            self.ax.text(x, y, "%i" % D, transform=self.ax.transAxes,
                         horizontalalignment='center', verticalalignment='center')

        # draw inclination labels
        for I in np.arange(self.grid_I_spacing, 90, self.grid_I_spacing):
            (x, y) = self.stereomap(0, -I)
            self.ax.text(x-0.1, y-0.07, "%i" % I, horizontalalignment='center', verticalalignment='center')


    def feature_points(self, m_obj, **plt_opt):
        d, i = (30, 50, 120, 150), (-10, -20, -30, -40)
        lines = self.ax.plot(*self.stereomap(d, i), **plt_opt)
        self._add_line_text_dict(m_obj.sample_obj.name, '_'.join(m_obj.ttypes), '_'.join(map(str, m_obj.tvals)), lines)


    def show(self):
        self.stereomap._check_ax().set_xlim((0.5, -4.5))  # reduce size of plot to make space for labels
        self.stereomap._check_ax().set_ylim((0.5, -4.5))  # reduce size of plot to make space for labels
        super(Stereo, self).show()