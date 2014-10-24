__author__ = 'mike'
import base
from Plotting import arai


class Arai(base.Generic):
    def __init__(self, sample_list, norm='mass',
                 t_min=20, t_max=700, component='mag',
                 line=True, check=True,
                 plot='show', folder=None, name='arai plot',
                 plt_opt=None, style='screen',
                 **options):

        super(Arai, self).__init__(sample_list, norm=None,
                                   plot=plot, folder=folder, name=name,
                                   plt_opt=plt_opt, style=style,
                                   **options)

        self.parameter = {'t_min': t_min,
                          't_max': t_max,
                          'component': component}

        self.show()
        self.x_label = 'pTRM gained [%s]' % ('Am^2')  # todo get_unit
        self.y_label = 'NRM remaining [%s]' % ('Am^2')  # todo get_unit
        if style == 'publication':
            self.setFigLinesBW()

        self.out()

    def show(self):
        x = []
        y = []
        for sample in self.sample_list:
            thellier_objects = sample.get_measurements(mtype='thellier')
            for thellier in thellier_objects:
                arai.arai(self.ax, thellier, self.parameter, **self.plt_opt)
                arai.arai_line(self.ax, thellier, self.parameter, **self.plt_opt)

                x.append(max(thellier.ptrm[self.parameter['component']]))  # append max for x_lim
                y.append(max(thellier.th[self.parameter['component']]))  # append max for y_lim
        self.ax.set_xlim([0, max(x)])
        self.ax.set_ylim([0, max(y)])