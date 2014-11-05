__author__ = 'mike'
import base
import Plotting.hysteresis

class T_v_Hys(base.Generic):
    def __init__(self, sample_list, norm='mass',
                 plot='show', folder=None, name='arai plot',
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
        for S in measurement_dict:
            for measurement in measurement_dict[S]:
                if measurement.virgin:
                    Plotting.hysteresis.vigin_branch(self.ax, measurement)

                Plotting.hysteresis.up_field_branch(self.ax, measurement)
                Plotting.hysteresis.down_field_branch(self.ax, measurement)