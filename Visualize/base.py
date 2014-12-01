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


class Generic(object):
    RockPy.Functions.general.create_logger('RockPy.VISUALIZE')

    def __init__(self, sample_list,
                 norm=None, rtype='mag', vval=None, norm_method='max',
                 plot='show', folder=None, name=None,
                 plt_opt={}, style='screen',
                 create_fig=True, create_ax=True,

                 **options):
        self.log = logging.getLogger('RockPy.VISUALIZE.' + type(self).__name__)

        if plt_opt is None: plt_opt = {}

        params = {'publication': {'backend': 'ps',
                                  'text.latex.preamble': [r"\usepackage{upgreek}",
                                                          r"\usepackage[nice]{units}"],
                                  'axes.labelsize': 12,
                                  'text.fontsize': 12,
                                  'legend.fontsize': 8,
                                  'xtick.labelsize': 10,
                                  'ytick.labelsize': 10,
                                  'text.usetex': True,
                                  'axes.unicode_minus': True},

                  'screen': {'axes.labelsize': 12,
                             'text.fontsize': 12,
                             'legend.fontsize': 8,
                             'xtick.labelsize': 10,
                             'ytick.labelsize': 10}}

        self.colors = np.tile(['b', 'g', 'r', 'c', 'm', 'y', 'k'], 10)
        self.linestyles = np.tile(['-', '--', ':', '-.'], 10)
        self.markers = np.tile(['.', 'v', '^', '<', '>', '1', '2', '3', '4', '8', 's', 'p', '*', 'h',
                                'H', '+', 'x', 'D', 'd', '|', '_'], 10)
        self.markersizes = np.tile([5, 4, 4, 4, 4], 10)

        # plt.rcParams.update(params[style])
        self.style = style
        self.plt_opt = plt_opt

        # ## initialize
        self.fig = None
        self.ax = None

        # ## labels and titles
        self.x_label = ''
        self.y_label = ''

        self.plot = plot

        self.log = logging.getLogger('RockPy.VISUALIZE.' + type(self).__name__)

        self.sample_group = None
        self._group_from_list(sample_list)

        self.name = name
        self.folder = folder


        # ## normalization
        self.norm = norm
        self.rtype = rtype
        self.vval = vval
        self.norm_method = norm_method

        # check if a figure is provided, this way multiple plots can be combined into one figure
        if create_fig:
            # self.fig = options.get('fig', plt.figure(figsize=(8, 6), dpi=100))
            self.fig = options.get('fig', plt.figure(figsize=(11.69, 8.27), dpi=100))

        if create_ax:
            self.ax = options.get('ax', plt.subplot2grid((1, 1), (0, 0), colspan=1, rowspan=1))

    @property
    def title(self):
        return type(self).__name__ + ' [' + ','.join(self.sample_names) + ']'

    @property
    def sample_names(self):
        return self.sample_group.sample_names

    @property
    def sample_list(self):
        return self.sample_group.sample_list

    @property
    def samples(self):
        return self.sample_group.sample_list

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

    def set_xlim(self, **options):
        xlim = options.get('xlim', None)
        if xlim is not None:
            self.ax.set_xlim(xlim)

    def set_ylim(self, **options):
        ylim = options.get('ylim', None)
        if ylim is not None:
            self.ax.set_ylim(ylim)

    def out(self, *args):
        if not self.name:
            self.name = ''.join(self.sample_names)
            self.name += '_' + type(self).__name__

        if not '.pdf' in self.name:
            self.name += '.pdf'

        out_options = {'show': plt.show,
                       'rtn': self.get_fig,
                       'save': self.save_fig,
                       'None': self.close_plot,
                       'folder': self.plt_save_script_folder,
                       'get_ax': self.get_ax}

        if self.plot in ['show', 'save', 'folder']:
            if not 'no_lable' in args:
                try:
                    if self.ax:
                        self.ax.set_xlabel(self.x_label)
                        self.ax.set_ylabel(self.y_label)
                except AttributeError:
                    self.log.info('NO label set for axis')
            if not 'no_legend' in args:
                plt.legend(loc='best', fontsize=8)

        if self.style == 'publication':
            self.setFigLinesBW()

        try:
            if self.ax:
                self.ax.set_title(self.title)
        except AttributeError:
            self.log.info('NO title set for figure')
        out_options[self.plot]()

    def plt_save_script_folder(self):
        import __main__ as main

        name = main.__file__[:-2]
        name += self.name[:-3]
        name += ''.join(self.sample_names)
        name += '.pdf'
        plt.savefig(name)

    def get_ax(self):
        plt.close()
        return self.ax

    def get_fig(self):
        return self.fig1

    def save_fig(self):
        plt.savefig(self.folder + self.name, dpi=300)

    def setAxLinesBW(self, ax):
        """
        Take each Line2D in the axes, ax, and convert the line style to be
        suitable for black and white viewing.
        """
        MARKERSIZE = 5

        COLORMAP = {
            'b': {'marker': '.', 'dash': (None, None)},
            'g': {'marker': 'o', 'dash': [5, 5]},
            'r': {'marker': 's', 'dash': [5, 3, 1, 3]},
            'c': {'marker': 'o', 'dash': [1, 3]},
            'm': {'marker': '<', 'dash': [5, 2, 5, 2, 5, 10]},
            'y': {'marker': '>', 'dash': [5, 3, 1, 2, 1, 10]},
            'k': {'marker': 'o', 'dash': (None, None)},  # [1,2,1,10]}
            '#808080': {'marker': '.', 'dash': (None, None)}  # [1,2,1,10]}
        }

        for line in ax.get_lines():  # + ax.get_legend().get_lines():
            origColor = line.get_color()
            line.set_color('black')
            line.set_dashes(COLORMAP[origColor]['dash'])
            line.set_marker(COLORMAP[origColor]['marker'])
            line.set_markersize(MARKERSIZE)

    def setFigLinesBW(self):
        """
        Take each axes in the figure, and for each line in the axes, make the
        line viewable in black and white.
        """
        for ax in self.fig.get_axes():
            self.setAxLinesBW(ax)


    def _treatment_variable_transformation(self, sample_obj, mtype, ttype):
        mdict = sample_obj.mtype_ttype_tval_mdict[mtype][ttype]
        var_vals = self.get_common_variables_from_treatments(mdict)
        out = {}
        for tval in sorted(mdict):
            for measure in mdict[tval]:
                for dtype in measure.data:
                    if not dtype in out:
                        out[dtype] = copy.deepcopy(measure.data[dtype])
                    else:
                        aux = copy.deepcopy(measure.data[dtype])
                        out[dtype] = out[dtype].append_rows(aux)
        return out

    def get_common_variables_from_treatments(self, mdict):
        var_vals = {}
        for tval in mdict:
            for measure in mdict[tval]:
                for dtype in measure.data:
                    if not dtype in var_vals:
                        var_vals[dtype] = set(measure.data[dtype]['variable'].v)
                    var_vals[dtype] = var_vals[dtype].intersection(set(measure.data[dtype]['variable'].v))

        # convert sets to sorted lists
        for dtype in var_vals:
            var_vals[dtype] = sorted(list(var_vals[dtype]))

        return var_vals


    # @property
    # def title(self):
    # return self._title

    @title.setter
    def title(self, text):
        self._title = text

    @property
    def nr_samples(self):
        return len(self.sample_list)

    def get_measurement_dict(self, mtype):
        measure_dict = {sample: [i for i in sample.get_measurements(mtype=mtype)] for sample in self.sample_list
                        if sample.get_measurements(mtype=mtype)}
        return measure_dict

    def get_plt_opt(self, sample, measurements, measurement):
        label = ''

        if self.nr_samples > 1:
            label += sample.name
            colorchange = 'measurements'
        if len(measurements) > 1:
            label += ' ' + measurement.suffix

        plt_opt = {'marker': self.markers[self.sample_list.index(sample)],
                   'markersize': self.markersizes[self.sample_list.index(sample)],
                   'color': self.colors[measurements.index(measurement)],
                   'linestyle': self.linestyles[measurements.index(measurement)],
                   'label': label}
        return plt_opt

    def create_heat_color_map(self, value_list, reverse=False):
        """
        takes a list of values and creates a list of colors from blue to red

        :param value_list:
        :param reverse:
        :return:
        """
        r = np.linspace(0, 255, len(value_list)).astype('int')
        r = [hex(i)[2:-1].zfill(2) for i in r]
        # r = [i.encode('hex') for i in r]
        b = r[::-1]

        out = ['#%2s' % r[i] + '00' + '%2s' % b[i] for i in range(len(value_list))]
        if reverse:
            out = out[::-1]
        return out

    def create_dummy_line(self, **kwds):
        return Line2D([], [], **kwds)

    def close_plot(self):
        plt.close()
