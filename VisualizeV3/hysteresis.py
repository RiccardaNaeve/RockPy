__author__ = 'mike'
import base
import RockPy
from Features import hysteresis

class Hysteresis(base.Generic):
    # _required for searching through samples for plotables
    _required = ['hys']

    def __init__(self, plt_index, plt_input=None, plot=None, name=None):
        super(Hysteresis, self).__init__(plt_input=plt_input, plt_index=plt_index, plot=plot)
        self.logger.info('CREATING new hysteresis plot')



    def init_visual(self):
        self.standard_features = [self.feature_hys]
        self.single_features = [self.feature_grid, self.feature_zero_lines]

        self.xlabel = 'Field'
        self.ylabel = 'Moment'



    def feature_hys(self, m_obj, **plt_opt):
        plt_opt.pop('marker')
        hysteresis.hysteresis(self.ax, m_obj, **plt_opt)

    def feature_virgin(self, m_obj, **plt_opt):
        pass

    def feature_grid(self):
        pass

    def feature_zero_lines(self, **plt_opt):
        color = plt_opt.pop('color', 'k')
        zorder = plt_opt.pop('zorder', 0)

        self.ax.axhline(0, color=color, zorder=zorder,
                   **plt_opt)
        self.ax.axvline(0, color=color, zorder=zorder,
                   **plt_opt)
