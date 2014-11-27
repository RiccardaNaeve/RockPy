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
    def __init__(self, sample_group=None, norm=None,
                 plot='show', folder=None, name=None,
                 create_fig=True, create_ax=True,
                 fig_opt=dict(), plt_opt=dict(),
                 **options):

        self.log = logging.getLogger('RockPy.VISUALIZE.' + type(self).__name__)
        self.name = type(self).__name__
        self.existing_visuals = {i.__name__:i for i in Generic.inheritors()}

        self._group_from_list(sample_group)
        self._plots = {}
        self._fig_opt = fig_opt
        self.initialize_plot()
        self.plotting()

    @property
    def plot_dict(self):
        pdict = {'colors': np.tile(['b', 'g', 'r', 'c', 'm', 'y', 'k'], 10),
                 'linestyles': np.tile(['-', '--', ':', '-.'], 10),
                 'markers': np.tile(['.', 'v', '^', '<', '>', '1', '2', '3', '4', '8', 's', 'p', '*', 'h',
                                     'H', '+', 'x', 'D', 'd', '|', '_'], 10),
                 'markersizes': np.tile([5, 4, 4, 4, 4], 10)}
        return pdict

    def initialize_plot(self):
        pass

    # ## TESTED
    @property
    def sample_names(self):
        return self.sample_group.sample_names

    @property
    def samples(self):
        return self.sample_group.sample_list

    @property
    def sample_nr(self):
        return len(self.sample_group.sample_list)

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
        if isinstance(s_list, RockPy.SampleGroup):
            self.sample_group = s_list

        if isinstance(s_list, list):
            self.log.debug('CONVERTING list(sample) -> RockPy.SampleGroup(Sample)')
            self.sample_group = rp.SampleGroup(sample_list=s_list)

        if isinstance(s_list, rp.Sample):
            self.log.debug('CONVERTING sample -> list(sample) -> RockPy.SampleGroup(Sample)')
            self.sample_group = rp.SampleGroup(sample_list=[s_list])

    def create_fig(self, **fig_opt):
        fig = plt.figure(**fig_opt)
        return fig

    def plotting(self):
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