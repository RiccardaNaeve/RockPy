from RockPy.PlottingOLD import arai
from RockPy.VisualizeOLD import base

__author__ = 'mike'
import matplotlib.pyplot as plt
import base
from RockPy import PlottingOLD
from RockPy.Visualize import Features
import numpy as np


class Sample_sheet(base.Generic):
    def __init__(self, sample_list, norm='mass',
                 t_min=20, t_max=700, component='mag',
                 line=True, check=True,
                 plot='show', folder=None, name='arai plot',
                 plt_opt=None, style='screen',
                 **options):
        """

        implemented options:
           arai_line: adds the line fit to the arai_plot

        """

        super(Sample_sheet, self).__init__(sample_list, norm=None,
                                           plot=plot, folder=folder, name=name,
                                           plt_opt=plt_opt, style=style,
                                           create_fig=False, create_ax=False,
                                           **options)
        # parameter for PalInt calculations
        self.parameter = {'t_min': t_min,
                          't_max': t_max,
                          'component': component}



        # initializing figure and axis
        self.fig = plt.figure(figsize=(11.69, 8.27), dpi=100)

        # axis objects
        self.dunlop = plt.subplot2grid((5, 5), (0, 0), colspan=3, rowspan=2)
        self.difference = plt.subplot2grid((5, 5), (2, 0), colspan=3, rowspan=1)
        self.arai = plt.subplot2grid((5, 5), (3, 0), colspan=2, rowspan=2)
        self.decay = plt.subplot2grid((5, 5), (3, 2), rowspan=2, colspan=2)
        self.zijderveld_ptrm = plt.subplot2grid((5, 5), (0, 3))
        self.zijderveld_th = plt.subplot2grid((5, 5), (0, 4))
        self.stereo_ptrm = plt.subplot2grid((5, 5), (1, 3))
        self.stereo_th = plt.subplot2grid((5, 5), (1, 4))

        plt.tight_layout()
        self.show(**options)
        self.out('nolable')

    def show(self, **options):
        self.dunlop.set_title('dunlop')
        self.arai.set_title('arai')
        self.difference.set_title('difference')
        self.decay.set_title('decay')
        self.zijderveld_th.set_title('TH')
        self.zijderveld_ptrm.set_title('PTRM')
        self.stereo_th.set_title('TH')
        self.stereo_ptrm.set_title('TH')

        if len(self.sample_list) > 1:
            self.log.warning('MORE than one sample, using first')

        sample = self.sample_list[0]
        # thellier_objs = sample.get_measurements(mtype='thellier')
        # for thellier in thellier_objs:
        arai.Arai(sample, plot='get_ax', fig=self.fig, ax=self.arai)
        # self.dunlop = arai.Arai(sample, plot='None', fig=self.fig, ax = self.arai).get_ax()


class Dunlop(base.Generic):
    def __init__(self, sample_list, norm='mass',
                 t_min=20, t_max=700, component='mag',
                 line=True, check=True,
                 plot='show', folder=None, name='arai plot',
                 plt_opt=None, style='screen',
                 **options):
        """

        implemented options:
           arai_line: adds the line fit to the arai_plot

        """

        super(Dunlop, self).__init__(sample_list, norm=norm,
                                     plot=plot, folder=folder, name=name,
                                     plt_opt=plt_opt, style=style,
                                     create_fig=True, create_ax=True,
                                     **options)
        self.component = component
        self.title = 'Dunlop Plot %s' % self.sample_names
        self.x_label = 'Temperature [C]'
        self.y_label = 'Moment'

        self.show(**options)
        self.out('no_legend')

    def show(self, **options):
        measure_dict = self.get_measurement_dict(mtype='thellier')
        for sample in measure_dict:
            for measurement in measure_dict[sample]:
                norm_factor = self.get_norm_factor(measurement)
                plt_opt = self.get_plt_opt(sample=sample, measurements=measure_dict[sample], measurement=measurement)
                # plt_opt.update({'markersize': measurement.tdict['pressure'] * 4 + 2})
                PlottingOLD.dunlop.dunlop(self.ax, measurement, norm_factor=norm_factor, **plt_opt)

                if 'std_fill' in options:
                    PlottingOLD.dunlop.dunlop_std(self.ax, measurement, norm_factor=norm_factor, **plt_opt)

    def get_norm_factor(self, measurement):
        implemented = {'is':
                           self._get_initial_state_normalizer}
        try:
            out = [1.0, implemented[self.norm](measurement)]
        except KeyError:
            # self.log.error('NORMALIZATION method << %s >> not implemented' % self.norm)
            out = [1.0, 1.0]
        return out

    def _get_initial_state_normalizer(self, measurement):
        """
        gets the initial state value for normalization
        """
        if measurement.initial_state:
            out = measurement.initial_state.data[self.component].v
        return out


