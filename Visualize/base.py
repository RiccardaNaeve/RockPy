__author__ = 'volk'
import logging

import numpy as np
import matplotlib.pyplot as plt

import Functions


class Generic(object):
    Functions.general.create_logger('RockPy.VISUALIZE')

    def __init__(self, sample_list, norm=None,
                 plot='show', folder=None, name='output.pdf',
                 plt_opt={}, style='screen',
                 create_fig=True, create_ax=True,
                 **options):
        if plt_opt is None: plt_opt = {}

        params = {'publication': {'backend': 'ps',
                                  'text.latex.preamble': [r"\usepackage{upgreek}",
                                                          r"\usepackage[nice]{units}"],
                                  'axes.labelsize': 12,
                                  'text.fontsize': 12,
                                  'legend.fontsize': 8,
                                  'xtick.labelsize': 10,
                                  'ytick.labelsize': 10,
                                  # 'text.usetex': True,
                                  'axes.unicode_minus': True},

                  'screen': {'axes.labelsize': 12,
                             'text.fontsize': 12,
                             'legend.fontsize': 8,
                             'xtick.labelsize': 10,
                             'ytick.labelsize': 10}}

        self.colors = np.tile(['b', 'g', 'r', 'c', 'm', 'y', 'k'], 10)
        self.linestyles = np.tile(['-', '--', ':', '-.'], 10)
        self.markers = np.tile(['.', ',', 'o', 'v', '^', '<', '>', '1', '2', '3', '4', '8', 's', 'p', '*', 'h',
                                'H', '+', 'x', 'D', 'd', '|', '_'], 10)
        self.markersizes = np.tile([10, 3, 3, 3, 3], 10)

        self.log = logging.getLogger('RockPy.VISUALIZE.' + type(self).__name__)

        plt.rcParams.update(params[style])
        self.style = style
        self.plt_opt = plt_opt

        # ## initialize
        self.fig = None
        self.ax = None

        # ## labels and titles
        self.x_label = None
        self.y_label = None

        self.plot = plot

        if type(sample_list) is not list:
            self.log.debug('CONVERTING Sample Instance to Samples List')
            sample_list = [sample_list]

        self.name = name

        if folder is None:
            from os.path import expanduser

            folder = expanduser("~") + '/Desktop/'

        self.folder = folder

        self.norm = norm
        self.samples = [i for i in sample_list]
        self.sample_list = sample_list
        self.sample_names = [i.name for i in sample_list]


        # check if a figure is provided, this way multiple plots can be combined into one figure
        if create_fig:
            self.fig = options.get('fig', plt.figure(figsize=(8, 6), dpi=100))
        if create_ax:
            self.ax = options.get('ax', plt.subplot2grid((1, 1), (0, 0), colspan=1, rowspan=1))

    def set_xlim(self, **options):
        xlim = options.get('xlim', None)
        if xlim is not None:
            self.ax.set_xlim(xlim)

    def set_ylim(self, **options):
        ylim = options.get('ylim', None)
        if ylim is not None:
            self.ax.set_ylim(ylim)
            
    def out(self, *args):
        if not '.pdf' in self.name:
            self.name += '.pdf'

        out_options = {'show': plt.show,
                       'rtn': self.get_fig,
                       'save': self.save_fig,
                       'None': self.close_plot,
                       'get_ax': self.get_ax}

        if self.plot in ['show', 'save']:
            if not 'nolable' in args:
                self.ax.set_xlabel(self.x_label)
                self.ax.set_ylabel(self.y_label)

                plt.legend(loc='best')
        out_options[self.plot]()

    def get_ax(self):
        plt.close()
        return self.ax

    def get_fig(self):
        return self.fig1

    def save_fig(self):
        try:
            plt.savefig(self.folder + self.samples[0].name + '_' + self.name, dpi=300)
        except IndexError:
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

    @property
    def nr_samples(self):
        return len(self.sample_list)

    def get_measurement_dict(self, mtype):
        measure_dict = {sample: [i for i in sample.get_measurements(mtype=mtype)] for sample in self.sample_list}
        return measure_dict

    def get_plt_opt(self, sample, measurements, measurement):
        label = ''

        if self.nr_samples > 1:
            label += sample.name
            colorchange = 'measurements'
        if len(measurements) > 1:
            label += ' ' + measurement.suffix

        plt_opt = {'marker': '.',  # self.markers[self.sample_list.index(sample)],
                   # 'markersize': self.markersizes[self.sample_list.index(sample)],
                   # 'color': self.colors[self.sample_list.index(sample)],
                   'linestyle': self.linestyles[measurements.index(measurement)],
                   'label': label}
        return plt_opt

    def close_plot(self):
        plt.close()
