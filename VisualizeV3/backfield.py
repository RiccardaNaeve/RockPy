__author__ = 'mike'
import base
from Features import backfield

class Backfield(base.Visual):

    # _required for searching through samples for plottables
    _required = ['backfield']

    def __init__(self, plt_index, plt_input = None, plot = None):
        super(Backfield, self).__init__(plt_input=plt_input, plt_index = plt_index, plot = plot)
        self.logger.info('CREATING new backfield plot')

    def init_visual(self):
        self.features = []
        self.single_features = []

        self.title = 'Backfield'
        self.xlabel = 'Field'
        self.ylabel = 'Moment'

    def plt_visual(self):
        self.add_standard()

    def feature_data(self, m_obj, **plt_opt):
        plt_opt.pop('marker')
        hysteresis.hysteresis(self.ax, m_obj, **plt_opt)