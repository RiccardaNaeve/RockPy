__author__ = 'mike'
import base
import matplotlib.pyplot as plt
import RockPy.PlottingOLD
import RockPy as RP
import RockPy.Measurements.thellier

from RockPy.Visualize.Features import generic, arai
from RockPy.Visualize.Features.day import day_grid
from copy import deepcopy


class Tutorial(base.Generic):
    _required = None
    """
    Tutorial class for how to create your own plot

    1. initialize plot: write
       def initialize_plot(self)

    2. define prerequisites

    3. add_plot

    4. plotting
    """


class Decay(base.Generic):
    _required = ['thellier']

    def initialize_visual(self):
        self.add_plot()


class Dunlop(base.Generic):
    _required = ['thellier']

    def initialize_visual(self):
        super(Dunlop, self).initialize_visual()
        self._required = RockPy.Measurements.thellier.Thellier
        self.add_plot()


class Arai(base.Generic):
    _required = ['thellier']

    def initialize_visual(self):
        super(Arai, self).initialize_visual()
        self._required = RockPy.Measurements.thellier.Thellier
        self.standard_features = [self.feature_points, self.feature_arai_stdev]
        self.single_features = [self.feature_grid]
        self.add_plot()
        self.ax = self.figs[self.name][0].gca()
        self.xlabel = 'NRM remaining'
        self.ylabel = 'pTRM gained'

    ''' Features '''

    def feature_points(self, m_obj, **plt_opt):
        lines = arai.arai_points(self.ax, m_obj, **plt_opt)
        self._add_line_text_dict(m_obj.sample_obj.name, '_'.join(m_obj.ttypes), '_'.join(map(str, m_obj.tvals)), lines)

    def feature_arai_stdev(self, m_obj, **plt_opt):
        lines = arai.arai_stdev(self.ax, m_obj, **plt_opt)
        self._add_line_text_dict(m_obj.sample_obj.name, '_'.join(m_obj.ttypes), '_'.join(map(str, m_obj.tvals)), lines)



def test():
    sample = RP.Sample(name='test_sample')
    sample.add_measurement(mtype='thellier', mfile='../Tutorials/test_data/NLCRY_Thellier_test.TT', machine='cryomag')
    Plot = Arai(plot_samples=sample)
    Plot.show()
    # print 'test', Plot.ls_source


if __name__ == '__main__':
    test()