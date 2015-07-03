__author__ = 'wack'

import base
from Features import stereo
from mpl_toolkits.basemap import Basemap

class Stereo(base.Visual):
    # _required for searching through samples for plotables
    #_required = ['hys']

    # def __init__(self, plt_index, plt_input=None, plot=None, name=None):
    #     super(Stereo, self).__init__(plt_input=plt_input, plt_index=plt_index, plot=plot, name=name)

    def init_visual(self):
        self.features = [self.feature_dir]
        self.single_features = [stereo.stereogrid, stereo.stereogridlabels]

        self.stereomap = Basemap(projection='spstere', boundinglat=0, lon_0=180, resolution='l', round=True, suppress_ticks=True, rsphere=1)
        self.grid_D_spacing = 30
        self.grid_I_spacing = 15

        self.xlabel = ''
        self.ylabel = ''

    def feature_dir(self, mobj, **plt_opt):
        plt_opt.pop('marker')
        stereo.dir(self.ax, mobj, **plt_opt)
        return 'multiple'

