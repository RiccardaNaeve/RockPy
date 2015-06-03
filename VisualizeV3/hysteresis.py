__author__ = 'mike'
import base
import RockPy
from Features import hysteresis

class Hysteresis(base.Generic):
    # _required for searching through samples for plotables
    _required = ['hys']

    def __init__(self, plt_index, plt_input=None, plot=None):
        super(Hysteresis, self).__init__(plt_input=plt_input, plt_index=plt_index, plot=plot)
        self.logger.info('CREATING new hysteresis plot')

    def init_visual(self):
        self.standard_features = [self.feature_hys]
        self.single_features = [self.feature_grid, self.feature_zero_lines]

        self.title = 'Hysteresis'
        self.xlabel = 'Field'
        self.ylabel = 'Moment'



    def feature_hys(self, m_obj, **plt_opt):
        hysteresis.hysteresis(self.ax, m_obj)

    def feature_virgin(self, m_obj, **plt_opt):
        pass

    def feature_grid(self):
        pass

    def feature_zero_lines(self):
        pass