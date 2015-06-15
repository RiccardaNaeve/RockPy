__author__ = 'volk'
import logging

from copy import deepcopy
from profilehooks import profile

import RockPy
import RockPy.core
import RockPy.Functions
import RockPy.Measurements.base
import RockPy.VisualizeV3.core



class Visual(object):
    """
    OPEN QUESTIONS:
       - what if I want to add a non-required feature to the visual e.g. backfield to hysteresis
       - what if I want to have a different visual on a second y axis?
    """
    logger = logging.getLogger('RockPy.MEASUREMENT')
    _required = []
    linestyles = ['-', '--', ':', '-.']
    marker = ['+', '*', ',', '.', '1', '3', '2', '4', '8', '<', '>', 'D', 'H', '_', '^', 'd', 'h', 'o', 'p', 's', 'v',
              '|']
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

    @property
    def implemented_features(self):
        out = {i[8:]: getattr(self, i) for i in dir(self) if i.startswith('feature_') if not i.endswith('names')}
        return out

    @property
    def feature_names(self):
        return [i.__name__[8:] for i in self.features]

    def __init__(self, plt_input=None, plt_index=None, plot=None, name=None):
        self.logger = logging.getLogger('RockPy.VISUALIZE.' + self.get_subclass_name())
        self.logger.info('CREATING new plot')

        self._plt_index = plt_index
        self._plt_input = deepcopy(plt_input)
        self._plt_obj = plot

        self.title = self.get_subclass_name()
        self.init_visual()

    def init_visual(self):
        ''' this part is needed by every plot, because it is executed automatically '''

        self.features = []  # list containing all features that have to be plotted for each measurement
        self.single_features = []  # list of features that only have to be plotted one e.g. zero lines

    def add_feature(self, features=None):
        self.add_feature_to_list(features=features, feature_list='features')

    def add_single_feature(self, features=None):
        self.add_feature_to_list(features=features, feature_list='single_features')

    def add_feature_to_list(self, feature_list, features=None):
        """
        Adds a feature to the list of pfeature that will be plotted (self.features)

        """
        list2add = getattr(self, feature_list)

        features = RockPy.core._to_list(features)  # convert to list if necessary
        # check if feature has been provided, if not show list of implemented features
        if not features:
            self.logger.warning('NO feature selcted chose one of the following:')
            self.logger.warning('%s' % sorted(self.implemented_features))

        # check if any of the features is not implemented
        if any(feature not in self.implemented_features for feature in features):
            for feature in features:
                if feature not in self.implemented_features:
                    self.logger.warning('FEATURE << %s >> not implemented chose one of the following:' % feature)

                    # remove feature that is not implemented
                    features.remove(feature)
            self.logger.warning('%s' % sorted(self.implemented_features.keys()))

        # check for duplicates and dont add them
        for feature in features:
            if feature not in self.feature_names:
                # add features to self.features
                list2add.append(self.implemented_features[feature])
            else:
                self.logger.info('FEATURE << %s >> already used in %s' % (feature, feature_list))

    def remove_feature(self, features=None):
        self.remove_feature_from_list(feature_list='features', features=features)

    def remove_single_feature(self, features=None): #todo automatic determination if single figure
        self.remove_feature_from_list(feature_list='single_features', features=features)

    def remove_feature_from_list(self, feature_list, features=None):
        """
        Removes a feature, will result in feature is not plotted

        :param features:
        :return:
        """
        list2remove = getattr(self, feature_list)
        list_names = [i.__name__[8:] for i in list2remove]

        features = RockPy.core._to_list(features)  # convert to list if necessary

        # check if feature has been provided, if not show list of implemented features
        if not features:
            self.logger.warning('NO FEATURE SELECTED')
            self.logger.warning('%s' % sorted(self.features))

        print list2remove
        # check if any of the features is in used features
        for feature in features:
            if feature in list_names:
                # remove feature that is not implemented
                self.logger.warning('REMOVING feature << %s >>' % feature)
                idx = list_names.index(feature)
                list2remove.remove(list2remove[idx])
            else:
                self.logger.warning('FEATURE << %s >> not used' % feature)

    def add_standard(self):
        """
        Adds standard stuff to plt, like title and x/y labels
        :return:
        """
        self.ax.set_title(self.title)
        self.ax.set_xlabel(self.xlabel)
        self.ax.set_ylabel(self.ylabel)

    def get_virtual_study(self):
        """
        creates a virtual study so you can iterate over samplegroups, samples, measurements

        Returns
        -------
           only_measurements: Bool
              True if only measurements are to be plotted
        """
        # initialize
        only_measurements = False
        study = None

        # because iterating over a study, samplegroup is like iterating over a list, I substitute them with lists if not
        # applicable so the plotting is simpler
        if isinstance(self._plt_input, RockPy.Study):  # input is Study
            study = self._plt_input  # no change
        if isinstance(self._plt_input, RockPy.SampleGroup):  # input is samplegroup
            study = [self._plt_input]  # list = virtual study
        if isinstance(self._plt_input, RockPy.Sample):  # input is sample
            study = [[self._plt_input]]  # list(list) = virtual study with a virtual samplegroup
        if isinstance(self._plt_input, list):
            if all(isinstance(item, RockPy.SampleGroup) for item in self._plt_input):  # all input == samples
                study = self._plt_input
            if all(isinstance(item, RockPy.Sample) for item in self._plt_input):  # all input == samples
                study = [self._plt_input]

            # all items in _plt_input are measurements
            if all(type(item) in RockPy.Measurements.base.Measurement.inheritors() for item in self._plt_input):
                only_measurements = True
                study = [[self._plt_input]]
        return study, only_measurements

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
                        for feature in self.features:
                            plt_opt = dict(color=color, marker=marker, ls=ls)
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
            return Visual.linestyles[indices[0]], Visual.marker[indices[1]], Visual.colors[indices[2]]
        if len(indices) == 2:
            return Visual.linestyles[indices[0]], Visual.marker[indices[1]], Visual.colors[indices[2]]

    def feature_grid(self, m_obj=None, **plt_opt):
        self.ax.grid()
        return 'single'

    def feature_zero_lines(self, m_obj=None, **plt_opt):
        color = plt_opt.pop('color', 'k')
        zorder = plt_opt.pop('zorder', 0)

        self.ax.axhline(0, color=color, zorder=zorder,
                        **plt_opt)
        self.ax.axvline(0, color=color, zorder=zorder,
                        **plt_opt)
        return 'single'

    @property
    def ax(self):
        return RockPy.VisualizeV3.core.get_subplot(self.fig, self._plt_index)

    @property
    def fig(self):
        return self._plt_obj.fig


### generic class:
class Generic(Visual):
    # _required for searching through samples for plotables
    _required = []

    def __init__(self, plt_index, plt_input=None, plot=None, name=None):
        super(Generic, self).__init__(plt_input=plt_input, plt_index=plt_index, plot=plot, name=name)
        self.logger.info('CREATING new plot')