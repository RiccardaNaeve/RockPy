__author__ = 'mike'
import matplotlib.pyplot as plt
import base
import arai
from RockPy import Plotting


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
        self.title= 'Dunlop Plot %s' %self.sample_names
        self.x_label = 'Temperature [C]'
        self.y_label = 'Moment'

        self.show(**options)
        self.out()

    def show(self, **options):
        measure_dict = self.get_measurement_dict(mtype='thellier')
        for sample in measure_dict:
            for measurement in measure_dict[sample]:
                norm_factor = self.get_norm_factor(measurement)
                plt_opt = self.get_plt_opt(sample=sample, measurements=measure_dict[sample], measurement=measurement)
                Plotting.dunlop.dunlop(self.ax, measurement, norm_factor=norm_factor, **plt_opt)

                if 'std_fill' in options:
                    Plotting.dunlop.dunlop_std(self.ax, measurement, norm_factor=norm_factor, **plt_opt)

    def get_norm_factor(self, measurement):
        implemented = {'is':
        self._get_initial_state_normalizer}
        try:
            out = [1.0, implemented[self.norm](measurement)]
        except KeyError:
            self.log.error('NORMALIZATION method << %s >> not implemented' %self.norm)
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

        super(Dunlop_Treatments, self).__init__(sample_list, norm=norm,
                                                plot=plot, folder=folder, name=name,
                                                plt_opt=plt_opt, style=style,
                                                create_fig=True, create_ax=False,
                                                **options)
        self.ttype = ttype
        self.component = component
        # self.fig = plt.figure()
        self.ax1 = plt.subplot2grid((4, 1), (0, 0), rowspan=2)
        self.ax2 = plt.subplot2grid((4, 1), (2, 0), rowspan=2)
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
            self.markersizes[i] = 1+ tval * 5
            ax1_lines.append((str(tval) +' GPa',{'color':'k', 'linestyle': self.linestyles[i],'marker': self.markers[i],
                                         'markersize': self.markersizes[i]}))
            for j, m in enumerate(d[tval]):
                if m.mtype == 'thellier':
                    self.plt_opt.update({'linestyle': self.linestyles[i],
                                         'marker': self.markers[i],
                                         'markersize': self.markersizes[i]})
                    norm_factor = [1, 1]#m.initial_state.data['mag'].v[0]]
                    Plotting.dunlop.dunlop(self.ax1, thellier_obj=m, component=self.component, norm_factor=norm_factor, **self.plt_opt)
                    if self.std_fill:
                        Plotting.dunlop.dunlop_std(self.ax1, thellier_obj=m, component=self.component, norm_factor=norm_factor, **self.plt_opt)

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
                    norm_factor = [1, 1]#b.initial_state.data['mag'].v[0]]

                    self.plt_opt.update({'linestyle': self.linestyles[i],
                                         'marker': self.markers[i],
                                         'markersize': self.markersizes[i],
                                         })
                    Plotting.dunlop.difference(self.ax2, a, b, component=self.component,  norm_factor=norm_factor, **self.plt_opt)

                    if self.std_fill:
                        Plotting.dunlop.difference_std(self.ax2, a, b, component=self.component,  norm_factor=norm_factor, **self.plt_opt)


        self.ax1.set_title('Dunlop %s' % self.sample_names)
        self.ax2.set_title('differences')

        # self.ax2.legend([self.create_dummy_line(**l[1]) for l in ax2_lines],
        #                # Line titles
        #                [l[0] for l in ax2_lines],
        #                loc='best'
        # )
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
        self.fig = plt.figure(figsize=(11.69,8.27))
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
                    norm_factor = [1, 1]# m.initial_state.data['mag'].v[0]]
                    Plotting.dunlop.dunlop(self.ax1, thellier_obj=m, component=self.component, norm_factor=norm_factor,
                                  **self.plt_opt)

                    if self.std_fill:
                        Plotting.dunlop.dunlop_std(self.ax1, thellier_obj=m, component=self.component, norm_factor=norm_factor,
                                  **self.plt_opt)

                    Plotting.dunlop.derivative(self.ax2, thellier_obj=m, component=self.component,
                                      norm_factor=norm_factor, diff=1, interpolate=False,
                                      **self.plt_opt)

        self.ax1.set_ylim([0,1.1])
        self.ax2.set_xlim(self.ax1.get_xlim()) #ax1 & ax2 same xlim()
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