class Dunlop_Treatments_Difference(base.Generic):
    def __init__(self, sample_list, norm='mass',
                 t_min=20, t_max=700, component='mag',
                 line=True, check=True,
                 plot='show', folder=None, name='Dunlop_Treatments',
                 plt_opt=None, style='screen', ttype='pressure',
                 **options):
        """

        implemented options:
           arai_line: adds the line fit to the arai_plot

        """

        super(Dunlop_Treatments_Difference, self).__init__(sample_list, norm=norm,
                                                           plot=plot, folder=folder, name=name,
                                                           plt_opt=plt_opt, style=style,
                                                           create_fig=False, create_ax=False,
                                                           **options)
        self.ttype = ttype
        self.component = component
        # self.fig = plt.figure()
        self.fig = plt.figure(figsize=(10, 10))

        self.ax1 = plt.subplot2grid((2, 1), (0, 0), rowspan=1)
        self.ax2 = plt.subplot2grid((2, 1), (1, 0), rowspan=1)
        self.get_plot_options(**options)
        self.show(**options)
        plt.tight_layout()
        self.out('nolable')

    def get_plot_options(self, **options):
        self.std_fill = options.pop('std_fill', False)


    def show(self, **options):
        d = self.sample_group.treatment_dict[self.ttype]

        th_line = ('TH', {'color': 'g', 'linestyle': '-', 'marker': '.'})
        ptrm_line = ('PTRM', {'color': 'b', 'linestyle': '-', 'marker': '.'})
        sum_line = ('SUM', {'color': 'r', 'linestyle': '-', 'marker': '.'})

        ax1_lines = []
        ax1_lines.append(th_line)
        ax1_lines.append(ptrm_line)
        ax1_lines.append(sum_line)
        for i, tval in enumerate(sorted(d.keys())):
            self.markers[i] = '.'
            self.markersizes[i] = 1 + tval * 5
            ax1_lines.append(
                (str(tval) + ' GPa', {'color': 'k', 'linestyle': self.linestyles[i], 'marker': self.markers[i],
                                      'markersize': self.markersizes[i]}))
            for j, m in enumerate(d[tval]):
                if m.mtype == 'thellier':
                    self.plt_opt.update({'linestyle': self.linestyles[i],
                                         'marker': self.markers[i],
                                         'markersize': self.markersizes[i]})
                    norm_factor = [1, 1]  # m.initial_state.data['mag'].v[0]]
                    PlottingOLD.dunlop.dunlop(self.ax1, thellier_obj=m, component=self.component, norm_factor=norm_factor,
                                           **self.plt_opt)
                    if self.std_fill:
                        PlottingOLD.dunlop.dunlop_std(self.ax1, thellier_obj=m, component=self.component,
                                                   norm_factor=norm_factor, **self.plt_opt)

        treats = sorted(d.keys())
        initial = min(treats)
        permutations = [(initial, t) for t in treats]

        ax2_lines = []
        ax2_lines.append(th_line)
        ax2_lines.append(ptrm_line)

        for i, perm in enumerate(permutations):
            A = d[perm[0]]
            B = d[perm[1]]
            for a in A:
                for b in B:
                    diff = (str(perm) + ' GPa', {'color': 'k', 'linestyle': '', 'marker': self.markers[i]})
                    ax2_lines.append(diff)
                    norm_factor = [1, 1]  # b.initial_state.data['mag'].v[0]]

                    self.plt_opt.update({'linestyle': self.linestyles[i],
                                         'marker': self.markers[i],
                                         'markersize': self.markersizes[i],
                    })
                    PlottingOLD.dunlop.difference(self.ax2, a, b, component=self.component, norm_factor=norm_factor,
                                               **self.plt_opt)

                    if self.std_fill:
                        PlottingOLD.dunlop.difference_std(self.ax2, a, b, component=self.component,
                                                       norm_factor=norm_factor, **self.plt_opt)

        self.ax1.set_title('Dunlop %s' % self.sample_names)
        self.ax2.set_title('differences')

        self.ax2.legend([self.create_dummy_line(**l[1]) for l in ax2_lines],
        # Line titles
        [l[0] for l in ax2_lines],
        loc='best'
        )
        self.ax1.legend([self.create_dummy_line(**l[1]) for l in ax1_lines],
                        # Line titles
        [l[0] for l in ax1_lines],
        loc='best',
        fontsize=8,
        )
        self.ax2.set_xlabel = 'Temperature [$^\\circ C$]'
        self.ax1.set_ylabel = 'Magnetic Moment'
        self.ax2.set_ylabel = 'M($P_0)-M($P_n$)'


