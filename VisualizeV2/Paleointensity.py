__author__ = 'mike'
import base
import matplotlib.pyplot as plt
import RockPy.Plotting
import RockPy as RP
import RockPy.Measurements.thellier


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

    def plotting(self, sample):
        pass


class Arai(base.Generic):
    _required = ['thellier']
    def initialize_visual(self):
        super(Arai, self).initialize_visual()
        self._required = RockPy.Measurements.thellier.Thellier
        self.add_plot()

    def plotting(self, sample):
        pass


class Multiple(base.Generic):
    _required = ['thellier']
    def initialize_visual(self):
        arai = Arai(plot_samples=self.study)
        dunlop = Dunlop(plot_samples=self.study)
        super(Multiple, self).initialize_visual()
        self.add_plot(plot=arai)
        self.add_plot(plot=dunlop)


def test():
    sample = RP.Sample(name='test_sample')
    sample.add_measurement(mtype='thellier', mfile='../Tutorials/test_data/NLCRY_Thellier_test.TT', machine='cryomag')
    Plot = Multiple(plot_samples=sample)
    Plot.show()
    # print 'test', Plot.ls_source


if __name__ == '__main__':
    test()