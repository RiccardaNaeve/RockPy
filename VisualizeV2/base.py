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
import RockPy
import inspect
RockPy.Functions.general.create_logger('RockPy.VISUALIZE')
import RockPy.Measurements.base


class Generic(object):
    """
    You can either give a sample, a samplegroup or a whole study into a plot.
    The standard behaviour of a plot is as follows:

    Definitions:
    ============
        Visual:  upper most level
        Figure:  a visual can contain one or more figures, e.g. hysteresis + thermocurve.
                 These are plotted in different windows/pages in a pdf
        Subplot: Contained in a Figure. A Figure can have more than one subplot BUT ALWAYS HAS ONE.
                 Subplots are independent of eachother.
        Plot:    a Subplot contains one or more plots. e.g.:
                    - the evolution of two parameters with a variable
                    - a hysteresis with included backfield plot
                    - measurements of different samples
    Study
    =====
    assuming you pass a study into a plot:

        This will plot a mean for each sample_group

        e.g. useful for lots of groups
        colors = Sample_groups
        lines = treatments

    Sample_Group
    ============
    passing a sample_group into a plot:

       This will plot all samples in sample_group and the average

    Sample
    ======
    passing a sample in to a plot:

       This will plot the sample and all the measurements
       open question:
       - do we need a average measurement function or is this done through sample groups


    OPEN QUESTIONS
    ==============

    """
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


    def __init__(self, plot_samples=None,
                 reference='nrm', rtype='mag', vval=None, norm_method='max',
                 fig_opt=dict(),
                 **options):

        self.log = logging.getLogger('RockPy.VISUALIZE.' + type(self).__name__)

        ## normalization_parameters for normalization of measurement
        self.name = type(self).__name__
        self.existing_visuals = {i.__name__: i for i in Generic.inheritors()}

        self._required = {}   #required measurements in a figure

        self.input_type = type(plot_samples)
        self._hierarchy = self.input_type
        self.study = self._to_study(plot_samples)

        # self.color_source = options.pop('color_source', self.get_source[self.input_type])
        # self.marker_source = options.pop('marker_source', self.get_source[self.input_type])
        # self.ls_source = options.pop('linestyle_source', 'treatment')

        self._figs = {}
        self._fig_opt = fig_opt

        self._plots = {}      #visual contains ... plots

        self.initialize_plot()

    ''' NEEDED BY ALL VISULIZATIONS '''
    def initialize_plot(self):#
        #MANDATORY
        """
        :return:
        """
        pass

    def plotting(self, sample):
        #MANDATORY
        """
        :param sample:
        :return:
        """
        pass
    ''' END OF MANDATORY '''

    ### plotting style related
    @property
    def get_source(self):
        out = {RockPy.Study: 'samplegroup',
               RockPy.SampleGroup: 'sample',
               RockPy.Sample: 'measurement',
               RockPy.Measurements.base.Measurement: 'measurement'
        }
        return out



    ''' PLOTTING REQUIREMENTS '''
    @property
    def required(self):
        if isinstance(self._required, dict):
            return self._required
        else:
            return {self.name.lower(): self._required}

    @property
    def require_list(self):
        return [j for i in self.required for j in self.required[i]]


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

    def get_samples_meet_requirements(self, sg):
        out = [sample for sample in sg.sample_list if self.meets_requirements(sample)]
        return out

    ''' FIGURE REALTED '''

    @property
    def figs(self):
        if self._figs:
            return self._figs
        else:
            return {self.name.lower(): self}

    @property
    def subplots(self):
        pass

    @property
    def plots(self):
        pass

    def add_fig(self, name=None, fig=None, **fig_opt):
        if not fig:
            fig = self._create_fig(**fig_opt)
            if not name:
                name = type(self).__name__.lower()
                if name in self._figs:
                    name += '%02i' %len(self.figs.keys())
            self._figs.update({name:fig})
        else:
            self._figs.update(fig._figs)

    def add_subplot(self, figure, name):
        pass

    def add_plot(self, figure, subplot, name):
        pass

    def _create_fig(self, **fig_opt):
        fig = plt.figure(**fig_opt)
        return fig
    # def plots(self):
    #     return self._plots
    #
    #
    # def add_plot(self, label=None, **fig_opt):
    #     if not fig_opt:
    #         fig_opt = self._fig_opt
    #     if not 'figsize' in fig_opt:
    #         fig_opt.update({'figsize': (11.69, 8.27)})
    #     if not label:
    #         label = len(self._plots)
    #     self._plots.update({label.lower(): self.create_fig(**fig_opt)})
    #     return self.plots[label]
    #
    # def add_fig(self, fig):
    #     # if isinstance(fig, Generic):
    #     self.plots.update(fig.plots)
    #     self._required.update(fig.required)
    #     self._figs.update({fig.name.lower(): fig})
    #
    # def get_fig(self, label):
    #     return self.plots[label]
    #
    # def create_fig(self, **fig_opt):
    #     fig = plt.figure(**fig_opt)
    #     return fig

    ''' SAMPLE RELATED '''

    def _to_study(self, slist):
        """
        converts list of measurements/samples/sample_groups -> study

        if list of sample_groups -> self.input_type = RockPy.Study
        if list of samples -> self.input_type = RockPy.Sample_Group
        if list of measurements -> self.input_type = RockPy.Sample

        if single measurement -> self.input_type = RockPy.Measurements.base.Measurement

        """
        if not isinstance(slist, list): #check if list
            if isinstance(slist, RockPy.Study): #if study keep study
                out = slist
            if not isinstance(slist, RockPy.Study):
                if isinstance(slist, RockPy.SampleGroup) or isinstance(slist, RockPy.Sample):
                    self.log.debug('CONVERTING %s -> RockPy.Study(%s)' % (type(slist), type(slist)))
                    out = RockPy.Study(slist)
                if type(slist) in RockPy.Measurements.base.Measurement.inheritors():
                    self.log.debug(
                        'CONVERTING %s -> RockPy.Sample -> RockPy.Study(Sample(%s))' % (type(slist), type(slist)))
                    s = RockPy.Sample(name=self.name)
                    s.measurements.append(slist)
                    self.input_type = RockPy.Measurements.base.Measurement
                    out = RockPy.Study(s)

        if isinstance(slist, list):
            if all(isinstance(item, RockPy.SampleGroup) for item in slist):
                self.log.debug('CONVERTING %s(%s) -> RockPy.Study(%s(%s))' % (
                    type(slist), type(slist[0]), type(slist), type(slist[0])))
                self.input_type = RockPy.Study
                out = RockPy.Study(slist)

            if all(isinstance(item, RockPy.Sample) for item in slist):
                self.log.debug('CONVERTING %s(%s) -> RockPy.Study(%s(%s))' % (
                    type(slist), type(slist[0]), type(slist), type(slist[0])))
                self.input_type = RockPy.SampleGroup
                out = RockPy.Study(slist)

            if all(type(item) in RockPy.Measurements.base.Measurement.inheritors() for item in slist):
                self.log.debug(
                    'CONVERTING %s -> RockPy.Sample -> RockPy.Study(Sample(%s))' % (type(slist), type(slist)))
                self.input_type = RockPy.Sample
                s = RockPy.Sample(name=self.name)
                s.measurements = slist
                out = RockPy.Study(s)
        return out


    def plot_measurements(self):
        pass

    def show(self):
        for label, fig in self.plots.iteritems():
            axes = fig.gca()
            axes.set_title(label)

        plt.show()


