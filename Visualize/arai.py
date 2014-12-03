__author__ = 'mike'
import base
from RockPy.Plotting import arai
import matplotlib.pyplot as plt

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
        self.x_label = 'pTRM gained [%s]' % ('Am^2')  # todo get_unit
        self.y_label = 'NRM remaining [%s]' % ('Am^2')  # todo get_unit
        self.ax.set_title('%s'%self.sample_names)
        if style == 'publication':
            self.setFigLinesBW()

        self.out()

    def show(self):
        x = []
        y = []
        measurement_dict = self.get_measurement_dict(mtype='thellier')
        for sample in measurement_dict:
            thellier_objects = measurement_dict[sample]
            for thellier in thellier_objects:
                if self.norm:
                    tt = thellier.normalize(reference = self.norm, rtype = self.rtype,
                                            vval = self.vval, norm_method = self.norm_method)
                else:
                    tt = thellier
                    # print tt.data['th']
                plt_opt = self.get_plt_opt(sample, thellier_objects, thellier)
                if len(self.sample_list)>1 or len(thellier_objects)>1:
                    plt_opt.update({'label': sample.name})
                arai.arai_std(self.ax, tt, self.parameter, **plt_opt)
                arai.arai_line(self.ax, tt, self.parameter, **plt_opt)
                plt_opt.update({'linewidth': 0.5})
                arai.arai_points(self.ax, tt, self.parameter, **plt_opt)

                # x.append(max(thellier.ptrm[self.parameter['component']].v))  # append max for x_lim
                # y.append(max(thellier.th[self.parameter['component']].v))  # append max for y_lim
        if len(self.sample_list)>1 or len(thellier_objects)>1:
            self.ax.legend(loc='best')
        # self.ax.set_xlim([0, max(x)])
        # self.ax.set_ylim([0, max(y)])