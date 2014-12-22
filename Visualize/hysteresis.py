__author__ = 'mike'
import base
import Plotting.hysteresis
import matplotlib.pyplot as plt

class T_v_Hys(base.Generic):
    def __init__(self, sample_list, norm='mass',
                 plot='show', folder=None, name='Hys[T]',
                 plt_opt=None, style='screen',
                 **options):


        super(T_v_Hys, self).__init__(sample_list, norm=None,
                                      plot=plot, folder=folder, name=name,
                                      plt_opt=plt_opt, style=style,
                                      **options)

        self.show()
        self.out()

    def show(self):
        measurement_dict = self.get_measurement_dict(mtype='hysteresis')
        self.ax.axhline(0, color='k')
        self.ax.axvline(0, color='k')
        self.ax.grid()
        for S in measurement_dict:
            for i, measurement in enumerate(measurement_dict[S]):
                colors = self.create_heat_color_map(measurement_dict[S])

                if measurement.virgin:
                    Plotting.hysteresis.vigin_branch(self.ax, measurement)

                Plotting.hysteresis.up_field_branch(self.ax, measurement, color = colors[i], linewidth=0.5)
                Plotting.hysteresis.down_field_branch(self.ax, measurement, color = colors[i], linewidth=0.5)

        self.ax.set_xlabel('field [T]')
        self.ax.set_ylabel('Moment [Am2]')
        self.ax.set_xlim([-1,1])
        plt.tight_layout()
