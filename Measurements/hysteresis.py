__author__ = 'volk'
import inspect
import numpy as np
import matplotlib.pyplot as plt
import logging
import base
from RockPy.Structure.data import RockPyData
from scipy import stats
from scipy.optimize import curve_fit
from copy import deepcopy
import scipy as sp
from math import tanh, cosh

from pprint import pprint

class Hysteresis(base.Measurement):
    """

    .. testsetup:: *

       >>> import RockPy
       >>> vftb_file = RockPy.test_data_path + '/' +  'MUCVFTB_test.hys'
       >>> sample = RockPy.Sample(name='vftb_test_sample')
       >>> M = sample.add_measurement(mtype='hysteresis', mfile=vftb_file, machine='vftb')


    """

    @classmethod
    def simulate(cls, sample_obj, m_idx=0, color=None,
                 ms=250., mrs_ms=0.5, bc=0.2, hf_sus=1., bmax=1.8, b_sat=1, steps=100,
                 noise=None):
        """
        Simulation of hysteresis loop using sngle tanh and sech functions.

        Parameters:
        -----------
        m_idx: int
            index of measurement
        ms: float

        mrs_ms: float
            :math:`M_{rs}/M_{s}` ratio
        bc:
        hf_sus:
        bmax:
        b_sat: float
            Field at which 99% of the moment is saturated
        steps:
        sample_obj:
        color:
        parameter:

        Returns:
        --------

        Note:
        ----
        Increasing the Mrs/Ms ratio to more then 0.5 results in weird looking hysteresis loops
        """

        data = {'up_field': None,
                'down_field': None,
                'virgin': None}

        fields = cls.get_grid(bmax=bmax, n=steps)

        # uf = float(ms) * np.array([tanh(3*(i-bc)/b_sat) for i in fields]) + hf_sus * fields
        # df = float(ms) * np.array([tanh(3*(i+bc)/b_sat) for i in fields]) + hf_sus * fields
        rev_mag = float(ms) * np.array([tanh(2 * i / b_sat) for i in fields]) + hf_sus * fields
        # irrev_mag = float(ms) * mrs_ms * np.array([cosh(i * (5.5 / b_sat)) ** -1 for i in fields])
        irrev_mag = float(ms) * mrs_ms * np.array([cosh(3.5 * i / b_sat) ** -1 for i in fields])

        data['down_field'] = RockPyData(column_names=['field', 'mag'], data=np.c_[fields, rev_mag + irrev_mag])
        data['up_field'] = RockPyData(column_names=['field', 'mag'], data=np.c_[fields, rev_mag - irrev_mag][::-1])
        #
        # plt.plot(fields, rev_mag)
        # plt.plot(fields, irrev_mag)
        # plt.plot(fields, rev_mag + irrev_mag)
        # plt.plot(fields, rev_mag - irrev_mag)
        # plt.show()
        return cls(sample_obj, 'hysteresis', mfile=None, mdata=data, machine='simulation', color=color)

    @classmethod
    def get_grid(cls, bmax=1, n=30, tuning=5):
        grid = []
        # calculating the grid
        for i in xrange(-n, n + 1):
            if i != 0:
                boi = (abs(i) / i) * (bmax / tuning) * ((tuning + 1) ** (abs(i) / float(n)) - 1.)
            else:  # catch exception for i = 0
                boi = 0
            grid.append(boi)
        return np.array(grid)


    def __init__(self, sample_obj,
                 mtype, mfile, machine,
                 **options):

        super(Hysteresis, self).__init__(sample_obj, mtype, mfile, machine, **options)

        self.paramag_correction = None

    @property
    def correction(self):
        return self.set_get_attr('_correction', value=list())

    @property
    def grid_data(self):
        return self.set_get_attr('_grid_data', value=self.data_gridding())

    @property
    def corrected_data(self):
        return self.set_get_attr('_corrected_data', deepcopy(self.data))

    # ## formatting functions
    def format_vftb(self):
        """
        format function that takes vftb.machine_data and transforms it into HYsteresis.RockPydata objects.
        :needed:
           virgin: virgin branch
           down_field: down field branch
           up_field: up field branch
        """
        #get data
        data = self.machine_data.out_hysteresis()
        # get header
        header = self.machine_data.header
        self._data['all'] = RockPyData(column_names=header, data=data[0]) #todo maybe not as attribute
        dfield = np.diff(self._data['all']['field'].v)

        #get index where change of field value is negative
        idx = [i for i in range(len(dfield)) if dfield[i] <= 0] # todo implement signchanges in RockPy.data
        idx += [max(idx) + 1] # add 1 point so down and up field branches start at same values
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

    """ RESULTS """

    def result_ms(self, method='auto', recalc=False, **parameter):
        """
        calculates the Ms value with a linear fit
        :param recalc:
        :param parameter:
            - from_field : field value in % of max. field above which slope seems linear
        :return:

        :methods auto: simple
        :methods simple: Calculates a simple linear regression of the high field magnetization. The y-intercept
                         is Ms.
        : method approach_to_sat: Calculates a simple approach to saturation :cite:`Dobeneck1996a`

        """

        if method == 'auto':
            method = 'simple'

        calc_method = '_'.join(method)
        self.calc_result(parameter, recalc, force_method=calc_method)
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

    """ CALCULATIONS """

    ## MS
    def calculate_ms(self, method='simple', **parameter):
        """
        Wrapper so one can call calculate_ms on its own, giving the method as an argument
        :param method:
        :param parameter:
        :return:
        """
        method = 'calculate_ms_' + method
        implemented = [i for i in dir(self) if i.startswith('calculate_ms_')]
        if method in implemented:
            getattr(self, method)(**parameter)

    def calculate_ms_simple(self, from_field=75, **parameter):
        """
        Calculates the value for Ms
        :param parameter: from_field: from % of this value a linear interpolation will be calculated for all branches (+ & -)
        :return:
        """
        from_field /= 100.0

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
        self.calculation_parameter['method'] = 'simple'

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
                    idx1, idx2 = (idx, idx - 1)
                else:
                    idx1, idx2 = (idx + 1, idx)
            else:
                if data[idx + 1] < 0:
                    idx1, idx2 = (idx + 1, idx)
                else:
                    idx1, idx2 = (idx - 1, idx)

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

    def calculate_E_delta_t(self, **parameter):
        '''
        Method calculates the :math:`E^{\Delta}_t` value for the hysteresis.
        It uses scipy.integrate.simps for calculation of the area under the down_field branch for positive fields and
        later subtracts the area under the Msi curve.

        The energy is:

        .. math::

           E^{\delta}_t = 2 \int_0^{B_{max}} (M^+(B) - M_{si}(B)) dB

        '''

        raise NotImplementedError


    """ CORRECTIONS """

    def check_if_msi(self):
        raise NotImplementedError


    def simple_paramag_cor(self, **parameter):

        # if not self.paramag_correction:
        #     self.calculate_ms(**parameter)

        slope = np.mean(self.paramag_correction[:, 0])
        intercept = np.mean(self.paramag_correction[:, 2])

        for dtype in self.data:
            if self.data[dtype]:
                d = self.data[dtype].v
                d[:, 1] -= d[:, 0] * slope


    def data_gridding(self, method='second', **parameter):
        """
        Data griding after :cite:`Dobeneck1996a`. Generates an interpolated hysteresis loop with
        :math:`M^{\pm}_{sam}(B^{\pm}_{exp})` at mathematically defined (grid) field values, identical for upper
         and lower branch.

        .. math::

           B_{\text{grid}}(i) = \frac{|i|}{i} \frac{B_m}{\lambda} \left[(\lambda + 1 )^{|i|/n} - 1 \right]


        Parameters
        ----------
        method : str
            method with wich the data is fitted between grid points.
            first:
                data is fitted using a first order polinomial :math:`M(B) = a_1 + a2*B`
            second:
                data is fitted using a second order polinomial :math:`M(B) = a_1 + a2*B +a3*B^2`

        parameter: dict
            Keyword arguments passed through

        See Also
        --------
        get_grid
        """

        bmax = min([max(self.data['down_field']['field'].v), max(self.data['up_field']['field'].v)])
        bmin = min([min(self.data['down_field']['field'].v), min(self.data['up_field']['field'].v)])
        bm = min([abs(bmax), abs(bmin)])

        grid = Hysteresis.get_grid(bmax=bm, **parameter)
        # interpolate the magnetization values M_int(Bgrid(i)) for i = -n+1 .. n-1
        # by fitting M_{measured}(B_{experimental}) individually in all intervals [Bgrid(i-1), Bgrid(i+1)]
        # with first or second order polinomials

        def first(x, a, b):
            """
            order one polinomial for fitting
            """
            return a + b * x

        def second(x, a, b, c):
            """
            second order polinomial
            """
            return a + b * x + c * x ** 2

        for dtype in ['down_field', 'up_field', 'virgin']:
            interp_data = RockPyData(column_names=['field', 'mag'])
            d = self.data[dtype]
            for i in range(1, len(grid) - 1):
                idx = [j for j, v in enumerate(d['field'].v) if grid[i - 1] <= v <= grid[i + 1]]
                if len(idx) > 0:
                    data = deepcopy(d.filter_idx(idx))
                    try:
                        if method == 'first':
                            popt, pcov = curve_fit(first, data['field'].v, data['mag'].v)
                            mag = first(grid[i], *popt)
                            interp_data = interp_data.append_rows(data=[grid[i], mag])
                        if method == 'second':
                            popt, pcov = curve_fit(second, data['field'].v, data['mag'].v)
                            mag = second(grid[i], *popt)
                            interp_data = interp_data.append_rows(data=[grid[i], mag])
                    except TypeError:
                        self.logger.error('Length of data for interpolation < 2. mag = mean(data)')
                        self.logger.error(
                            'consider reducing number of points for interpolation or lower tuning parameter')
                        mag = np.mean(data['mag'].v)
            self._grid_data.update({dtype: interp_data})


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

    def correct_paramag(self, method='simple', **parameter):
        "corrects data according to specified method"

        # print self.corrected_data['up_field']['mag'].v[0]
        # definition of methods
        def simple(dtype):
            """
            very simple correction, uses a linear fit from results_paramag_slope()
            :param dtype:
            :return:
            """
            out = deepcopy(self.corrected_data[dtype])
            correct = out['field'].v * self.result_paramag_slope(**parameter).v[0]
            out['mag'] = out['mag'].v - correct
            # print correct
            return out

        # def simple_grid(dtype):
        #     print self.grid_data
        if method =='simple':
            for dtype in self.corrected_data:
                self.corrected_data[dtype] = simple(dtype)
        if method =='simple_grid':
            for dtype in self.corrected_data:
                self.corrected_data[dtype] = self.grid_data[dtype]
                print dtype
                print self.corrected_data[dtype]
                self.corrected_data[dtype] = simple(dtype)

        # print self.corrected_data['up_field']['mag'].v[0]



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
        a2s_data = map(self.calc_approach2sat, ['down_field'])  # , 'up_field'])
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
