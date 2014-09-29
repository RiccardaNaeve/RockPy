from Structure.rockpydata import rockpydata

__author__ = 'volk'
import base
import numpy as np
import Structure.data
import matplotlib.pyplot as plt


class Hysteresis(base.Measurement):
    def __init__(self, sample_obj,
                 mtype, mfile, machine,
                 **options):
        super(Hysteresis, self).__init__(sample_obj, mtype, mfile, machine)

        data_formatting = {'vftb': self.format_vftb,
                           'vsm': self.format_vsm}

        # ## initialize
        self.virgin = None
        self.msi = None
        self.up_field = None
        self.down_field = None

        data_formatting[self.machine]()

        # ## calculation initialization
        self.results = rockpydata(column_names=['ms', 'mrs', 'bc', 'brh'])

    ### formatting functions
    def format_vftb(self):
        self.data = rockpydata(column_names=('field', 'moment', 'temperature', 'time',
                                             'std_dev', 'susceptibility'), data=self.raw_data)
        dfield = np.diff(self.data['field'])

        idx = [i for i in range(len(dfield)) if dfield[i] < 0]
        virgin_idx = range(0, idx[0])
        down_field_idx = idx
        up_field_idx = range(idx[-1], len(dfield) + 1)

        self.virgin = self.data.filter_idx(virgin_idx)
        self.down_field = self.data.filter_idx(down_field_idx)
        self.up_field = self.data.filter_idx(up_field_idx)

    def format_vsm(self):
        print self.raw_data.out

    # ## parameters
    @property
    def ms(self):
        '''
        returns the ms value if already calculated,
        calls calculate_ms if not yet calculated
        :return:
        '''
        if self.results['ms'] is None or self.results['ms'] == 0:
            self.calculate_ms()
            # return self.results['ms'][0]

    @property
    def mrs(self):
        '''
        returns the mrs value if already calculated,
        calls calculate_mrs if not yet calculated
        :return:
        '''
        if self.results['mrs'] is None or self.results['mrs'] == 0:
            self.calculate_mrs()
            # return self.results['mrs'][0]

    @property
    def bc(self):
        '''
        returns the bc value if already calculated,
        calls calculate_bc if not yet calculated
        :return:
        '''
        if self.results['bc'] is None or self.results['bc'] == 0:
            self.calculate_bc()
        return self.results['bc'][0]

    @property
    def brh(self):
        '''
        returns the brh value if already calculated,
        calls calculate_brh if not yet calculated
        :return:
        '''
        if self.results['brh'] is None or self.results['brh'] == 0:
            self.calculate_brh()
            # return self.results['brh'][0]

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
            idx = np.argmin(abs(d['moment']))  # index of closest to 0

            if d['moment'][idx] < 0:
                if d['moment'][idx + 1] < 0:
                    idx1 = idx
                    idx2 = idx - 1
                else:
                    idx1 = idx + 1
                    idx2 = idx
            else:
                if d['moment'][idx + 1] < 0:
                    idx1 = idx + 1
                    idx2 = idx
                else:
                    idx1 = idx - 1
                    idx2 = idx

            i = [idx1, idx2]
            d = d.filter_idx(i)

            dy = d['moment'][1] - d['moment'][0]
            dx = d['field'][1] - d['field'][0]
            m = dy / dx
            b = d['moment'][1] - d['field'][1] * m
            bc = abs(b / m)

            return bc

        df = calc('down_field')
        uf = calc('up_field')
        self.results['bc'] = np.mean([df, uf])

    def calculate_brh(self):
        raise NotImplemented


    ### plotting functions
    def plt_hys(self):
        '''
        Rudimentary plotting function for quick check of data
        :return:
        '''

        std, = plt.plot(self.down_field['field'], self.down_field['moment'], '.-', zorder=1)
        plt.plot(self.up_field['field'], self.up_field['moment'], '.-', color=std.get_color(), zorder=1)

        if not self.virgin is None:
            plt.plot(self.virgin['field'], self.virgin['moment'], color=std.get_color(), zorder=1)
        plt.plot([-self.bc, self.bc], [0,0], 'xr')
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