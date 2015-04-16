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

        Parameters
        ----------
           n: int
              number of points at beginning of dataset to be ommitted in subsequent analysis
        """

        self.data['data'].data = self.data['data'].data[n:]

    def result_visc_decay(self, ommit_first_n=0, recalc=False, **options):
        """
        Calculates the result for the viscous decay

        Parameters
        ----------
           ommit_first_n: int
              the first n data points are not used for the calculation of the result
              *default* = 0
           recalc: bool
              if True it gets forced recalculated
              if False it is only recalculated if not previoiusly calculated or if the result has been calculated with
              different parameters
        Returns
        -------
           RockPyData
              result for viscous decay, not normalized

        Note
        ----
           For normalized viscous decay use :py:func:`result_visc_decay_norm`
        """

        parameter = dict(ommit_first_n=ommit_first_n)
        parameter.update(options)

        self.calc_result(parameter, recalc=recalc)
        return self.results['visc_decay']

    def result_visc_decay_norm(self, ommit_first_n=0, recalc=False, **options):
        """
        Calculates the result for the normalized viscous decay. Data is devided by the max(mag) before calculation.

        Parameters
        ----------
           ommit_first_n: int
              the first n data points are not used for the calculation of the result
              *default* = 0
           recalc: bool
              if True it gets forced recalculated
              if False it is only recalculated if not previoiusly calculated or if the result has been calculated with
              different parameters
        Returns
        -------
           RockPyData
              result for viscous decay, *normalized*

        Note
        ----
           For non-normalized viscous decay use :py:func:`result_visc_decay`
        """

        parameter = dict(ommit_first_n=ommit_first_n)
        parameter.update(options)

        self.calc_result(parameter, recalc=recalc, force_method='visc_decay')
        return self.results['visc_decay_norm']


    def calculate_visc_decay(self, **parameter):
        """
        Parameters
        ----------
           ommit_first_n: int

        :return:
        """
        ommit_first_n = parameter.get('ommit_first_n', 0)
        ln_time = self.data['data']['ln_time'].v[ommit_first_n:]
        mag = self.data['data']['mag'].v[ommit_first_n:]
        norm_mag = mag / max(mag)
        slope, intercept, std_err, r_value = self.fit_viscous_relaxation(ln_time=ln_time, mag=mag)
        norm_slope, norm_intercept, norm_std_err, norm_r_value = self.fit_viscous_relaxation(ln_time=ln_time, mag=norm_mag)
        self.results['visc_decay'] = [[[slope, std_err]]]
        self.results['visc_decay_norm'] = [[[norm_slope, norm_std_err]]]
        return slope, std_err, norm_slope, norm_std_err

    def plt_viscosity(self):
        plt.plot(self.data['data']['log_time'].v, self.data['data']['mag'].v)
        plt.show()