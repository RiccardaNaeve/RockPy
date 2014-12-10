__author__ = 'mike'
import base
import matplotlib.pyplot as plt
import Plotting
import RockPy as RP


class Plot(base.Generic):
    """
    Tutorial class for how to create your own plot

    1. initialize plot: write
       def initialize_plot(self)

    2. define prerequisites

    3. add_plot

    4. plotting
    """


class Decay(base.Generic):
    def initialize_plot(self):
        super(Decay, self).initialize_plot()
        self.add_fig()

class Dunlop(base.Generic):
    def initialize_plot(self):
        super(Dunlop, self).initialize_plot()
        self.add_fig()

    def plotting(self, sample):
        print 'dunlop'

class Arai(base.Generic):
    def initialize_plot(self):
        super(Arai, self).initialize_plot()
        self.add_fig()

    def plotting(self, sample):
        print 'arai'

class Multiple(base.Generic):
    def initialize_plot(self):
        arai = Arai(plot_samples=self.study)
        dunlop = Dunlop(plot_samples=self.study)
        super(Multiple, self).initialize_plot()
        self.add_fig(fig=arai)
        self.add_fig(fig=dunlop)

def test():
    sample = RP.Sample(name='test_sample')
    sample.add_measurement(mtype='thellier', mfile='../testing/test_data/NLCRY_Thellier_test.TT', machine='cryomag')
    Plot = Multiple(plot_samples=sample)
    Plot.show()
    # print 'test', Plot.ls_source


if __name__ == '__main__':
    test()