from Structure.rockpydata import rockpydata

__author__ = 'volk'
import base
import Structure.data
import matplotlib.pyplot as plt
import numpy as np


class ThermoCurve(base.Measurement):
    def __init__(self, sample_obj,
                 mtype, mfile, machine,
                 **options):
        super(ThermoCurve, self).__init__(sample_obj, mtype, mfile, machine)

        data_formatting = {'vftb': self.format_vftb,
        }
        # ## initialize
        self.data = None

        data_formatting[self.machine]()

    def format_vftb(self):
        tdiff = np.diff(self.raw_data['temp'])

        for i in range(len(tdiff)):
            if tdiff[i] < 0:
                idx = i
                break

        self.up_temp = rockpydata(variable=self.raw_data['temp'][:i], var_unit='C',
                                  measurement=self.raw_data['moment'][:i], measure_unit='$Am^2$',
                                  std_dev=self.raw_data['std_dev'][:i],
        )
        self.down_temp = rockpydata(variable=self.raw_data['temp'][i:], var_unit='C',
                                    measurement=self.raw_data['moment'][i:], measure_unit='$Am^2$',
                                    std_dev=self.raw_data['std_dev'][i:],
        )

    @property
    def ut(self):
        return self.up_temp

    @property
    def dt(self):
        return self.down_temp


    def plt_thermocurve(self):
        plt.plot(self.ut.variable, self.ut.measurement, 'r-')
        plt.plot(self.dt.variable, self.dt.measurement, 'b-')
        plt.xlabel(self.dt.var_unit)
        plt.ylabel(self.dt.measure_unit)
        plt.show()