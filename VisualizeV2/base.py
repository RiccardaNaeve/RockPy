__author__ = 'volk'
import logging
import os
import sys

import numpy as np
import matplotlib.pyplot as plt

import RockPy as rp
import RockPy.Functions
from matplotlib.lines import Line2D
import copy


RockPy.Functions.general.create_logger('RockPy.VISUALIZE')


class Generic(object):
    def __init__(self, plot_samples=None, norm=None,
                 plot='show', folder=None, name=None,
                 create_fig=True, create_ax=True,
                 fig_opt=dict(), plt_opt=dict(),
                 **options):

        self.log = logging.getLogger('RockPy.VISUALIZE.' + type(self).__name__)
        self.name = type(self).__name__
        self.existing_visuals = {i.__name__: i for i in Generic.inheritors()}

        self._required = {}
        self._group_from_list(plot_samples)
        self._plots = {}

        self.color_source = options.pop('color_source', self.hierarchy[self.plot_samples_type])
        self.marker_source = options.pop('marker_source', self.hierarchy[self.plot_samples_type])
        self.ls_source = options.pop('linestyle_source', self.hierarchy['sample'])

        self._fig_opt = fig_opt

        self.initialize_plot()

        for sample in self.samples:
            if self.meets_requirements(sample):
                self.plotting(sample)

    @property
    def hierarchy(self):
        h = {'study': 'sample_group',
             'sample_group': 'sample',
             'sample': 'measurement',
             'measurement': 'treatment',
             'none': None}
        return h


    @property
    def plot_dict(self):
        pdict = {'colors': np.tile(['b', 'g', 'r', 'c', 'm', 'y', 'k'], 10),
                 'linestyles': np.tile(['-', '--', ':', '-.'], 10),
                 'markers': np.tile(['.', 'v', '^', '<', '>', '1', '2', '3', '4', '8', 's', 'p', '*', 'h',
                                     'H', '+', 'x', 'D', 'd', '|', '_'], 10),
                 'markersizes': np.tile([5, 4, 4, 4, 4], 10)}
        return pdict

    @property
    def required(self):
        if isinstance(self._required, dict):
            return self._required
        else:
            return {self.name: self._required}

    @property
    def require_list(self):
        return [j for i in self.required for j in self.required[i]]

    def initialize_plot(self):
        pass

    def meets_requirements(self, sample_obj):
        """
        checks if prerequsits are met for a certain plot

        :param sample_obj:
        :return:
        """
        # measurements = sample_obj.get_measurements(mtype=self.require_list)
        out = []
        for i in self.require_list:
            if i in sample_obj.mtypes:
                out.append(True)
            else:
                out.append(False)
        if all(out):
            return True
        else:
            return False

    # ## TESTED
    @property
    def sample_names(self):
        return self.plot_samples.sample_names

    @property
    def samples(self):
        return self.plot_samples.sample_list

    @property
    def sample_nr(self):
        return len(self.plot_samples.sample_list)

    def add_plot(self, label=None, **fig_opt):
        if not fig_opt:
            fig_opt = self._fig_opt
        if not 'figsize' in fig_opt:
            fig_opt.update({'figsize': (11.69, 8.27)})
        if not label:
            label = len(self._plots)
        self._plots.update({label: self.create_fig(**fig_opt)})
        return self.plots[label]

    def get_fig(self, label):
        return self.plots[label]

    def add_fig(self, fig):
        if isinstance(fig, Generic):
            self.plots.update(fig.plots)
            self._required.update(fig.required)

    @property
    def plots(self):
        return self._plots


    @property
    def folder(self):
        return self._folder

    @folder.setter
    def folder(self, folder):
        if folder is None:
            from os.path import expanduser

            self._folder = expanduser("~") + '/Desktop/'
        else:
            self._folder = folder

    def _group_from_list(self, s_list):
        """
        takes sample_list argument and checks if it is sample, list(samples) or RockPy.sample_group
        """
        # self.plot_samples_type = ''
        if isinstance(s_list, RockPy.SampleGroup):
            self.plot_samples = s_list
            self.plot_samples_type = 'sample_group'

        if isinstance(s_list, list):
            self.log.debug('CONVERTING list(sample) -> RockPy.SampleGroup(Sample)')
            self.plot_samples = rp.SampleGroup(sample_list=s_list)
            self.plot_samples_type = 'sample'

        if isinstance(s_list, rp.Sample):
            self.log.debug('CONVERTING sample -> list(sample) -> RockPy.SampleGroup(Sample)')
            self.plot_samples = rp.SampleGroup(sample_list=[s_list])
            self.plot_samples_type = 'sample'


    def create_fig(self, **fig_opt):
        fig = plt.figure(**fig_opt)
        return fig

    def plotting(self, sample):
        pass

    def show(self):
        for label, fig in self.plots.iteritems():
            axes = fig.gca()
            axes.set_title(label)

        plt.show()

    @classmethod
    def inheritors(cls):
        subclasses = set()
        work = [cls]
        while work:
            parent = work.pop()
            for child in parent.__subclasses__():
                if child not in subclasses:
                    subclasses.add(child)
                    work.append(child)
        return subclasses