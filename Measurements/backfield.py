__author__ = 'volk'
import matplotlib.pyplot as plt
import numpy as np
import logging
from RockPy.Structure.data import RockPyData
import base
from copy import deepcopy

class Backfield(base.Measurement):
    logger = logging.getLogger('RockPy.MEASUREMENT.Backfield')
    """
    A Backfield Curve can give information on:
       Bcr: the remanence coercivity

       S300: :math:`(1 - (M_{300mT} /M_{rs})) / 2`

    Bcr is determined by finding the intersection of the linear interpolated measurement data with the axis
    representing zero-magnetization.
    For the calculation of S300, the initial magnetization is used as an approximation of the saturation remanence
    :math:`M_{rs}` and the magnetization at 300mT :math:`M_{300mT}` is determined by linear interpolation of measured
    data.

    Possible data structure::

       self.remanence: the remanence measurement after the field was applied (normal measurement mode for e.g. VFTB or VSM)
       self.induced: the induced moment measurement while the field is applied (only VSM)

    Notes
    -----
    - VSM- files with irm acquisition will add a new irm_acquisition measurement to the sample

    """

    def __init__(self, sample_obj,
                 mtype, mfile, machine,
                 **options):

        super(Backfield, self).__init__(sample_obj,
                                        mtype, mfile, machine,
                                        **options)

    def format_vftb(self):
        '''
        formats the output from vftb to measurement.data
        :return:
        '''
        data = self.machine_data.out_backfield()
        header = self.machine_data.header
        self._raw_data['remanence'] = RockPyData(column_names=header, data=data[0])
        self._raw_data['induced'] = None

    def format_vsm(self):
        """
        formats the vsm output to be compatible with backfield measurements
        :return:
        """
        data = self.machine_data.out_backfield()
        header = self.machine_data.header

        # check for IRM acquisition -> index is changed
        data_idx = 0

        if self.machine_data.measurement_header['SCRIPT']['Include IRM?'] == 'Yes':
            data_idx += 1
            self.logger.info('IRM acquisition measured, adding new measurement')
            irm = self.sample_obj.add_measurement(mtype='irm_acquisition', mfile=self.mfile, machine=self.machine)
            irm._series = self._series

        self._raw_data['remanence'] = RockPyData(column_names=['field', 'mag'], data=data[data_idx][:, [0, 1]])

        if self.machine_data.measurement_header['SCRIPT']['Include direct moment?'] == 'Yes':
            self._raw_data['induced'] = RockPyData(column_names=['field', 'mag'], data=data[data_idx + 1][:, [0, 2]])
        else:
            self._raw_data['induced'] = None


    @property
    def bcr(self):
        '''
        returns the bcr value if already calculated,
        calls calculate_bcr if not yet calculated
        :return:
        '''
        if self.results['bcr'] is None or self.results['bcr'].v == np.nan:
            self.calculate_bcr()
        return self.results['bcr'].v

    @property
    def s300(self):
        if self.results['s300'] is None or self.results['s300'].v == np.nan:
            self.results['s300'] = self.calculate_s300()
        return self.results['s300'].v


    def result_bcr(self, recalc=False):
        """
        calculates :math:`B_{cr}`
        :param recalc:
        :return:

        .. doctest::
           >>> import RockPy
           >>> vftb_file = tutorials.rst
           >>> sample = RockPy.Sample(name='vftb_test_sample')
           >>> M = sample.add_measurement(mtype='backfield', mfile=vftb_file, machine='vftb')
           >>> M.calculate_bcr()
           >>> print M.bcr
           0.0202307972682
        """
        parameter = {}
        self.calc_result(parameter, recalc)

        return self.results['bcr']

    def result_s300(self, recalc=False):
        parameter = {}
        self.calc_result(parameter, recalc)
        return self.results['s300']

    def result_mrs(self, recalc=False):
        parameter = {}
        self.calc_result(parameter, recalc)
        return self.results['mrs']

    def result_ms(self, recalc=False):
        parameter = {}
        self.calc_result(parameter, recalc)
        return self.results['ms']


    def calculate_bcr(self, **parameter):
        '''
        calculates Bcr from linear interpolation between two points closest to mag = o

        Bcr is the field needed to demagnetize the saturation remanence

        :return: float
               calculated bcr value
        '''
        Backfield.logger.info('CALCULATING << Bcr >> parameter from linear interpolation')
        Backfield.logger.info('               ---    If sample is not saturated, value could be too low')

        idx = np.argmin(np.abs(self.data['remanence']['mag'].v))  # index of closest to 0

        if self.data['remanence']['mag'].v[idx] < 0:
            i = [idx - 1, idx]
        else:
            i = [idx, idx + 1]
        # tf_array = [True if x in i else False for x in range(len(self.data['remanence']['mag'].v))]
        d = self.data['remanence'].filter_idx(i)

        slope, sigma, y_intercept, x_intercept = d.lin_regress('field', 'mag')
        bcr = - y_intercept / slope
        self.results['bcr'] = abs(bcr)

    def calculate_s300(self, **parameter):
        '''
        S300: :math:`(1 - (M_{300mT} /M_{rs})) / 2`

        :return: result
        '''
        Backfield.logger.info('CALCULATING << S300 >> parameter, assuming measurement started in saturation remanence')
        idx = np.argmin(np.abs(self._data['remanence']['field'].v + 0.300))

        if self.data['remanence']['field'].v.all() > 0.300:
            self.results['s300'] = np.nan
            return

        if self.data['remanence']['field'].v[idx] > 0.3:
            i = [idx - 1, idx]
        else:
            i = [idx, idx + 1]

        d = self.data['remanence'].filter_idx(i)
        slope, sigma, y_intercept, x_intercept = d.lin_regress('field', 'mag')

        m300 = y_intercept + (slope * 0.3)
        mrs = self.data['remanence']['mag'].v[0]

        s300 = (1 - ( m300 / mrs)) / 2

        self.results['s300'] = s300

    def calculate_mrs(self, **parameter):
        """
        Magnetic Moment at last measurement point
        :param parameter:
        :return:
        """
        start = self._data['remanence']['mag'].v[0]
        end = self._data['remanence']['mag'].v[-1]
        mrs = np.mean([abs(start), abs(end)])
        self.results['mrs'] = mrs

    def calculate_ms(self, **parameter):
        self.results['ms'] = None

    def plt_backfield(self):
        plt.plot(self.data['remanence']['field'].v, self.data['remanence']['mag'].v, '.-', zorder=1)
        plt.plot(-self.bcr, 0.0, 'x', color='k')

        if self.data['induced']:
            plt.plot(self._data['induced']['field'].v, self._data['induced']['mag'].v, zorder=1)

        plt.axhline(0, color='#808080')
        plt.axvline(0, color='#808080')
        plt.grid()
        plt.title('Backfield %s' % (self.sample_obj.name))
        plt.xlabel('Field [%s]' % ('T'))  # todo replace with data unit
        plt.ylabel('Moment [%s]' % ('Am2'))  # todo replace with data unit
        plt.show()