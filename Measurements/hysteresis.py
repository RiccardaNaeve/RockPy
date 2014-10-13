__author__ = 'volk'
import numpy as np
import matplotlib.pyplot as plt

import base
from Structure.rockpydata import RockPyData


class Hysteresis(base.Measurement):
    def __init__(self, sample_obj,
                 mtype, mfile, machine,
                 **options):
        super(Hysteresis, self).__init__(sample_obj, mtype, mfile, machine)


    # ## formatting functions
    def format_vftb(self):
        data = self.machine_data.out_hys()
        header = self.machine_data.header
        self.induced = RockPyData(column_names=header, data=data[0])
        dfield = np.diff(self.induced['field'])

        idx = [i for i in range(len(dfield)) if dfield[i] < 0]
        virgin_idx = range(0, idx[0])
        down_field_idx = idx
        up_field_idx = range(idx[-1], len(dfield) + 1)

        self.virgin = self.induced.filter_idx(virgin_idx)
        self.down_field = self.induced.filter_idx(down_field_idx)
        self.up_field = self.induced.filter_idx(up_field_idx)

    def format_vsm(self):
        pass

    def format_microsense(self):
        data = self.machine_data.out_hys()
        header = self.machine_data.header

        self.raw_data = RockPyData(column_names=header, data=data)
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

    # ## parameters
    @property
    def ms(self):
        '''
        returns the ms value if already calculated,
        calls calculate_ms if not yet calculated
        :return:
        '''
        if self.results['ms'] is None:
            self.calculate_ms()
            # return self.results['ms'][0]

    @property
    def mrs(self):
        '''
        returns the mrs value if already calculated,
        calls calculate_mrs if not yet calculated
        :return:
        '''
        if self.results['mrs'] is None:
            self.calculate_mrs()
            # return self.results['mrs'][0]

    @property
    def bc(self):
        '''
        returns the bc value if already calculated,
        calls calculate_bc if not yet calculated
        :return:
        '''
        if self.results['bc'] is None:
            self.calculate_bc()
        return np.mean(self.results['bc'])

    @property
    def bc_diff(self):
        '''
        returns the difference between down_field and up_field calculation of bc
        :return: float
        '''
        if self.results['bc'] is None:
            self.calculate_bc()
        return self.results['bc'][0] - self.results['bc'][1]

    @property
    def brh(self):
        '''
        returns the brh value if already calculated,
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

    def result_generic(self, parameters='standard'):
        '''
        Generic for for result implementation. Every calculation of result should be in the self.results data structure
        before calculation.
        It should then be tested if a value for it exists, and if not it should be created by calling
        _calculate_result_(result_name).

        '''
        if self.results['generic'] is None:
            self.calculate_generic(parameters)
        return self.results['generic']

    def result_ms(self):
        if self.results['ms'] is None:
            self.calculate_generic()
        return self.results['ms']

    def result_mrs(self):
        if self.results['mrs'] is None:
            self.calculate_generic()
        return self.results['mrs']

    def result_bc(self):
        if self.results['bc'] is None:
            self.calculate_generic()
        return self.results['bc']

    def result_brh(self):
        if self.results['brh'] is None:
            self.calculate_generic()
        return self.results['brh']

    # ## calculations

    def calculate_ms(self):
        raise NotImplemented

    def calculate_mrs(self):
        raise NotImplemented

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
        self.results['bc'] = [df, uf]

    def calculate_brh(self):
        raise NotImplemented

    def calculate_generic(self, parameters):
        '''
        actual calculation of the result

        :return:
        '''
        self.results['generic'] = 0

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

        std, = plt.plot(self.down_field['field'], self.down_field['mag'], '.-', zorder=1)
        plt.plot(self.up_field['field'], self.up_field['mag'], '.-',
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
            plt.plot(self.virgin['field'], self.virgin['mag'], color=std.get_color(), zorder=1)

        # ## plotting pc as crosses
        plt.plot([-(self.bc + (self.bc_diff / 2)), self.bc - (self.bc_diff / 2)], [0, 0], 'xr')
        plt.axhline(0, color='#808080')
        plt.axvline(0, color='#808080')
        plt.grid()
        plt.title('Hysteresis %s' % (self.sample_obj.name))
        plt.xlabel('Field [%s]' % ('T'))  # todo replace with data unit
        plt.ylabel('Moment [%s]' % ('Am^2'))  #todo replace with data unit
        plt.show()

    def plt_hysteresis(self):
        '''
        helper calls plt_hys()
        :return:
        '''
        self.plt_hys()