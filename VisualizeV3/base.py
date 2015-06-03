__author__ = 'volk'
import logging
import os
import sys
import inspect
import copy

import numpy as np

from profilehooks import profile

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib import gridspec
from matplotlib.backends.backend_pdf import PdfPages

import RockPy
import RockPy.Functions
import RockPy.Measurements.base
import RockPy.VisualizeV3.core
from RockPy.Functions.general import _to_list

from copy import deepcopy

class NewPlot(object):
    def __init__(self):
        """
        Container for visuals.

        Parameters
        ----------

        """
        self.logger = logging.getLogger(__name__)
        self.logger.info('CREATING new plot')

        # create dictionary for visuals {visual_name:visual_object}
        self._visuals = []
        self._n_visuals = 0

        self.fig = plt.figure() # initialize figure


    @property
    def visuals(self):
        return self._visuals

    def __getitem__(self, item):
        """
        Asking for an item from the plot will result in one of two things.
           1. If you ask for a name or an index, and the name or index are
        :param item:
        :return:
           Visual Object
        """
        # try:
        if item in self.vtypes:
            idx = [ i for i, v in enumerate(self.vtypes) if v == item]
            return [self._visuals[i][2] for i in idx]
        if item in self.vnames:
            idx = self.vnames.index(item)
            return self._visuals[idx][2]
        if type(item) == int:
            return self._visuals[item][2]
        else:
            raise KeyError('%s can not be found' %item)

    def add_visual(self, visual, name= None, plt_input=None):
        """
        adds a visual to the plot. This creates a new subplot.

        Parameters
        ----------

           visual: list, str
              name of visual to add.

        """
        input_exchange = []
        # convert visual to list
        visuals = _to_list(visual)
        for visual in visuals:
            # check if visual exists otherwise don't create it
            if visual in Generic.inheritors():
                if not name:
                    name = visual
                n = self._n_visuals
                # create instance of visual by dynamically calling from inheritors dictionary
                visual_obj = Generic.inheritors()[visual](plt_input=plt_input, plt_index=n, plot=self)
                self._visuals.append([name, visual, visual_obj])
                self._n_visuals += 1
            else:
                self.logger.warning('VISUAL << %s >> not implemented yet' %visual)

        self.fig = self._create_fig()
        self.plt_all()

    @property
    def vnames(self):
        return [i[0] for i in self._visuals]
    @property
    def vtypes(self):
        return [i[1] for i in self._visuals]
    @property
    def vinstances(self):
        return [i[2] for i in self._visuals]

    def plt_all(self):
        for name, type, visual in self._visuals:
            visual.plt_visual()

    def _create_fig(self):
        """
        Wrapper that creates a new figure but first deletes the old one.
        """
        # closes old figure before it is actually shown
        plt.close(self.fig)
        # create new figure with appropriate number of subplots
        return RockPy.VisualizeV3.core.generate_plots(n=self._n_visuals)

    def show(self):
        plt.show()

class Generic(object):
    """
    """
    _required = []

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
        return {i.__name__.lower(): i for i in subclasses}

    def __init__(self, plt_input=None, plt_index=None, plot=None):
        self.logger = logging.getLogger(__name__)

        self._plt_index = plt_index
        self._plt_input = plt_input
        self._plt_obj = plot

        ''' this part is needed by every plot, because it is executed automatically '''

        self.standard_features = []  # list containing all features that have to be plotted for each measurement
        self.single_features = []  # list of features that only have to be plotted one e.g. zero lines

        self.init_visual()

    def init_visual(self):
        pass

    def add_standard(self):
        """
        Adds standard stuff to plt, like title and x/y labels
        :return:
        """
        self.ax.set_title(self.title)
        self.ax.set_xlabel(self.xlabel)
        self.ax.set_ylabel(self.ylabel)

    def plt_visual(self):
        self.add_standard()
        if isinstance(self._plt_input, RockPy.Study):
            study = self._plt_input
            for sg_idx, sg in enumerate(study):
                print sg_idx
                # for sample_idx, sample in enumerate(sg):
                #     measurements = sample.get_measurements(mtype=self.__class__._required)
                #     for m_idx, m in enumerate(measurements):
                #         print sg_idx, sample_idx, m_idx
        #                 for feature in self.standard_features:
        #                     feature(m)

    @property
    def ax(self):
        return RockPy.VisualizeV3.core.get_subplot(self.fig, self._plt_index)

    @property
    def fig(self):
        return self._plt_obj.fig