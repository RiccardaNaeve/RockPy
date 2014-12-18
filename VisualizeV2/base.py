__author__ = 'volk'
import logging
import os
import sys
import inspect

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
# from matplotlib import rc
from RockPy.Functions.general import _to_list
from matplotlib import gridspec
from matplotlib.backends.backend_pdf import PdfPages

class Generic(object):
    """
    You can either give a sample, a samplegroup or a whole study into a plot.
    The standard behaviour of a plot is as follows:

    Definitions:
    ============
        Visual:  upper most level
        Plot:  a visual can contain one or more figures, e.g. hysteresis + thermocurve.
                 These are plotted in different windows/pages in a pdf
        Subplot: Contained in a Figure. A Figure can have more than one subplot BUT ALWAYS HAS ONE.
                 Subplots are independent of eachother.
        dataseries:    a Subplot contains one or more dataseries. e.g.:
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

        # self.log = logging.getLogger('RockPy.VISUALIZE.' + type(self).__name__)
        self.tex = options.pop('tex', False)
        self.options = options

        # # normalization_parameters for normalization of measurement
        self.name = type(self).__name__.lower()
        self.existing_visuals = {i.__name__: i for i in Generic.inheritors()}

        self._required = {}  # required measurements in a figure

        self.input = plot_samples
        self.input_type = type(plot_samples)

        self.study = self._to_study(plot_samples)
        self._hierarchy = self.input_type

        # self.color_source = options.pop('color_source', self.get_source[self.input_type])
        # self.marker_source = options.pop('marker_source', self.get_source[self.input_type])
        # self.ls_source = options.pop('linestyle_source', 'treatment')

        self._visuals = {}  # visual contains ... plots
        self._figs = []
        self._fig_opt = fig_opt

        self.standard_features = []
        self.features = {i[0][8:]: i[1] for i in inspect.getmembers(self, predicate=inspect.ismethod) if
                         i[0].startswith('feature_')}

        self.line_dict = {i: None for i in self.features}
        self.text_dict = {i: None for i in self.features}

        self.initialize_visual()

    ''' NEEDED BY ALL VISULIZATIONS '''

    def initialize_visual(self):  #
        # MANDATORY
        """
        :return:
        """
        pass

    def plotting(self, sample):
        # MANDATORY
        """
        :param sample:
        :return:
        """
        pass

    ''' END OF MANDATORY '''

    # ## plotting style related
    @property
    def get_source(self):
        out = {RockPy.Study: 'samplegroup',
               RockPy.SampleGroup: 'sample',
               RockPy.Sample: 'measurement',
               RockPy.Measurements.base.Measurement: 'measurement'
        }
        return out
    #
    # def plotting_levels(self):
    #     """
    #     All possible plottings
    #     :return:
    #     """
    #
    #     out = {'Study_standard' : self.input.get_samplegroup_means,
    #            'Group_standard' : self.input.get_measurement_means
    #            }

    ''' PLOTTING REQUIREMENTS '''

    @property
    def required(self):
        if isinstance(self._required, dict):
            return self._required
        else:
            return {self.name: self._required}

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
    def visuals(self):
        if self._visuals:
            return self._visuals
        else:
            return {self.name.lower(): self}

    @property
    def figs(self):
        out = {name: visual._figs for name, visual in self.visuals.iteritems()}
        return out

    @property
    def subplots(self):
        pass


    def add_plot(self, name=None, plot=None, **plot_opt):
        if not plot:
            plot, gs = self._create_fig(**plot_opt)
            if not name:
                name = type(self).__name__.lower()
                if name in self._visuals:
                    name += '%02i' % len(self.visuals.keys())
            self.gs = gs
            self._figs.append(plot)
            self._visuals.update({name: self})
        else:
            self._visuals.update({plot.name: plot})
            self._required.update(plot.required)

    def add_subplot(self, name=None):
        if name is None:
            name = self.name
        self.gs = gridspec.GridSpec(1, 2)
        for ax in self.figs[name][0].as_list():
            ax.set_position(self.gs[0])
        self.figs[name][0].add_subplot(self.gs[1])

    def _create_fig(self, **fig_opt):
        fig = plt.figure(**fig_opt)
        gs = gridspec.GridSpec(1, 1)
        ax1 = fig.add_subplot(gs[0])
        return fig, gs

    ''' SAMPLE RELATED '''
    def get_plotting_samples(self):
        print self.input_type


    def _to_study(self, slist):
        """
        converts list of measurements/samples/sample_groups -> study

        if list of sample_groups -> self.input_type = RockPy.Study
        if list of samples -> self.input_type = RockPy.Sample_Group
        if list of measurements -> self.input_type = RockPy.Sample

        if single measurement -> self.input_type = RockPy.Measurements.base.Measurement

        """
        if not isinstance(slist, list):  # check if list
            if isinstance(slist, RockPy.Study):  # if study keep study
                out = slist
            if not isinstance(slist, RockPy.Study):
                if isinstance(slist, RockPy.SampleGroup) or isinstance(slist, RockPy.Sample):
                    # self.log.debug('CONVERTING %s -> RockPy.Study(%s)' % (type(slist), type(slist)))
                    out = RockPy.Study(slist)
                if type(slist) in RockPy.Measurements.base.Measurement.inheritors():
                    # self.log.debug(
                    print(
                        'CONVERTING %s -> RockPy.Sample -> RockPy.Study(Sample(%s))' % (type(slist), type(slist)))
                    s = RockPy.Sample(name=self.name)
                    s.measurements.append(slist)
                    self.input_type = RockPy.Measurements.base.Measurement
                    out = RockPy.Study(s)

        if isinstance(slist, list):
            if all(isinstance(item, RockPy.SampleGroup) for item in slist):
                # self.log.debug('CONVERTING %s(%s) -> RockPy.Study(%s(%s))' % (
                print('CONVERTING %s(%s) -> RockPy.Study(%s(%s))' % (
                    type(slist), type(slist[0]), type(slist), type(slist[0])))
                self.input_type = RockPy.Study
                out = RockPy.Study(slist)

            if all(isinstance(item, RockPy.Sample) for item in slist):
                # self.log.debug('CONVERTING %s(%s) -> RockPy.Study(%s(%s))' % (
                print('CONVERTING %s(%s) -> RockPy.Study(%s(%s))' % (
                    type(slist), type(slist[0]), type(slist), type(slist[0])))
                self.input_type = RockPy.SampleGroup
                out = RockPy.Study(slist)

            if all(type(item) in RockPy.Measurements.base.Measurement.inheritors() for item in slist):
                # self.log.debug(
                print(
                    'CONVERTING %s -> RockPy.Sample -> RockPy.Study(Sample(%s))' % (type(slist), type(slist)))
                self.input_type = RockPy.Sample
                s = RockPy.Sample(name=self.name)
                s.measurements = slist
                out = RockPy.Study(s)
        return out

    def _to_sample_list(self, slist):
        out = None
        if isinstance(slist, RockPy.Study):
            out = slist.samples
        if isinstance(slist, RockPy.SampleGroup):
            out = slist.sample_list
        if isinstance(slist, RockPy.Sample):
            out = [slist]

        if isinstance(slist, list):
            if all(isinstance(item, RockPy.SampleGroup) for item in slist):
                out = sum(slist).sample_list
            if all(isinstance(item, RockPy.Sample) for item in slist):
                out = slist
        return out

    def plot_measurements(self):
        pass

    def make_plots(self):
        for i in self.visuals:
            print i
            self.visuals[i].plotting('test')

    def show(self):
        # for label, figs in self.figs.iteritems():
        # for fig in figs:
        # axes = fig.gca()
        #         axes.set_title(label)

        plt.show()

    def showfigure(self):
        pass

    def save(self, folder=None, name=None):
        # rc('text', usetex=True)
        if folder is None:
            from os.path import expanduser

            folder = expanduser("~") + '/Desktop/'
        if name is None:
            name = self.name
        if not '.pdf' in name:
            name += '.pdf'
        loc = folder + name

        with PdfPages(loc) as pdf:
            for fig in self.figs:
                pdf.savefig()

    ''' Add smth. to plot '''

    def add_grid(self, visuals):
        visuals = _to_list(visuals)

        for plot in visuals:
            if plot in self.visuals:
                for fig in self.figs[plot]:
                    fig.gca().grid()


    def set_xlim(self, limits):
        for plot in self.visuals:
            for fig in self.figs[plot]:
                fig.gca().set_xlim(limits)

    def set_title(self, title):
        for plot in self.visuals:
            for fig in self.figs[plot]:
                fig.gca().set_title(title)


    ''' GET FUNCTIONS '''

    def get_single_fig(self):
        pass

    def _change_visible(self, text_or_line, caller, lines):
        tol = {'line': self.line_dict,
               'text': self.text_dict}
        if not text_or_line in tol:
            tol_dict = tol[text_or_line]
            if caller in tol_dict:
                tol_dict.update({caller: lines})
            else:
                tols = tol_dict[caller]
                for line in tols:
                    bool = line.get_visible()
                    line.set_visible(not bool)


    def _add_line_text_dict(self, lines, texts):
        caller = inspect.stack()[1][3][8:]
        self.line_dict[caller] = lines
        self.text_dict[caller] = texts