class Dunlop_Treatments_Derivative(base.Generic):
    def __init__(self, sample_list, norm='mass',
                 t_min=20, t_max=700, component='mag',
                 line=True, check=True,
                 plot='show', folder=None, name='Dunlop_Treatments',
                 plt_opt=None, style='screen', ttype='pressure',
                 **options):
        """

        implemented options:
           arai_line: adds the line fit to the arai_plot

        """

        super(Dunlop_Treatments_Derivative, self).__init__(sample_list, norm=norm,
                                                           plot=plot, folder=folder, name=name,
                                                           plt_opt=plt_opt, style=style,
                                                           create_fig=False, create_ax=False,
                                                           **options)
        self.std_fill = options.pop('std_fill', False)
        self.ttype = ttype
        self.component = component
        self.fig = plt.figure(figsize=(11.69, 8.27))
        self.ax1 = plt.subplot2grid((4, 1), (0, 0), rowspan=2)
        self.ax2 = plt.subplot2grid((4, 1), (2, 0), rowspan=2)
        self.show()
        plt.tight_layout()
        self.out('no_lable', 'no_legend')


    def show(self):
        d = self.sample_group.treatment_dict[self.ttype]

        th_line = ('TH', {'color': 'g', 'linestyle': '-', 'marker': '.'})
        ptrm_line = ('PTRM', {'color': 'b', 'linestyle': '-', 'marker': '.'})
        sum_line = ('SUM', {'color': 'r', 'linestyle': '-', 'marker': '.'})

        ax1_lines = []
        ax1_lines.append(th_line)
        ax1_lines.append(ptrm_line)
        ax2_lines = ax1_lines
        ax1_lines.append(sum_line)

        for i, tval in enumerate(sorted(d.keys())):
            self.markers[i] = '.'
            self.markersizes[i] = 1 + tval * 5
            ax1_lines.append(
                (str(tval) + ' GPa', {'color': 'k', 'linestyle': self.linestyles[i], 'marker': self.markers[i],
                                      'markersize': self.markersizes[i]}))
            ax2_lines.append((str(tval) + ' GPa', {'color': 'k', 'linestyle': self.linestyles[i], 'marker': '',
                                                   'markersize': self.markersizes[i]}))
            for j, m in enumerate(d[tval]):
                if m.mtype == 'thellier':
                    self.plt_opt.update({'linestyle': self.linestyles[i],
                                         'marker': self.markers[i],
                                         'markersize': self.markersizes[i]})
                    norm_factor = [1, 1]  # m.initial_state.data['mag'].v[0]]
                    PlottingOLD.dunlop.dunlop(self.ax1, thellier_obj=m, component=self.component, norm_factor=norm_factor,
                                           **self.plt_opt)

                    if self.std_fill:
                        PlottingOLD.dunlop.dunlop_std(self.ax1, thellier_obj=m, component=self.component,
                                                   norm_factor=norm_factor,
                                                   **self.plt_opt)

                    PlottingOLD.dunlop.derivative(self.ax2, thellier_obj=m, component=self.component,
                                               norm_factor=norm_factor, diff=1, interpolate=False,
                                               **self.plt_opt)

        # self.ax1.set_ylim([0, 1.1])
        self.ax2.set_xlim(self.ax1.get_xlim())  # ax1 & ax2 same xlim()
        self.ax1.set_title('Dunlop %s' % self.sample_names)
        self.ax2.set_title('derivatives')
        self.ax1.set_xlabel('Temperature [$^\\circ C$]')
        self.ax2.set_xlabel('Temperature [$^\\circ C$]')
        self.ax1.set_ylabel('Magnetic Moment')
        self.ax2.set_ylabel('dM($P_n$)(T)/dT')
        #
        self.ax1.legend([self.create_dummy_line(**l[1]) for l in ax1_lines],
                        # Line titles
                        [l[0] for l in ax1_lines],
                        loc='best',
                        fontsize=10,
        )


