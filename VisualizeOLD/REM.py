__author__ = 'mike'
import matplotlib.pyplot as plt
import base
from PlottingOLD import af_demagnetization


class REM_dash_log(base.Generic):
    def __init__(self, sample_list, norm='mass',
                 plot='show', folder=None, name='REM_',
                 suffix_1='irm', suffix_2='nrm',
                 plt_opt={},
                 **options):

        super(REM_dash_log, self).__init__(sample_list=sample_list,
                                           norm=norm,
                                           plot=plot, folder=folder, name=name,
                                           **options)
        self.suffix_1 = suffix_1
        self.suffix_2 = suffix_2
        self.show()
        self.out()

    def show(self):

        for sample in self.sample_list:
            af_x = sample.get_measurements(mtype='afdemag', suffix=self.suffix_1)[0]
            af_y = sample.get_measurements(mtype='afdemag', suffix=self.suffix_2)[0]
            af_demagnetization.d_log_diff_af(af_demag_obj1=af_x, af_demag_obj2=af_y, ax=self.ax)
        af_demagnetization.d_log_iso_lines(ax=self.ax)

        self.ax.set_title('REM\' %s' % [i.name for i in self.sample_list])
        self.x_label = 'dM(%s)/dB(AF)' % self.suffix_1.upper()
        self.y_label = 'dM(%s)/dB(AF)' % self.suffix_2.upper()

        if len(self.sample_list) > 1:
            plt.legend(loc='best')
        plt.tight_layout(pad=2)