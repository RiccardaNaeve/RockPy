from Structure.rockpydata import rockpydata

__author__ = 'volk'
import base
import Structure.data
import Structure.rockpydata
import matplotlib.pyplot as plt
import numpy as np


class Backfield(base.Measurement):
    '''
    A Backfield Curve can give information on:
       Bcr: the remanence coercivity
       S300: :math:`(1 - (M_{300mT} /M_{rs})) / 2

    Bcr is determined by finding the intersection of the linear interpolated measurement data with the axis
    representing zero-magnetization.
    For the calculation of S300, the initial magnetization is used as an approximation of the saturation remanence
    :math:`M_{rs}` and the magnetization at 300mT :math:`M_{300mT} is determined by linear interpolation of measured
    data.
    '''

    def __init__(self, sample_obj,
                 mtype, mfile, machine,
                 **options):
        super(Backfield, self).__init__(sample_obj, mtype, mfile, machine)

    def format_vftb(self):
        '''
        formats the output from vftb to measurement. data
        :return:
        '''
        data = self.machine_data.out_backfield()
        header = self.machine_data.header()
        self.remanence = rockpydata(column_names=header, data=data[0])
        self.induced = None

    @property
    def bcr(self):
        '''
        returns the bcr value if already calculated,
        calls calculate_bcr if not yet calculated
        :return:
        '''
        if self.results['bcr'] is None or self.results['bcr'] == 0:
            self.calculate_bcr()
        return self.results['bcr'][0]

    @property
    def s300(self):
        if self.results['s300'] is None or self.results['s300'] == 0:
            self.results['s300'] = self.calculate_s300()
        return self.results['s300'][0]

    def result_bcr(self):
        if self.results['bcr'] is None:
            self.calculate_bcr()
        return self.results['bcr']

    def result_s300(self):
        if self.results['s300'] is None:
            self.calculate_s300()
        return self.results['s300']

    def calculate_bcr(self):
        '''
        calculates Bcr from linear interpolation between two points closest to mag = o

        Bcr is the field needed to demagnetize the saturation remanence

        :return: float
               calculated bcr value
        '''
        self.log.info('CALCULATING << Bcr >> parameter from linear interpolation')
        self.log.info('               ---    If sample is not saturated, value could be too low')

        idx = np.argmin(np.abs(self.remanence['mag']))  # index of closest to 0

        if self.remanence['mag'][idx] < 0:
            idx1 = idx
            idx2 = idx - 1
        else:
            idx1 = idx + 1
            idx2 = idx

        i = [idx1, idx2]
        tf_array = [True if x in i else False for x in range(len(self.remanence['mag']))]
        d = self.remanence.filter(tf_array=tf_array)
        slope, sigma, y_intercept, x_intercept = d.lin_regress('field', 'mag')
        bcr = - y_intercept / slope
        self.results['bcr'] = bcr


    def calculate_s300(self):
        '''
        S300: :math:`(1 - (M_{300mT} /M_{rs})) / 2
        :return:
        '''
        self.log.info('CALCULATING << S300 >> parameter, assuming measurement started in saturation remanence')
        idx = np.argmin(np.abs(self.remanence['field'] + 0.300))

        if abs(self.remanence['field'][idx]) < 0.300:
            idx2 = idx
            idx1 = idx + 1
        else:
            idx1 = idx
            idx2 = idx - 1

        i = [idx1, idx2]
        tf_array = [True if x in i else False for x in range(len(self.remanence['mag']))]

        d = self.remanence.filter(tf_array=tf_array)
        slope, sigma, y_intercept, x_intercept = d.lin_regress('field', 'mag')

        m300 = y_intercept + (slope * 0.3)
        mrs = self.remanence['mag'][0]

        s300 = (1 - ( m300 / mrs)) / 2

        return s300

    def plt_backfield(self):
        plt.plot(self.remanence['field'], self.remanence['mag'], '.-', zorder=1)
        plt.plot(self.bcr, 0.0, 'x', color='k')

        if self.induced:
            plt.plot(self.induced['field'], self.induced['mag'], zorder=1)

        plt.axhline(0, color='#808080')
        plt.axvline(0, color='#808080')
        plt.grid()
        plt.title('Backfield %s' % (self.sample_obj.name))
        plt.xlabel('Field [%s]' % ('T'))  # todo replace with data unit
        plt.ylabel('Moment [%s]' % ('Am^2'))  # todo replace with data unit
        plt.show()