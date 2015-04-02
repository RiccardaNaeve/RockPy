__author__ = 'mike'
__author__ = 'volk'
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
import base
from RockPy.Structure.data import RockPyData
from math import log

class Viscosity(base.Measurement):
    @staticmethod
    def fit_viscous_relaxation(ln_time, mag):
        """
        Fits a line through ln(time) and magnetic moment

        Parameters
        ----------
           ln_time: ndarray
              natural logarithm of time
           mag: ndarray
              magnetic moments

        Returns
        -------
           slope: float
           intercept: float
           std_error: float
           r_value: float
        """
        slope, intercept, r_value, p_value, std_err = stats.linregress(ln_time, mag)
        return slope, intercept, std_err, r_value

    def __init__(self, sample_obj,
                 mtype, mfile, machine,
                 ommit_first_n_values=2,
                 **options):

        super(Viscosity, self).__init__(sample_obj, mtype, mfile, machine)

    # formatting
    def format_vsm(self):
        """
        Formatting for viscosity Measurements from VSM machine
        """
        data = self.machine_data.out
        header = self.machine_data.header
        self._raw_data['data'] = RockPyData(column_names=['time', 'mag', 'field'], data=data[0][:])
        self._raw_data['data'] = self._raw_data['data'].append_columns(column_names=['ln_time'], data=np.log(self._raw_data['data']['time'].v))

    def correct_ommit_first_n(self, n=2):
        """
        ommits the first n points of the data.

        Parameter
        ---------
           n: int
              number of points at beginning of dataset to be ommitted in subsequent analysis
        """

        self.data['data'].data = self.data['data'].data[n:]

    def result_visc_decay(self, ommit_first_n=0, recalc=False, **options):
        """

        :param recalc:
        :return:
        """

        parameter = dict(ommit_first_n=ommit_first_n)
        parameter.update(options)

        self.calc_result(parameter, recalc=recalc)
        return self.results['visc_decay']


    def calculate_visc_decay(self, **parameter):
        """

        :return:
        """
        ommit_first_n = parameter.get('ommit_first_n', 0)
        slope, intercept, std_err, r_value = self.fit_viscous_relaxation(self.data['data']['ln_time'].v[ommit_first_n:], self.data['data']['mag'].v[ommit_first_n:])


        self.results['visc_decay'] = slope
        self.results['visc_decay'].e = [[std_err]]

        self.calculation_parameter['visc_decay'].update(parameter)
        return slope, std_err

    def plt_viscosity(self):
        plt.plot(self.data['data']['log_time'].v, self.data['data']['mag'].v)
        plt.show()