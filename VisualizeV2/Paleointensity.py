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


class Dunlop(base.Generic):
    def initialize_plot(self):
        super(Dunlop, self).initialize_plot()
        self.std_reference = 'nrm'
        self.std_parameter = {'t_min': 20, 't_max': 700, 'component': 'mag'}
        self._required = ['thellier']
        self.plot = self.add_plot(label='dunlop')
        self.ax = self.plots['dunlop'].add_subplot(111)


    def plotting(self, sample):
        for m in sample.get_measurements(mtype=self.require_list):
            Plotting.dunlop.dunlop(self.ax, m)


class Arai(base.Generic):
    def initialize_plot(self):
        super(Arai, self).initialize_plot()
        self.std_reference = 'nrm'
        self.std_parameter = {'t_min': 20, 't_max': 700, 'component': 'mag'}
        self._required = ['thellier']
        self.plot = self.add_plot(label='arai')
        self.ax = self.plots['arai'].add_subplot(111)

    def plotting(self, sample):
        for m in sample.get_measurements(mtype=self.require_list):
            # plt_opt = self.get_plt_opt(measurement=m)
            Plotting.arai.arai_points(self.ax, m, self.parameter)


class Multiple(base.Generic):
    def initialize_plot(self):
        arai = Arai(plot_samples=self.study)
        dunlop = Dunlop(plot_samples=self.study)
        super(Multiple, self).initialize_plot()
        self.add_fig(arai)
        self.add_fig(dunlop)

def test():
    sample = RP.Sample(name='test_sample')
    sample.add_measurement(mtype='thellier', mfile='../testing/test_data/NLCRY_Thellier_test.TT', machine='cryomag')
    Plot = Multiple(plot_samples=sample)
    Plot.show()
    # print 'test', Plot.ls_source


if __name__ == '__main__':
    test()