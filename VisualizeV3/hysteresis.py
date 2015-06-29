__author__ = 'mike'
import base
import RockPy
from Features import hysteresis


class Hysteresis(base.Visual):
    # _required for searching through samples for plotables
    _required = ['hys']

    # def __init__(self, plt_index, plt_input=None, plot=None, name=None):
    #     super(Hysteresis, self).__init__(plt_input=plt_input, plt_index=plt_index, plot=plot, name=name)

    def init_visual(self):
        self.features = [self.feature_hys]
        self.single_features = [self.feature_grid, self.feature_zero_lines]

        self.xlabel = 'Field'
        self.ylabel = 'Moment'

    def feature_hys(self, mobj, **plt_opt):
        plt_opt.pop('marker')
        hysteresis.hysteresis(self.ax, mobj, **plt_opt)
        return 'multiple'

    def feature_virgin(self, m_obj, **plt_opt):
        pass
        return 'multiple'