class Dunlop_vs_Treatment(base.Generic):
    def __init__(self, sample_list, norm='mass',
                 ttype='pressure', component='mag',
                 plot='show', folder=None, name='arai plot',
                 plt_opt=None, style='screen',
                 **options):
        """

        implemented options:
           arai_line: adds the line fit to the arai_plot

        """
        self.ttype = ttype
        self.component = component
        super(Dunlop_vs_Treatment, self).__init__(sample_list, norm=norm,
                                                  plot=plot, folder=folder, name=name,
                                                  plt_opt=plt_opt, style=style,
                                                  create_fig=False, create_ax=False,
                                                  **options)
        self.fig = plt.figure(figsize=(11.69, 8.27))
        self.th = plt.subplot2grid((6, 1), (0, 0), rowspan=2)
        self.ptrm = plt.subplot2grid((6, 1), (2, 0), rowspan=2)
        self.sum = plt.subplot2grid((6, 1), (4, 0), rowspan=2)
        self.fig.suptitle(self.sample_names)
        self.show(**options)
        plt.tight_layout(rect=(0, 0, 0.9, 0.95))
        self.out('no_legend')

    def show(self, **options):
        plottable = ['th', 'ptrm', 'sum']

        for sample in self.sample_list:
            ddict = self._treatment_variable_transformation(sample, mtype='thellier', ttype=self.ttype)
            for dtype, data in ddict.iteritems():
                if dtype in plottable:
                    values = sorted(list(set(data['variable'].v)))
                    colors = self.create_heat_color_map(values)
                    for varval in values:
                        idx = np.where(data['variable'].v == varval)[0]
                        plot_data = data.filter_idx(idx)
                        getattr(self, dtype).plot(plot_data['ttype ' + self.ttype].v, plot_data[self.component].v,
                                                  '-',
                                                  color=colors[values.index(varval)],
                                                  linewidth=0.5,
                                                  label=varval)
                        getattr(self, dtype).plot(plot_data['ttype ' + self.ttype].v, plot_data[self.component].v,
                                                  '.',
                                                  color=colors[values.index(varval)],
                        )
                        getattr(self, dtype).set_title(dtype)
                        getattr(self, dtype).set_ylabel('M($P_n$) / M(TRM)')
                        getattr(self, dtype).set_xlabel(self.ttype)
                        getattr(self, dtype).set_xlim([0, 1.8])
        self.th.legend(bbox_to_anchor=(1.01, -0.8, 0.3, 0.102), loc=3,
                       ncol=1, mode="expand", borderaxespad=0., fontsize=10,
                       frameon=False,
        )