class Generic_OLD(object):
    """
    You can either give a sample, a samplegroup or a whole study into a plot.
    The standard behaviour of a plot is as follows:

    Study
    =====
    assuming you pass a study into a plot:

        This will plot a mean for each sample_group

        e.g. useful for lots of groups
        colors = Sample_groups
        lines = treatments

    Sample_Group
    ============
    passing a sample_group into a plot:

       This will plot all samples in sample_group and the average

    Sample
    ======
    passing a sample in to a plot:

       This will plot the sample and all the measurements
       open question:
       - do we need a average measurement function or is this done through sample groups


    OPEN QUESTIONS
    ==============
    - passing a measurement ? is that something we want?

    """
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


    def __init__(self, plot_samples=None, norm=None,
                 parameter=dict(),
                 reference='nrm', rtype='mag', vval=None, norm_method='max',
                 plot='show', folder=None, name=None,
                 create_fig=True, create_ax=True,
                 plot_all=False,
                 fig_opt=dict(), plt_opt=dict(),
                 **options):

        self.log = logging.getLogger('RockPy.VISUALIZE.' + type(self).__name__)

        ## normalization_parameters for normalization of measurement
        self.norm = {'reference':reference, 'rtype':rtype, 'vval':vval, 'norm_method':norm_method}
        self.name = type(self).__name__
        self.existing_visuals = {i.__name__: i for i in Generic.inheritors()}

        self._required = {} #required measurements in a figure
        self._plots = {} #visual contains ... plots

        self.input_type = type(plot_samples)
        self._hierarchy = self.input_type
        self.study = self._to_study(plot_samples)

        self._parameter = parameter
        self.plot_all = plot_all

        self.color_source = options.pop('color_source', self.get_source[self.input_type])
        self.marker_source = options.pop('marker_source', self.get_source[self.input_type])
        self.ls_source = options.pop('linestyle_source', 'treatment')

        self._figs = {}
        self._fig_opt = fig_opt

        self.initialize_plot()

    def initialize_plot(self):
        pass

    @property
    def parameter(self):
        parameter = dict()
        if not self._parameter:
            parameter = self.std_parameter
        else:
            for key in self.std_parameter:
                if not key in parameter:
                    parameter.update({key: self.std_parameter[key]})
        return parameter

    ### plotting style related
    @property
    def get_source(self):
        out = {RockPy.Study: 'samplegroup',
               RockPy.SampleGroup: 'sample',
               RockPy.Sample: 'measurement',
               RockPy.Measurements.base.Measurement: 'measurement'
        }
        return out

    def get_plt_opt(self, measurement, sample_group):
        out = {'color': color,
               'marker': marker,
               'linestyle': line,
        }
        return out



    def change_hierarchy(self, new_hierarchy):
        h = {}
        return h

    @property
    def figs(self):
        if self._figs:
            return self._figs
        else:
            return {self.name.lower(): self}

    @property
    def plot_samples(self):
        return self.get_plotting_samples()

    def get_plotting_samples(self):
        """
        defines the standard plotting behaviour for different input types, can be changed using change_hierarchy method #todo

        :return:
        """
        if self._hierarchy == RockPy.Study:
            # plot sample_group averages
            out = {}
            for fig in self.required:  # different figures may have different mtype requirements
                out.update({fig: []})
                for mtype in self.required[fig]:
                    if self.plot_all:
                        groups = self.study.samplegroups
                    else:
                        groups = self.study.no_all_samplegroups
                    for sg in groups:
                        samples_meet_req = self.get_samples_meet_requirements(sg)
                        sampleg = RockPy.SampleGroup(sample_list=samples_meet_req)
                        s = sampleg.get_average_mtype_sample(mtype=mtype, reference=self.figs[fig].std_reference)
                        out[fig].append(s)

        if self._hierarchy == RockPy.SampleGroup:
            # plot samples and sample average
            pass

        if self._hierarchy == RockPy.Sample:
            # plot measurements and treatments, ??? average measurement for equal treatment???
            pass

        return out

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
            return {self.name.lower(): self._required}

    @property
    def require_list(self):
        return [j for i in self.required for j in self.required[i]]


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

    def get_samples_meet_requirements(self, sg):
        out = [sample for sample in sg.sample_list if self.meets_requirements(sample)]
        return out

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
        self._plots.update({label.lower(): self.create_fig(**fig_opt)})
        return self.plots[label]

    def get_fig(self, label):
        return self.plots[label]

    def add_fig(self, fig):
        # if isinstance(fig, Generic):
        self.plots.update(fig.plots)
        self._required.update(fig.required)
        self._figs.update({fig.name.lower(): fig})

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

    def _to_study(self, slist):
        """
        converts list of measurements/samples/sample_groups -> study

        if list of sample_groups -> self.input_type = RockPy.Study
        if list of samples -> self.input_type = RockPy.Sample_Group
        if list of measurements -> self.input_type = RockPy.Sample

        if single measurement -> self.input_type = RockPy.Measurements.base.Measurement

        """
        if not isinstance(slist, list): #check if list
            if isinstance(slist, RockPy.Study): #if study keep study
                out = slist
            if not isinstance(slist, RockPy.Study):
                if isinstance(slist, RockPy.SampleGroup) or isinstance(slist, RockPy.Sample):
                    self.log.debug('CONVERTING %s -> RockPy.Study(%s)' % (type(slist), type(slist)))
                    out = RockPy.Study(slist)
                if type(slist) in RockPy.Measurements.base.Measurement.inheritors():
                    self.log.debug(
                        'CONVERTING %s -> RockPy.Sample -> RockPy.Study(Sample(%s))' % (type(slist), type(slist)))
                    s = RockPy.Sample(name=self.name)
                    s.measurements.append(slist)
                    self.input_type = RockPy.Measurements.base.Measurement
                    out = RockPy.Study(s)

        if isinstance(slist, list):
            if all(isinstance(item, RockPy.SampleGroup) for item in slist):
                self.log.debug('CONVERTING %s(%s) -> RockPy.Study(%s(%s))' % (
                    type(slist), type(slist[0]), type(slist), type(slist[0])))
                self.input_type = RockPy.Study
                out = RockPy.Study(slist)

            if all(isinstance(item, RockPy.Sample) for item in slist):
                self.log.debug('CONVERTING %s(%s) -> RockPy.Study(%s(%s))' % (
                    type(slist), type(slist[0]), type(slist), type(slist[0])))
                self.input_type = RockPy.SampleGroup
                out = RockPy.Study(slist)

            if all(type(item) in RockPy.Measurements.base.Measurement.inheritors() for item in slist):
                self.log.debug(
                    'CONVERTING %s -> RockPy.Sample -> RockPy.Study(Sample(%s))' % (type(slist), type(slist)))
                self.input_type = RockPy.Sample
                s = RockPy.Sample(name=self.name)
                s.measurements = slist
                out = RockPy.Study(s)
        return out

    def create_fig(self, **fig_opt):
        fig = plt.figure(**fig_opt)
        return fig

    def plotting(self, sample):
        pass


    def add_samples_to_plot(self):
        for plot in self.plot_samples:
            for sample in self.get_samples_meet_requirements(self.study.all_samplegroup):
                self.figs[plot].plotting(sample=sample)

    def plot_study(self):
        pass

    def plot_group(self):
        pass

    # def plot_samples(self):
    #     pass

    def plot_measurements(self):
        pass

    def show(self):
        for label, fig in self.plots.iteritems():
            axes = fig.gca()
            axes.set_title(label)

        plt.show()

