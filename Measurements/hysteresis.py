__author__ = 'volk'
import numpy as np
import matplotlib.pyplot as plt

import base
from RockPy.Structure.data import RockPyData


class Hysteresis(base.Measurement):
    """

    .. testsetup:: *

       >>> from Structure.project import Sample
       >>> vftb_file = '../testing/test_data/MUCVFTB_test.hys'
       >>> sample = Sample(name='vftb_test_sample')
       >>> M = sample.add_measurement(mtype='hysteresis', mfile=vftb_file, machine='vftb')


    """

    def __init__(self, sample_obj,
                 mtype, mfile, machine,
                 **options):
        super(Hysteresis, self).__init__(sample_obj, mtype, mfile, machine, **options)


    # ## formatting functions
    def format_vftb(self):
        data = self.machine_data.out_hysteresis()
        header = self.machine_data.header
        self.induced = RockPyData(column_names=header, data=data[0])
        dfield = np.diff(self.induced['field'].v)

        idx = [i for i in range(len(dfield)) if dfield[i] < 0]
        virgin_idx = range(0, idx[0])
        down_field_idx = idx
        up_field_idx = range(idx[-1], len(dfield) + 1)

        self.virgin = self.induced.filter_idx(virgin_idx)
        self.down_field = self.induced.filter_idx(down_field_idx)
        self.up_field = self.induced.filter_idx(up_field_idx)

    def format_vsm(self):
        header = self.machine_data.header
        segments = self.machine_data.segment_info

        if 'adjusted field' in header:
            header[header.index('adjusted field')] = 'field'
            header[header.index('field')] = 'uncorrected field'

        if 'adjusted moment' in header:
            header[header.index('moment')] = 'uncorrected moment'
            header[header.index('adjusted moment')] = 'moment'

        if len(segments['segment number'].v) == 3:
            self.virgin = RockPyData(column_names=header, data=self.machine_data.out_hysteresis()[0])
            self.down_field = RockPyData(column_names=header, data=self.machine_data.out_hysteresis()[1])
            self.up_field = RockPyData(column_names=header, data=self.machine_data.out_hysteresis()[2])

        if len(segments['segment number'].v) == 2:
            self.virgin = None
            self.down_field = RockPyData(column_names=header, data=self.machine_data.out_hysteresis()[0])
            self.up_field = RockPyData(column_names=header, data=self.machine_data.out_hysteresis()[1])

        if len(segments['segment number'].v) == 1:
            self.virgin = RockPyData(column_names=header, data=self.machine_data.out_hysteresis()[0])
            self.down_field = None
            self.up_field = None

        try:
            self.virgin.rename_column('moment', 'mag')
        except AttributeError:
            pass

        try:
            self.up_field.rename_column('moment', 'mag')
        except AttributeError:
            pass

        try:
            self.down_field.rename_column('moment', 'mag')
        except AttributeError:
            pass

    def format_microsense(self):
        data = self.machine_data.out_hys()
        header = self.machine_data.header

        self.raw_data = RockPyData(column_names=header, values=data)
        dfield = np.diff(self.raw_data['raw_applied_field_for_plot_'])
        down_field_idx = [i for i in range(len(dfield)) if dfield[i] < 0]
        up_field_idx = [i for i in range(len(dfield)) if dfield[i] > 0]

        self.down_field = self.raw_data.filter_idx(down_field_idx)
        self.down_field.define_alias('field', 'raw_applied_field_for_plot_')
        self.down_field.define_alias('mag', 'raw_signal_mx')
        self.down_field['field'] *= 0.1 * 1e-3  # conversion Oe to Tesla

        self.up_field = self.raw_data.filter_idx(up_field_idx)
        self.up_field.define_alias('field', 'raw_applied_field_for_plot_')
        self.up_field.define_alias('mag', 'raw_signal_mx')
        self.up_field['field'] *= 0.1 * 1e-3  # conversion Oe to Tesla

        self.virgin = None
        self.msi = None

    # ## calculations

    def irrev(self, **options):
        irrev = self.down_field
        irrev -= self.up_field
        return irrev

    # ## parameters
    @property
    def ms(self):
        '''
        returns the :math:`M_{s}` value if already calculated,
        calls calculate_ms if not yet calculated
        :return:
        '''
        if self.results['ms'] is None:
            self.calculate_ms()
            # return self.results['ms'][0]

    @property
    def mrs(self):
        '''

        returns the :math:`M_{rs}` value if already calculated,
        calls calculate_mrs if not yet calculated

        :return:
        '''
        if self.results['mrs'] is None:
            self.calculate_mrs()
            # return self.results['mrs'][0]

    @property
    def bc(self):
        '''

        returns the :math:`B_{c}` value if already calculated,
        calls calculate_bc if not yet calculated

        :return:
        '''
        if self.results['bc'] is None:
            self.calculate_bc()
        return np.mean(self.results['bc'])

    @property
    def bc_diff(self):
        '''

        returns the difference between down_field and up_field calculation of :math:`\Delta B_c`

        :return: float
        '''
        return self.results['sigma_bc']

    @property
    def brh(self):
        '''
        returns the :math:`B_{rh}` value if already calculated,
        calls calculate_brh if not yet calculated
        :return:
        '''
        if self.results['brh'] is None:
            self.calculate_brh()
            # return self.results['brh'][0]

    @property
    def generic(self):
        '''
        helper function that returns the value for a given statistical method. If result not available will calculate
        it with standard parameters
        '''
        return self.result_generic()

    # ## results

    def result_generic(self, parameters='standard', recalc=False):
        '''
        Generic for for result implementation. Every calculation of result should be in the self.results data structure
        before calculation.
        It should then be tested if a value for it exists, and if not it should be created by calling
        _calculate_result_(result_name).

        '''
        self.calc_result(parameters, recalc)
        return self.results['generic']

    def result_ms(self, recalc=False):
        self.calc_result(dict(), recalc)
        return self.results['ms']

    def result_mrs(self, recalc=False):
        self.calc_result(dict(), recalc)
        return self.results['mrs']

    def result_bc(self, recalc=False, **options):
        """
        Calculates :math:`B_c` using a linear interpolation between the points closest to zero.

        :param recalc: bool
                     Force recalculation if already calculated

        .. doctest::
           from Structure.project import Sample

           vftb_file = 'test_data/MUCVFTB_test.hys'
           sample = Sample(name='vftb_test_sample')
           M = sample.add_measurement(mtype='hysteresis', mfile=vftb_file, machine='vftb')
           M.result_bc()

           >>> 0.00647949
        """
        self.calc_result(dict(), recalc)
        return self.results['bc']

    def result_sigma_bc(self, recalc=False):
        self.calc_result(dict(), recalc, force_caller='bc')
        return self.results['bc']


    def result_brh(self, recalc=False):
        self.calc_result(dict(), recalc)
        return self.results['brh']

    # ## calculations

    def calculate_ms(self):
        pass  # todo implement

    def calculate_mrs(self):
        pass  # todo implement

    def calculate_bc(self):
        '''

        :return:
        '''
        self.log.info('CALCULATING << Bc >> parameter from linear interpolation between points closest to m=0')

        def calc(direction):
            d = getattr(self, direction)
            idx = np.argmin(abs(d['mag']))  # index of closest to 0

            if d['mag'][idx] < 0:
                if d['mag'][idx + 1] < 0:
                    idx1 = idx
                    idx2 = idx - 1
                else:
                    idx1 = idx + 1
                    idx2 = idx
            else:
                if d['mag'][idx + 1] < 0:
                    idx1 = idx + 1
                    idx2 = idx
                else:
                    idx1 = idx - 1
                    idx2 = idx

            i = [idx1, idx2]
            d = d.filter_idx(i)

            dy = d['mag'][1] - d['mag'][0]
            dx = d['field'][1] - d['field'][0]
            m = dy / dx
            b = d['mag'][1] - d['field'][1] * m
            bc = abs(b / m)

            return bc

        df = calc('down_field')
        uf = calc('up_field')
        self.results['bc'] = np.mean([df, uf])
        self.results['sigma_bc'] = np.std([df, uf])

    def calculate_brh(self):
        pass  # todo implement


    def down_field_interp(self):
        from scipy import interpolate

        x = self.down_field['field']
        y = self.down_field['mag']

        if np.all(np.diff(x) > 0):
            f = interpolate.interp1d(x, y, kind='slinear')
        else:
            x = x[::-1]
            y = y[::-1]
            f = interpolate.interp1d(x, y, kind='slinear')

        x_new = np.arange(min(x), max(x), 0.01)
        y_new = f(x_new)
        return x_new, y_new

    def up_field_interp(self):
        from scipy import interpolate

        x = self.up_field['field']
        y = self.up_field['mag']

        if np.all(np.diff(x) > 0):
            f = interpolate.interp1d(x, y, kind='slinear')
        else:
            x = x[::-1]
            y = y[::-1]
            f = interpolate.interp1d(x, y, kind='slinear')

        x_new = np.arange(min(x), max(x), 0.01)
        y_new = f(x_new)
        return x_new, y_new

    # ## plotting functions
    def plt_hys(self):
        '''
        Rudimentary plotting function for quick check of data
        :return:
        '''

        std, = plt.plot(self.down_field['field'].v, self.down_field['mag'].v, '.-', zorder=1)
        plt.plot(self.up_field['field'].v, self.up_field['mag'].v, '.-',
                 color=std.get_color(),
                 zorder=1)

        # plotting interpolated data
        # plt.plot(self.down_field_interp()[0], self.down_field_interp()[1], '--',
        # color=std.get_color(),
        # zorder=1)
        # plt.plot(self.up_field_interp()[0], self.up_field_interp()[1], '--',
        # color=std.get_color(),
        # zorder=1)

        if not self.virgin is None:
            plt.plot(self.virgin['field'].v, self.virgin['mag'].v, color=std.get_color(), zorder=1)

        # ## plotting pc as crosses
        # plt.plot([-(self.bc + (self.bc_diff / 2)), self.bc - (self.bc_diff / 2)], [0, 0], 'xr')
        plt.axhline(0, color='#808080')
        plt.axvline(0, color='#808080')
        plt.grid()
        plt.title('Hysteresis %s' % (self.sample_obj.name))
        plt.xlabel('Field [%s]' % ('T'))  # todo replace with data unit
        plt.ylabel('Moment [%s]' % ('Am^2'))  # todo replace with data unit
        plt.show()

    def plt_hysteresis(self):
        '''
        helper calls plt_hys()
        :return:
        '''
        self.plt_hys()