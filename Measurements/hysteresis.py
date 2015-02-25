__author__ = 'volk'
import numpy as np
import matplotlib.pyplot as plt
import logging
import base
from RockPy.Structure.data import RockPyData
from scipy import stats
from scipy.optimize import curve_fit
from copy import deepcopy
import scipy as sp

class Hysteresis(base.Measurement):
    """

    .. testsetup:: *

       >>> from Structure.sample import Sample
       >>> vftb_file = TutoTutorials      >>> sample = Sample(name='vftb_test_sample')
       >>> M = sample.add_measurement(mtype='hysteresis', mfile=vftb_file, machine='vftb')


    """

    # logger = logging.getLogger('RockPy.MEASUREMENT.hysteresis')

    def __init__(self, sample_obj,
                 mtype, mfile, machine,
                 **options):

        self._data = {'up_field': None,
                      'down_field': None,
                      'virgin': None,
                      'msi': None,
                      'all': None}

        # TODO: check if the above makes sense. super resets self._data ????

        super(Hysteresis, self).__init__(sample_obj, mtype, mfile, machine, **options)

        self._grid_data = {}
        self._corrected_data = {}

        self.paramag_correction = None

    @property
    def grid_data(self):
        if not self._grid_data:
            self.data_gridding()
        return self._grid_data

    @property
    def corrected_data(self):
        if hasattr(self, '_corrected_data'):
            if not self._corrected_data:
                return deepcopy(self.data)
            else:
                return self._corrected_data
        else:
            return deepcopy(self.data)

    # ## formatting functions
    def format_vftb(self):
        data = self.machine_data.out_hysteresis()
        header = self.machine_data.header
        self._data['all'] = RockPyData(column_names=header, data=data[0])
        dfield = np.diff(self._data['all']['field'].v)
        idx = [i for i in range(len(dfield)) if dfield[i] <= 0]
        idx += [max(idx) + 1]
        virgin_idx = range(0, idx[0])
        down_field_idx = idx
        up_field_idx = range(idx[-1], len(dfield) + 1)

        self._data['virgin'] = self._data['all'].filter_idx(virgin_idx)
        self._data['down_field'] = self._data['all'].filter_idx(down_field_idx)
        self._data['up_field'] = self._data['all'].filter_idx(up_field_idx)

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
            self._data['virgin'] = RockPyData(column_names=header, data=self.machine_data.out_hysteresis()[0])
            self._data['down_field'] = RockPyData(column_names=header, data=self.machine_data.out_hysteresis()[1])
            self._data['up_field'] = RockPyData(column_names=header, data=self.machine_data.out_hysteresis()[2])

        if len(segments['segment number'].v) == 2:
            self._data['virgin'] = None
            self._data['down_field'] = RockPyData(column_names=header, data=self.machine_data.out_hysteresis()[0])
            self._data['up_field'] = RockPyData(column_names=header, data=self.machine_data.out_hysteresis()[1])

        if len(segments['segment number'].v) == 1:
            self._data['virgin'] = RockPyData(column_names=header, data=self.machine_data.out_hysteresis()[0])
            self._data['down_field'] = None
            self._data['up_field'] = None

        try:
            self.data['virgin'].rename_column('moment', 'mag')
        except AttributeError:
            pass

        try:
            self.data['up_field'].rename_column('moment', 'mag')
        except AttributeError:
            pass

        try:
            self.data['down_field'].rename_column('moment', 'mag')
        except AttributeError:
            pass

    def format_microsense(self):
        data = self.machine_data.out_hys()
        header = self.machine_data.header

        self._data['all'] = RockPyData(column_names=header, data=data)
        dfield = np.diff(self._data['all']['raw_applied_field_for_plot_'])
        down_field_idx = [i for i in range(len(dfield)) if dfield[i] < 0]
        up_field_idx = [i for i in range(len(dfield)) if dfield[i] > 0]

        self._data['down_field'] = self.raw_data.filter_idx(down_field_idx)
        self._data['down_field'].define_alias('field', 'raw_applied_field_for_plot_')
        self._data['down_field'].define_alias('mag', 'raw_signal_mx')
        self._data['down_field']['field'] *= 0.1 * 1e-3  # conversion Oe to Tesla

        self._data['up_field'] = self.raw_data.filter_idx(up_field_idx)
        self._data['up_field'].define_alias('field', 'raw_applied_field_for_plot_')
        self._data['up_field'].define_alias('mag', 'raw_signal_mx')
        self._data['up_field']['field'] *= 0.1 * 1e-3  # conversion Oe to Tesla

    # ## calculations

    def irrev(self, **options):
        irrev = self.data['down_field']
        irrev -= self.data['up_field']
        return irrev

    # ## results

    def result_generic(self, parameter='standard', recalc=False, **options):
        '''
        Generic for for result implementation. Every calculation of result should be in the self.results data structure
        before calculation.
        It should then be tested if a value for it exists, and if not it should be created by calling
        _calculate_result_(result_name).

        '''
        self.calc_result(parameter, recalc)
        return self.results['generic']

    def result_ms(self, method='auto', recalc=False, **parameter):
        """
        calculates the Ms value with a linear fit
        :param recalc:
        :param parameter:
            - from_field : field value in % of max. field above which slope seems linear
        :return:
        """
        self.calc_result(parameter, recalc, force_method=method)
        return self.results['ms']

    def result_sigma_ms(self, recalc=False, **parameter):
        self.calc_result(parameter, recalc, force_method='ms')
        return self.results['sigma_ms']

    def result_mrs(self, recalc=False, **parameter):
        self.calc_result(dict(), recalc)
        return self.results['mrs']

    def result_sigma_mrs(self, recalc=False, **parameter):
        self.calc_result(dict(), recalc, force_method='mrs')
        return self.results['sigma_mrs']

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

    def result_sigma_bc(self, recalc=False, **options):
        self.calc_result(dict(), recalc, force_method='bc')
        return self.results['sigma_bc']

    def result_brh(self, recalc=False, **options):
        self.calc_result(dict(), recalc)
        return self.results['brh']

    def result_paramag_slope(self, from_field=80, recalc=False, **options):
        parameter = {'from_field': from_field}
        self.calc_result(parameter, recalc, force_method='ms')
        return self.results['paramag_slope']

    def result_E_delta_t(self, recalc=False, **options):
        self.calc_result(dict(), recalc)
        return self.results['E_delta_t']

    def result_E_hys(self, recalc=False, **options):
        self.calc_result(dict(), recalc)
        return self.results['E_hys']

    # def result_E_delta_t(self, recalc=False, **options):
    #     self.calc_result(dict(), recalc)
    #     return self.results['E_hys']

    # ## calculations

    def calculate_ms(self, **parameter):
        """
        Calculates the value for Ms
        :param parameter: from_field: from % of this value a linear interpolation will be calculated for all branches (+ & -)
        :return:
        """
        from_field = parameter.get('from_field', 75) / 100.0
        df_fields = self.data['down_field']['field'].v / max(self.data['down_field']['field'].v)
        uf_fields = self.data['up_field']['field'].v / max(self.data['up_field']['field'].v)

        # get the indices of the fields larger that from_field
        df_plus = [i for i, v in enumerate(df_fields) if v >= from_field]
        df_minus = [i for i, v in enumerate(df_fields) if v <= -from_field]
        uf_plus = [i for i, v in enumerate(uf_fields) if v >= from_field]
        uf_minus = [i for i, v in enumerate(uf_fields) if v <= -from_field]

        dfp = self.data['down_field'].filter_idx(df_plus).lin_regress(column_name_x='field', column_name_y='mag')
        dfm = self.data['down_field'].filter_idx(df_minus).lin_regress(column_name_x='field', column_name_y='mag')
        ufp = self.data['down_field'].filter_idx(uf_plus).lin_regress(column_name_x='field', column_name_y='mag')
        ufm = self.data['down_field'].filter_idx(uf_minus).lin_regress(column_name_x='field', column_name_y='mag')
        self.paramag_correction = np.array([dfp, dfm, ufp, ufm])

        ms_all = [abs(dfp[2]), abs(dfm[2]), abs(ufp[2]), abs(ufm[2])]
        slope_all = [abs(dfp[0]), abs(dfm[0]), abs(ufp[0]), abs(ufm[0])]

        self.results['ms'] = np.median(ms_all)
        self.results['sigma_ms'] = np.std(ms_all)
        self.results['paramag_slope'] = np.median(slope_all)

        self.calculation_parameter['ms'] = parameter
        self.calculation_parameter['paramag_slope'] = parameter

    def calculate_mrs(self, **parameter):

        def calc(direction):
            d = getattr(self, direction)
            data = d['field'].v
            idx = np.argmin(abs(data))  # index of closest to 0
            if data[idx] < 0:
                if data[idx + 1] < 0:
                    idx1 = idx
                    idx2 = idx - 1
                else:
                    idx1 = idx + 1
                    idx2 = idx
            else:
                if data[idx + 1] < 0:
                    idx1 = idx + 1
                    idx2 = idx
                else:
                    idx1 = idx - 1
                    idx2 = idx

            i = [idx1, idx2]
            d = d.filter_idx(i)

            x = d['field'].v
            y = d['mag'].v
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            return abs(intercept)

        df = calc('down_field')
        uf = calc('up_field')
        self.results['mrs'] = np.mean([df, uf])
        self.results['sigma_mrs'] = np.std([df, uf])

    def calculate_bc(self, **parameter):
        '''

        :return:
        '''
        # Hysteresis.logger.info('CALCULATING << Bc >> parameter from linear interpolation between points closest to m=0')

        def calc(direction):
            d = getattr(self, direction)
            data = d['mag'].v
            idx = np.argmin(abs(data))  # index of closest to 0
            if data[idx] < 0:
                if data[idx + 1] < 0:
                    idx1 = idx
                    idx2 = idx - 1
                else:
                    idx1 = idx + 1
                    idx2 = idx
            else:
                if data[idx + 1] < 0:
                    idx1 = idx + 1
                    idx2 = idx
                else:
                    idx1 = idx - 1
                    idx2 = idx

            i = [idx1, idx2]
            d = d.filter_idx(i)

            dy = d['mag'].v[1] - d['mag'].v[0]
            dx = d['field'].v[1] - d['field'].v[0]
            m = dy / dx
            b = d['mag'].v[1] - d['field'].v[1] * m
            bc = abs(b / m)

            return bc

        df = calc('down_field')
        uf = calc('up_field')
        self.results['bc'] = np.mean([df, uf])
        self.results['sigma_bc'] = np.std([df, uf])

    def calculate_brh(self, **parameter):
        pass  # todo implement

    def check_if_msi(self):


    def calculate_E_delta_t(self, **parameter):
        '''
        Method calculates the :math:`E^{\Delta}_t` value for the hysteresis.
        It uses scipy.integrate.simps for calculation of the area under the down_field branch for positive fields and
        later subtracts the area under the Msi curve.

        The energy is:

        .. math::

           E^{\delta}_t = 2 \int_0^{B_{max}} (M^+(B) - M_{si}(B)) dB

        '''
        if self.msi is not None:
            df_positive = np.array([i for i in self.down_field if i[0] > 0])[::-1]
            df_energy = scipy.integrate.simps(df_positive[:, 1], x=df_positive[:, 0])
            virgin_energy = scipy.integrate.simps(self.msi[:, 1], x=self.msi[:, 0])
            out = 2 * (df_energy - virgin_energy)
            return out

        else:
            self.log.error('UNABLE\t to find Msi branch')
            return 0.0

        if self.data['virgin'] is not None:
            df_positive = np.array([i for i in self.down_field if i[0] > 0])[::-1]
            df_energy = sp.integrate.simps(df_positive[:, 1], x=df_positive[:, 0])
            virgin_energy = sp.integrate.simps(self.msi[:, 1], x=self.msi[:, 0])
            out = 2 * (df_energy - virgin_energy)
            return out

        else:
            self.log.error('UNABLE\t to find Msi branch')
            return 0.0


    def simple_paramag_cor(self, **parameter):

        if self.paramag_correction is None:
            self.calculate_ms(**parameter)

        slope = np.mean(self.paramag_correction[:, 0])
        intercept = np.mean(self.paramag_correction[:, 2])

        for dtype in self.data:
            if self.data[dtype]:
                d = self.data[dtype].v
                d[:, 1] -= d[:, 0] * slope


    def data_gridding(self, **parameter):
        """
        .. math::

           B_{\text{grid}}(i) = \frac{|i|}{i} \frac{B_m}{\lambda} \left[(\lambda + 1 )^{|i|/n} - 1 \right]

        :return:
        """

        grid = self.get_grid(**parameter)
        order = parameter.get('order', 'second')
        # interpolate the magnetization values M_int(Bgrid(i)) for i = -n+1 .. n-1
        # by fitting M_{measured}(B_{experimental}) individually in all intervals [Bgrid(i-1), Bgrid(i+1)]
        # with first or second order polinomials

        def first(x, a, b):
            return a + b * x

        def second(x, a, b, c):
            return a + b * x + c * x ** 2

        for dtype in ['down_field', 'up_field']:
            interp_data = RockPyData(column_names=['field', 'mag'])
            d = self.data[dtype]
            for i in range(1, len(grid) - 1):
                idx = [j for j, v in enumerate(d['field'].v) if grid[i - 1] <= v <= grid[i + 1]]
                if len(idx) > 0:
                    data = deepcopy(d.filter_idx(idx))
                    try:
                        if order == 'first':
                            popt, pcov = curve_fit(first, data['field'].v, data['mag'].v)
                            mag = first(grid[i], *popt)
                            interp_data = interp_data.append_rows(data=[grid[i], mag])
                        if order == 'second':
                            popt, pcov = curve_fit(second, data['field'].v, data['mag'].v)
                            mag = second(grid[i], *popt)
                            interp_data = interp_data.append_rows(data=[grid[i], mag])
                    except TypeError:
                        self.logger.error('Length of data for interpolation < 2. mag = mean(data)')
                        self.logger.error(
                            'consider reducing number of points for interpolation or lower tuning parameter')
                        mag = np.mean(data['mag'].v)
            self._grid_data.update({dtype: interp_data})

    def get_grid(self, **parameter):
        if not hasattr(self, '_grid_data'):
            self._grid_data = {}
        n = parameter.get('n', 20)
        tuning = parameter.get('tuning', 8)

        # getting the Bmax that is common for both branches
        bmax = min([max(self.data['down_field']['field'].v), max(self.data['up_field']['field'].v)])
        bmin = min([min(self.data['down_field']['field'].v), min(self.data['up_field']['field'].v)])
        bm = min([abs(bmax), abs(bmin)])
        grid = []

        # calculating the grid
        for i in xrange(-n - 1, n + 2):
            if i != 0:
                boi = (abs(i) / i) * (bm / tuning) * ((tuning + 1) ** (abs(i) / float(n)) - 1.)
            else:  # catch exception for i = 0
                boi = 0
            grid.append(boi)

        return grid

    def correct_center(self, data='grid_data'):
        uf_rotate = self.rotate_branch('up_field', data)

        # copy data and average with opposite rotated branch
        df_corrected = getattr(self, data)['down_field']
        shift = (max(getattr(self, data)['down_field']['mag'].v) - min(getattr(self, data)['up_field']['mag'].v) + \
                 min(getattr(self, data)['down_field']['mag'].v) - max(getattr(self, data)['up_field']['mag'].v)) / 4

        df_corrected['mag'] = (df_corrected['mag'].v + uf_rotate['mag'].v) / 2 - shift
        uf_corrected = deepcopy(df_corrected)
        uf_corrected['field'] = -uf_corrected['field'].v
        uf_corrected['mag'] = -uf_corrected['mag'].v

        self._corrected_data.update({'down_field': df_corrected})
        self._corrected_data.update({'up_field': uf_corrected})

    def rotate_branch(self, branch, data='data'):
        """
        rotates a branch by 180 degrees, by multiplying the field and mag values by -1
        :param data: str
                     e.g. data, grid_data, corrected_data
        :param branch: str
                       up-field or down-field
        :return:
        """
        data = deepcopy(getattr(self, data)[branch])
        data['field'] = -data['field'].v[::-1]
        data['mag'] = -data['mag'].v[::-1]
        return data

    def correct_slope(self):
        """
        The magnetization curve in this region can be expressed as
        .. math::

           M(B) = Ms + \Chi B + \alpha B^{\beta}

        where :math:`\Chi` is the susceptibility of all dia- and paramagnetic components
        (including the para-effect) and the last term represents an individual approach to saturation law.
        :return:
        """
        # calculate approach to saturation ( assuming beta = -1 ) for upfield/downfield branches with pos / negative field
        # assuming 80 % saturation
        a2s_data = map(self.calc_approach2sat, ['down_field'])#, 'up_field'])
        a2s_data = np.array(a2s_data)
        a2s_data = a2s_data.reshape(1, 2, 3)[0]

        simple = self.result_paramag_slope()
        # print a2s_data

        popt = np.mean(a2s_data, axis=0)
        ms = np.mean(abs(a2s_data[:, 0]))
        ms_std = np.std(abs(a2s_data[:, 0]))
        chi = np.mean(abs(a2s_data[:, 1])) * np.sign(simple)
        chi_std = np.std(abs(a2s_data[:, 1]))

        alpha = np.mean(abs(a2s_data[:, 2])) * np.sign(a2s_data[0, 2])
        alpha_std = np.std(abs(a2s_data[:, 2]))

        for dtype in self.corrected_data:
            self.corrected_data[dtype]['mag'] = self.corrected_data[dtype]['mag'].v - \
                                                self.corrected_data[dtype]['field'].v * chi
        print(a2s_data), self.result_paramag_slope()
        return ms, chi, alpha

    def calc_approach2sat(self, branch):
        def approach2sat_func(x, ms, chi, alpha, beta=-1):
            """
            General approach to saturation function
            :param x: field
            :param ms: saturation magnetization
            :param chi: susceptibility
            :param alpha:
            :param beta:
            :return:
            """
            return ms + chi * x + alpha * x ** -1  # beta

        #### POSITIVE BRANCH
        # get idx of downfield branch where b > 0
        idx = [i for i, v in enumerate(self.corrected_data[branch]['field'].v) if
               v >= 0.7 * max(self.corrected_data[branch]['field'].v)]
        df_pos = deepcopy(self.corrected_data[branch].filter_idx(idx))  # down field with positive field data

        popt_pos, pcov_pos = curve_fit(approach2sat_func, df_pos['field'].v, df_pos['mag'].v,
                                       p0=[max(df_pos['mag'].v), 0, 0])

        idx = [i for i, v in enumerate(self.corrected_data[branch]['field'].v) if
               v <= 0.4 * min(self.corrected_data[branch]['field'].v)]
        df_neg = deepcopy(self.corrected_data[branch].filter_idx(idx))  # down field with positive field data

        popt_neg, pcov_neg = curve_fit(approach2sat_func, df_neg['field'].v[::-1], df_neg['mag'].v[::-1],
                                       p0=[max(df_neg['mag'].v), 1e-7, 0])
        return popt_pos, popt_neg


    def correct_holder(self):
        raise NotImplementedError

    # ## plotting functions
    def plt_hys(self, noshow=False):
        '''
        Rudimentary plotting function for quick check of data
        :return:
        '''

        std, = plt.plot(self.data['down_field']['field'].v, self.data['down_field']['mag'].v, '.-', zorder=1)
        plt.plot(self.data['up_field']['field'].v, self.data['up_field']['mag'].v, '.-',
                 color=std.get_color(),
                 zorder=1)
        plt.plot(0, self.results['mrs'].v[0], 'x')

        if not self.paramag_correction is None:
            slopes = self.paramag_correction[:, 0]
            intercepts = self.paramag_correction[:, 2]
            # downfield paramag_correction_line
            xdf = np.array([0, max(self.data['down_field']['field'].v)])  # get x
            xuf = np.array([min(self.data['down_field']['field'].v), 0])  # get x
            ydf = xdf * np.mean(slopes) + np.mean(np.fabs(intercepts))
            yuf = xuf * np.mean(slopes) - np.mean(np.fabs(intercepts))

            plt.plot(xdf, ydf, 'g--', alpha=0.5)
            plt.plot(xuf, yuf, 'g--', alpha=0.5)

        if not self.data['virgin'] is None:
            plt.plot(self.data['virgin']['field'].v, self.data['virgin']['mag'].v, color=std.get_color(), zorder=1)

        # ## plotting pc as crosses
        # plt.plot([-(self.bc + (self.bc_diff / 2)), self.bc - (self.bc_diff / 2)], [0, 0], 'xr')
        plt.axhline(0, color='#808080')
        plt.axvline(0, color='#808080')
        plt.grid()
        plt.title('Hysteresis %s' % (self.sample_obj.name))
        plt.xlabel('Field [%s]' % ('T'))  # todo replace with data unit
        plt.ylabel('Moment [%s]' % ('Am2'))  # todo replace with data unit
        if not noshow:
            plt.show()

    def plt_hysteresis(self):
        '''
        helper calls plt_hys()
        :return:
        '''
        self.plt_hys()

    def export_vftb(self, folder=None, filename=None):
        import os
