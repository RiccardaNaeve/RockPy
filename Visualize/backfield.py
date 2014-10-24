__author__ = 'mike'
import base
import Plotting.backfield


class Backfield(base.Generic):
    def __init__(self, sample_list, norm='mass',
                 plot='show', folder=None, name='arai plot',
                 plt_opt=None, style='screen',
                 **options):
        super(Backfield, self).__init__(sample_list, norm=None,
                                        plot=plot, folder=folder, name=name,
                                        plt_opt=plt_opt, style=style,
                                        **options)

        self.show()
        self.x_label = 'Field [%s]' % ('T')  # todo get_unit
        self.y_label = 'Magnetic Moment [%s]' % ('Am^2')  # todo get_unit

        if style == 'publication':
            self.setFigLinesBW()

        self.set_xlim(**options)
        self.set_ylim(**options)
        self.out()

    def show(self):
        mdict = self.get_measurement_dict(mtype='backfield')

        for sample, measurements in mdict.iteritems():
            for measurement in measurements:
                plt_opt = self.get_plt_opt(sample, measurements, measurement)
                Plotting.backfield.zero_line(self.ax, linestyle='-', linewidth=0.6, zorder=0)
                Plotting.backfield.backfield(self.ax, measurement, **plt_opt)
                self.ax.grid(True)
