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

        data_formatting = {'vftb': self.format_vftb,
        }

        ### initialize
        self.remanence = None
        self.induced = None

        data_formatting[self.machine]()

        self.results = Structure.rockpydata.rockpydata(column_names=('bcr', 's300'))


    def format_vftb(self):
        '''
        formats the output from vftb to measurement. data
        :return:
        '''
        self.remanence = Structure.rockpydata.rockpydata(column_names=('field', 'moment', 'temperature', 'time',
                                                                  'std_dev', 'susceptibility'), data= self.raw_data)

    @property
    def bcr(self):#todo rockpydata stores value twice
        '''
        returns the bcr value if already calculated,
        calls calculate_bcr if not yet calculated
        :return:
        '''
        if self.results['bcr'] is None:
            self.calculate_bcr()
        return self.results['bcr'][0]

    @property
    def s300(self):#todo rockpydata stores value twice
        if self.results['s300'] is None:
            self.results['s300'] = self.calculate_s300()
        return self.results['s300'][0]

    def calculate_bcr(self):
        '''
        calculates Bcr from linear interpolation between two points closest to moment = o

        Bcr is the field needed to demagnetize the saturation remanence

        :return: float
               calculated bcr value
        '''
        self.log.info('CALCULATING << Bcr >> parameter from linear interpolation')
        self.log.info('               ---    If sample is not saturated, value could be too low')

        idx = np.argmin(np.abs(self.remanence['moment']))  # index of closest to 0

        if self.remanence['moment'][idx] < 0:
            idx1 = idx
            idx2 = idx - 1
        else:
            idx1 = idx + 1
            idx2 = idx

        i = [idx1, idx2]
        tf_array = [True if x in i else False for x in range(len(self.remanence['moment']))]
        d = self.remanence.filter(tf_array=tf_array)
        slope, sigma, y_intercept, x_intercept = d.lin_regress('field', 'moment')
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

        print self.remanence['field'][idx1], self.remanence['moment'][idx1]
        print self.remanence['field'][idx2], self.remanence['moment'][idx2]

        dx = self.remanence['field'][idx1] - self.remanence['field'][idx2]
        dy = self.remanence['moment'][idx1] - self.remanence['moment'][idx2]

        m = dy / dx
        y_intercept = self.remanence['moment'][idx2] + m * self.remanence['field'][idx2]

        m300 = y_intercept + (m * 0.3)
        mrs = self.remanence['moment'][0]
        print m, 'x', y_intercept
        print '-0.0385803 x-0.206456'
        s300 = (1 - ( m300 / mrs)) / 2

        return s300

    def plt_backfield(self):
        plt.plot(self.remanence['field'], self.remanence['moment'], '.-', zorder=1)
        plt.plot(self.bcr, 0.0, 'x', color='k')

        if self.induced:
            plt.plot(self.induced['field'], self.induced['moment'], zorder=1)

        plt.axhline(0, color='#808080')
        plt.axvline(0, color='#808080')
        plt.grid()
        plt.title('Backfield %s' %(self.sample_obj.name))
        plt.xlabel('Field [%s]' %('T')) #todo replace with data unit
        plt.ylabel('Moment [%s]' %('Am^2')) #todo replace with data unit
        plt.show()