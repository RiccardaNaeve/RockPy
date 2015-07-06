__author__ = 'wack'

import base
from Features import stereo
from mpl_toolkits.basemap import Basemap

class Stereo(base.Visual):
    # _required for searching through samples for plotables
    _required = ['anisotropy']

    def init_visual(self):
        self.features = [self.feature_stereodirs]
        self.single_features = [self.feature_stereogrid, self.feature_stereogridlabels]

        self.stereomap = Basemap(projection='spstere', boundinglat=0, lon_0=180, resolution='l', round=True, suppress_ticks=True, rsphere=1)
        self.grid_D_spacing = 30
        self.grid_I_spacing = 15

        self.xlabel = ''
        self.ylabel = ''

    def feature_stereogrid(self, **plt_opt):
        stereo.stereogrid(self.ax, self.stereomap, self.grid_D_spacing, self.grid_I_spacing, **plt_opt)
        return 'single'

    def feature_stereogridlabels(self, **plt_opt):
        stereo.stereogridlabels(self.ax, self.stereomap, self.grid_D_spacing, self.grid_I_spacing, **plt_opt)
        return 'single'

    def feature_stereodirs(self, mobj, **plt_opt):
        stereo.stereodirs(self.ax, self.stereomap, mobj, **plt_opt)
        return 'multiple'