class T0_vs_Tn(base.Generic):
    def __init__(self, sample_list, norm='mass',
                 ttype='pressure', component='mag',
                 plot='show', folder=None, name='arai plot',
                 plt_opt=None, style='screen',
                 **options):
        """

        implemented options:
           arai_line: adds the line fit to the arai_plot

        """
        self.ttype = ttype
        self.component = component
        super(T0_vs_Tn, self).__init__(sample_list, norm=norm,
                                       plot=plot, folder=folder, name=name,
                                       plt_opt=plt_opt, style=style,
                                       create_fig=False, create_ax=False,
                                       **options)
        self.fig = plt.figure(figsize=(11.69, 5.8))
        self.th = plt.subplot2grid((1, 2), (0, 0))
        self.ptrm = plt.subplot2grid((1, 2), (0, 1))
        self.fig.suptitle(self.sample_names)

        self.show(**options)
        plt.tight_layout()
        self.out('no_legend')

    def show(self, **options):
        plottable = ['th', 'ptrm']

        for sample in self.sample_list:
            ddict = self._treatment_variable_transformation(sample, mtype='thellier', ttype=self.ttype)
            for dtype, data in ddict.iteritems():
                if dtype in plottable:
                    values = sorted(list(set(data['variable'].v)))
                    colors = self.create_heat_color_map(values)
                    for varval in values:
                        tvals = sorted(list(set(data['ttype ' + self.ttype].v)))
                        for tval in tvals:
                            idx0 = [i for i in range(len(data['variable'].v))
                                    if data['ttype ' + self.ttype].v[i] == 0
                                    if data['variable'].v[i] == varval]
                            idxn = [i for i in range(len(data['variable'].v))
                                    if data['ttype ' + self.ttype].v[i] == tval
                                    if data['variable'].v[i] == varval]
                            if idx0 and idxn:
                                T0_data = data.filter_idx(idx0)
                                Tn_data = data.filter_idx(idxn)
                                getattr(self, dtype).plot(
                                    Tn_data[self.component].v,
                                    T0_data[self.component].v,
                                    color=colors[values.index(varval)],
                                    marker='.',
                                    markersize=1 + tval * 7,
                                    linestyle='',
                                    # linewidth=0.5,
                                    label=varval)
                    getattr(self, dtype).set_title(dtype)
                    getattr(self, dtype).set_ylabel('M($P_n$) / M(TRM)')
                    getattr(self, dtype).set_xlabel('M($P_0$) / M(TRM)')
                    getattr(self, dtype).grid()
                    getattr(self, dtype).plot([0, 1.2], [0, 1.2], '--', color='#808080')


class Arai(base.Generic):
    def __init__(self, sample_list, norm=None,
                 t_min=20, t_max=700, component='mag',
                 line=True, check=True,
                 plot='show', folder=None, name=None,
                 plt_opt=None, style='screen',
                 **options):

        super(Arai, self).__init__(sample_list, norm=norm,
                                   plot=plot, folder=folder, name=name,
                                   plt_opt=plt_opt, style=style,
                                   **options)

        self.parameter = {'t_min': t_min,
                          't_max': t_max,
                          'component': component}

        self.show()
        self.x_label = 'pTRM gained [%s]' % ('Am2')  # todo get_unit
        self.y_label = 'NRM remaining [%s]' % ('Am2')  # todo get_unit
        self.ax.set_title('%s' % self.sample_names)
        if style == 'publication':
            self.setFigLinesBW()

        self.out()

    def show(self):
        x = []
        y = []
        measurement_dict = self.get_measurement_dict(mtype='thellier')
        arai.arai_1_1_line(self.ax)
        for sample in measurement_dict:
            thellier_objects = measurement_dict[sample]
            for thellier in thellier_objects:
                if self.norm:
                    tt = thellier.normalizeOLD(reference=self.norm, rtype=self.rtype,
                                            vval=self.vval, norm_method=self.norm_method)
                else:
                    tt = thellier
                    # print tt.data['th']
                plt_opt = self.get_plt_opt(sample, thellier_objects, thellier)
                if len(self.sample_list) > 1 or len(thellier_objects) > 1:
                    plt_opt.update({'label': sample.name})
                # arai.arai_std(self.ax, tt, self.parameter, **plt_opt)
                arai.arai_error(self.ax, tt, self.parameter, **plt_opt)
                arai.arai_line(self.ax, tt, self.parameter, **plt_opt)
                plt_opt.update({'linewidth': 0.5})
                arai.arai_points(self.ax, tt, self.parameter, **plt_opt)
                # Features.arai.add_ck_check(self.ax, tt)
                # x.append(max(thellier.ptrm[self.parameter['component']].v))  # append max for x_lim
                # y.append(max(thellier.th[self.parameter['component']].v))  # append max for y_lim
        if len(self.sample_list) > 1 or len(thellier_objects) > 1:
            self.ax.legend(loc='best')
            # self.ax.set_xlim([0, max(x)])
            # self.ax.set_ylim([0, max(y)])