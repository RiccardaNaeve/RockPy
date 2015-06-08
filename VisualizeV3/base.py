__author__ = 'volk'
import logging
from copy import deepcopy

import RockPy
import RockPy.Functions
import RockPy.Measurements.base
import RockPy.VisualizeV3.core


class Generic(object):
    """
    """
    _required = []
    linestyles = ['-', '--', ':', '-.']
    marker = ['+', '*', ',', '.', '1', '3', '2', '4', '8', '<', '>', 'D', 'H', '_', '^', 'd', 'h', 'o', 'p', 's', 'v', '|']
    colors = ('b', 'g', 'r', 'c', 'm', 'y', 'k')

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

    @classmethod
    def get_subclass_name(cls):
        return cls.__name__

    def __init__(self, plt_input=None, plt_index=None, plot=None, name=None):
        self.logger = logging.getLogger(self.get_subclass_name())

        self._plt_index = plt_index
        self._plt_input = deepcopy(plt_input)
        self._plt_obj = plot

        self.title = self.get_subclass_name()
        self.init_visual()

    def init_visual(self):
        ''' this part is needed by every plot, because it is executed automatically '''

        self.standard_features = []  # list containing all features that have to be plotted for each measurement
        self.single_features = []  # list of features that only have to be plotted one e.g. zero lines

    def add_standard(self):
        """
        Adds standard stuff to plt, like title and x/y labels
        :return:
        """
        self.ax.set_title(self.title)
        self.ax.set_xlabel(self.xlabel)
        self.ax.set_ylabel(self.ylabel)

    def get_virtual_study(self):
        all_measurements = False

        # because iterating over a study, samplegrou is like iterating over a list, I substitute them with lists if not
        # applicable so the plotting is simpler
        if isinstance(self._plt_input, RockPy.Study): # input is Study
            study = self._plt_input # no change
        if isinstance(self._plt_input, RockPy.SampleGroup): # input is samplegroup
            study = [self._plt_input]  # list = virtual study
        if isinstance(self._plt_input, RockPy.Sample): # input is sample
            study = [[self._plt_input]] # list(list) = virtual study with a virtual samplegroup
        if isinstance(self._plt_input, list):
            if all(isinstance(item, RockPy.SampleGroup) for item in self._plt_input):  # all input == samples
                study = self._plt_input
            if all(isinstance(item, RockPy.Sample) for item in self._plt_input):  # all input == samples
                study = [self._plt_input]
            if all(type(item) in RockPy.Measurements.base.Measurement.inheritors() for item in self._plt_input):
                all_measurements = True
                study = [[self._plt_input]]
        return study, all_measurements

    def plt_visual(self):
        self.add_standard()
        study, all_measurements = self.get_virtual_study()
        # plotting over study/ virtual study - > samplegroup / virtual SG ...
        for sg_idx, sg in enumerate(study):
            for sample_idx, sample in enumerate(sg):
                if not all_measurements:
                    measurements = sample.get_measurements(mtype=self.__class__._required)
                else:
                    measurements = study[0][0]
                if len(measurements) > 0:
                    for m_idx, m in enumerate(measurements):
                        ls, marker, color = self.get_ls_marker_color([sg_idx, sample_idx, m_idx])
                        for feature in self.standard_features:
                            plt_opt = dict(color = color, marker = marker, ls = ls)
                            feature(m, **plt_opt)
        for feature in self.single_features:
            feature()

    def normalize_all(self, reference='data', rtype='mag', ntypes='all', vval=None, norm_method='max'):
        study, all_measurements = self.get_virtual_study()
        # cycle through all measurements that will get plotted
        for sg_idx, sg in enumerate(study):
            for sample_idx, sample in enumerate(sg):
                if not all_measurements:
                    measurements = sample.get_measurements(mtype=self.__class__._required)
                else:
                    measurements = study[0][0]
                if len(measurements) > 0:
                    for m_idx, m in enumerate(measurements):
                        m.normalize(reference=reference, rtype=rtype, ntypes=ntypes, vval=vval, norm_method=norm_method)

    def get_ls_marker_color(self, indices):
        """
        Looks up the appropriate color, marker, ls for given indices
        :param indices:
        :return:
        """
        if len(indices) == 3:
            return Generic.linestyles[indices[0]], Generic.marker[indices[1]], Generic.colors[indices[2]]
        if len(indices) == 2:
            return Generic.linestyles[indices[0]], Generic.marker[indices[1]], Generic.colors[indices[2]]


    @property
    def ax(self):
        return RockPy.VisualizeV3.core.get_subplot(self.fig, self._plt_index)

    @property
    def fig(self):
        return self._plt_obj.fig