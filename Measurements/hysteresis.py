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
from os.path import join
from pprint import pprint


class Hys(base.Measurement):
    """
    Measurement Class for Hysteresis Measurements

    Corrections
    -----------

       correct_slope:
          *not implemented* corrects data for high-field susceptibility

       correct_hsym:
          *not implemented* corrects data for horizontal assymetry

       correct_vsym:
          *not implemented* corrects data for vertical assymetry

       correct_drift:
          *not implemented* corrects data for machine drift

       correct_pole_sat:
          *not implemented* corrects data for pole piece saturation

       correct_holder:
          *not implemented* corrects data for holder magnetization

       correct_outliers:
          *not implemented* removes outliers from data

    Results:

    Decomposition:

    Fitting
    -------



    .. testsetup:: *
       >>> import RockPy
       >>> from os.path import join
       >>> vftb_file = join(RockPy.test_data_path,'MUCVFTB_test.hys')
       >>> sample = RockPy.Sample(name='vftb_test_sample')
       >>> M = sample.add_measurement(mtype='hysteresis', mfile=vftb_file, machine='vftb')

    See Also
    --------
       :cite:`Dobeneck1996a`
       :cite:`Fabian2003`
       :cite:`Yu2005b`

    **References**
    .. bibliography:: hysteresis.bib
       :cited:
    """

    @classmethod
    def simulate(cls, sample_obj, m_idx=0, color=None,
                 ms=250., mrs_ms=0.5, bc=0.2, hf_sus=1., bmax=1.8, b_sat=1, steps=100,
                 noise=None):
        """
        Simulation of hysteresis loop using sngle tanh and sech functions.

        Parameters:
           m_idx (int): index of measurement
           ms (float): desired saturation magnetization
           mrs_ms (float): :math:`M_{rs}/M_{s}` ratio
           bc (float): desired bc
           hf_sus:

           bmax:

           b_sat: float
              Field at which 99% of the moment is saturated

           steps:

           sample_obj:

           color:

           parameter:

        :Returns:

        :Note:

        Increasing the Mrs/Ms ratio to more then 0.5 results in weird looking hysteresis loops

        :TODO:

           Not working properly, yet. Use with caution
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
    def get_grid(cls, bmax=1, grid_points=30, tuning=10):
        grid = []
        # calculating the grid
        for i in xrange(-grid_points, grid_points + 1):
            if i != 0:
                boi = (abs(i) / i) * (bmax / tuning) * ((tuning + 1) ** (abs(i) / float(grid_points)) - 1.)
            else:  # catch exception for i = 0
                boi = 0
            grid.append(boi)
        return np.array(grid)


    def __init__(self, sample_obj, mtype, mfile, machine, **options):

        super(Hys, self).__init__(sample_obj, mtype, mfile, machine, **options)

    @property
    def correction(self):
        return self.set_get_attr('_correction', value=list())

    @property
    def data(self):
        if not self._data:
            self._data = deepcopy(self._raw_data)
        return self._data

    # ## formatting functions
    def format_vftb(self):
        """
        format function that takes vftb.machine_data and transforms it into Hysteresis.RockPydata objects.

        :needed:

           virgin: virgin branch
           down_field: down field branch
           up_field: up field branch
        """
        # get data
        data = self.machine_data.out_hysteresis()
        # get header
        header = self.machine_data.header
        raw_data = RockPyData(column_names=header, data=data[0])  # todo maybe not as attribute
        dfield = np.diff(raw_data['field'].v)

        # get index where change of field value is negative
        idx = [i for i in range(len(dfield)) if dfield[i] <= 0]  # todo implement signchanges in RockPy.data
        idx += [max(idx) + 1]  # add 1 point so down and up field branches start at same values
        virgin_idx = range(0, idx[0])
        down_field_idx = idx
        up_field_idx = range(idx[-1], len(dfield) + 1)

        self._raw_data['virgin'] = raw_data.filter_idx(virgin_idx)
        self._raw_data['down_field'] = raw_data.filter_idx(down_field_idx)
        self._raw_data['up_field'] = raw_data.filter_idx(up_field_idx)

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
            self._raw_data['virgin'] = RockPyData(column_names=header, data=self.machine_data.out_hysteresis()[0])
            self._raw_data['down_field'] = RockPyData(column_names=header, data=self.machine_data.out_hysteresis()[1])
            self._raw_data['up_field'] = RockPyData(column_names=header, data=self.machine_data.out_hysteresis()[2])

        if len(segments['segment number'].v) == 2:
            self._raw_data['virgin'] = None
            self._raw_data['down_field'] = RockPyData(column_names=header, data=self.machine_data.out_hysteresis()[0])
            self._raw_data['up_field'] = RockPyData(column_names=header, data=self.machine_data.out_hysteresis()[1])

        if len(segments['segment number'].v) == 1:
            self._raw_data['virgin'] = RockPyData(column_names=header, data=self.machine_data.out_hysteresis()[0])
            self._raw_data['down_field'] = None
            self._raw_data['up_field'] = None

        try:
            self._raw_data['virgin'].rename_column('moment', 'mag')
        except AttributeError:
            pass

        try:
            self._raw_data['up_field'].rename_column('moment', 'mag')
        except AttributeError:
            pass

        try:
            self._raw_data['down_field'].rename_column('moment', 'mag')
        except AttributeError:
            pass

    def format_microsense(self):
        data = self.machine_data.out_hys()
        header = self.machine_data.header

        self._data['all'] = RockPyData(column_names=header, data=data)
        dfield = np.diff(self._data['all']['raw_applied_field_for_plot_'])
        down_field_idx = [i for i in range(len(dfield)) if dfield[i] < 0]
        up_field_idx = [i for i in range(len(dfield)) if dfield[i] > 0]

        self._raw_data['down_field'] = self.raw_data.filter_idx(down_field_idx)
        self._raw_data['down_field'].define_alias('field', 'raw_applied_field_for_plot_')
        self._raw_data['down_field'].define_alias('mag', 'raw_signal_mx')
        self._raw_data['down_field']['field'] *= 0.1 * 1e-3  # conversion Oe to Tesla

        self._raw_data['up_field'] = self.raw_data.filter_idx(up_field_idx)
        self._raw_data['up_field'].define_alias('field', 'raw_applied_field_for_plot_')
        self._raw_data['up_field'].define_alias('mag', 'raw_signal_mx')
        self._raw_data['up_field']['field'] *= 0.1 * 1e-3  # conversion Oe to Tesla

    # ## calculations

    """ RESULTS """

    def result_ms(self, method='auto', recalc=False, **parameter):
        """
        calculates the Ms value with a linear fit

        :Parameters:

           recalc: str standard(False)
              if True result will be forced to be recalculated


           parameter:
              - from_field : field value in % of max. field above which slope seems linear

        :Return:

            RockPyData

        :Methods:

           auto:
             uses simple method

           simple:
              Calculates a simple linear regression of the high field magnetization. The y-intercept is Ms.

           approach_to_sat:
              Calculates a simple approach to saturation :cite:`Dobeneck1996a`

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

    def result_hf_sus(self, saturation_field=80, method='auto', recalc=False, **options):
        if method == 'auto':
            method = 'simple'

        calc_method = '_'.join(['hf_sus', method])

        parameter = dict(saturation_field=saturation_field)
        parameter.update(options)

        self.calc_result(parameter, recalc=recalc, force_method=calc_method)
        return self.results['hf_sus']

    def result_E_delta_t(self, recalc=False, **options):
        self.calc_result(dict(), recalc)
        return self.results['E_delta_t']

    def result_E_hys(self, recalc=False, **options):
        self.calc_result(dict(), recalc)
        return self.results['E_hys']

    """ CALCULATIONS """

    def fit_hf_slope(self, saturation_percent=75., ommit_last=5):
        saturation_percent /= 100.0
        ms_all, slope_all = [], []

        for dtype in ['down_field', 'up_field']:
            b_sat = max(self.data[dtype]['field'].v) * saturation_percent
            data_plus = self.data[dtype].filter(self.data[dtype]['field'].v >= b_sat)
            data_minus = self.data[dtype].filter(self.data[dtype]['field'].v <= -b_sat)

            for dir in [data_plus, data_minus]:
                slope, intercept, r_value, p_value, std_err = stats.linregress(abs(dir['field'].v), abs(dir['mag'].v))
                ms_all.append(intercept)
                slope_all.append(slope)

        return ms_all, slope_all

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

    def calculate_ms_simple(self, saturation_field=75, **parameter):
        """
        Calculates the value for Ms
        :param parameter: from_field: from % of this value a linear interpolation will be calculated for all branches (+ & -)
        :return:
        """
        ms_all, slope_all = self.fit_hf_slope(saturation_field=saturation_field)

        self.results['ms'].v = np.median(ms_all)
        self.results['ms'].e = np.std(ms_all)
        parameter.update(dict(method='simple'))
        self.calculation_parameter['ms'].update(parameter)

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

    def calculate_hf_sus_simple(self, saturation_percent=75, **parameter):

        ms_all, slope_all = self.fit_hf_slope(saturation_percent=saturation_percent)
        self.results['hf_sus'].data = [[[np.mean(slope_all), np.std(slope_all)]]]
        self.results['hf_sus'] = np.mean(slope_all)

        parameter.update(dict(method='simple'))
        self.calculation_parameter['hf_sus'].update(parameter)

    def get_irreversible(self):
        """
        Calculates the irreversible hysteretic components :math:`M_{ih}` from the data.

        .. math::

           M_{ih} = (M^+(H) + M^-(H)) / 2

        where :math:`M^+(H)` and :math:`M^-(H)` are the upper and lower branches of the hysteresis loop

        Returns
        -------
           Mih: RockPyData

        """
        M_ih = deepcopy(self.data['down_field'])
        uf = self.data['up_field'].interpolate(self.data['down_field']['field'].v)
        M_ih['mag'] = (M_ih['mag'].v + uf['mag'].v) / 2
        return M_ih

    def get_reversible(self):
        """
        Calculates the reversible hysteretic components :math:`M_{ih}` from the data.

        .. math::

           M_{ih} = (M^+(H) + M^-(H)) / 2

        where :math:`M^+(H)` and :math:`M^-(H)` are the upper and lower branches of the hysteresis loop

        Returns
        -------
           Mrh: RockPyData

        """
        M_rh = deepcopy(self.data['down_field'])
        uf = self.data['up_field'].interpolate(self.data['down_field']['field'].v)
        M_rh['mag'] = (M_rh['mag'].v - uf['mag'].v) / 2
        return M_rh

    """ CORRECTIONS """

    def correct_outliers(self, threshold=4, check=False):
        """

        :param threshold:
        :return:
        """
        raise NotImplementedError
        mx = max(self.data['down_field']['mag'].v)
        for dtype in self.data:
            print len(self.data[dtype]['field'].v[1:]), len(np.diff(self.data[dtype]['mag'].v) / mx)

            plt.plot(self.data[dtype]['field'].v[1:], np.diff(self.data[dtype]['mag'].v) / mx)
        plt.show()

    def correct_vsym(self, method='auto', check=False):
        """
        Correction of horizontal symmetry of hysteresis loop. Horizontal displacement is found by looking for the minimum
         of the absolute magnetization value of the :math:`M_{ih}` curve. The hysteresis is then shifted by the field
         value at this point.

        Parameter
        ---------
           method: str
              for implementation of several methods of calculation
           check: str
              plot to check for consistency
        """

        if check:  # for check plot
            checkdata = deepcopy(self.data)

        pos_max = np.mean([np.max(self.data['up_field']['mag'].v), np.max(self.data['down_field']['mag'].v)])
        neg_min = np.mean([np.min(self.data['up_field']['mag'].v), np.min(self.data['down_field']['mag'].v)])
        correct = (pos_max + neg_min) / 2

        for dtype in self.data:
            self.data[dtype]['mag'] = self.data[dtype]['mag'].v - correct
        self.correction.append('vysm')

        if check:
            for dtype in self.data:
                plt.plot(self.data[dtype]['field'].v, self.data[dtype]['mag'].v, 'b.-')
                plt.plot(checkdata[dtype]['field'].v, checkdata[dtype]['mag'].v, 'r.-')
            plt.xlabel('Moment')
            plt.xlabel('Field')
            plt.legend(['original', 'corrected'])
            plt.xlim([min(self.data['down_field']['field'].v), max(self.data['down_field']['field'].v)])
            plt.grid()
            plt.show()

    def correct_hsym(self, method='auto', check=False):
        """
        Correction of horizontal symmetry of hysteresis loop. Horizontal displacement is found by looking for the minimum
         of the absolute magnetization value of the :math:`M_{ih}` curve. The hysteresis is then shifted by the field
         value at this point.

        Parameter
        ---------
           method: str
              for implementation of several methods of calculation
           check: str
              plot to check for consistency
        """

        mir = self.get_irreversible()
        idx = np.nanargmin(abs(mir['mag'].v))
        correct = mir['field'].v[idx] / 2

        if check:  # for check plot
            uncorrected_data = deepcopy(self.data)

        for dtype in self.data:
            self.data[dtype]['field'] = self.data[dtype]['field'].v - correct
        self.correction.append('hysm')
        if check:
            self.check_plot(uncorrected_data)

    def simple_paramag_cor(self, **parameter):

        # if not self.paramag_correction:
        # self.calculate_ms(**parameter)

        slope = np.mean(self.paramag_correction[:, 0])
        intercept = np.mean(self.paramag_correction[:, 2])

        for dtype in self.data:
            if self.data[dtype]:
                d = self.data[dtype].v
                d[:, 1] -= d[:, 0] * slope


    def data_gridding(self, method='first', **parameter):
        """
        Data griding after :cite:`Dobeneck1996a`. Generates an interpolated hysteresis loop with
        :math:`M^{\pm}_{sam}(B^{\pm}_{exp})` at mathematically defined (grid) field values, identical for upper
        and lower branch.

        .. math::

           B_{\text{grid}}(i) = \\frac{|i|}{i} \\frac{B_m}{\lambda} \\left[(\lambda + 1 )^{|i|/n} - 1 \\right]

        Parameters
        ----------

           method: str
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

        grid = Hys.get_grid(bmax=bm, **parameter)
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
            self.data.update({dtype: interp_data})


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

        :Parameters:

           data: str
              e.g. data, grid_data, corrected_data

           branch: str
              up-field or down-field
        """
        data = deepcopy(getattr(self, data)[branch])
        data['field'] = -data['field'].v[::-1]
        data['mag'] = -data['mag'].v[::-1]
        return data


    def correct_paramag(self, saturation_percent=75., method='simple', check=False, **parameter):
        "corrects data according to specified method"
        hf_sus = self.result_hf_sus(method=method).v[0]

        if check:
            uncorrected_data = deepcopy(self.data)

        for dtype in self.data:
            correction = hf_sus * self.data[dtype]['field'].v
            self.data[dtype]['mag'] = self.data[dtype]['mag'].v - correction

        self.correction.append('paramag')

        if check:
            ms_all, slope_all = self.fit_hf_slope(saturation_percent=saturation_percent)
            i = 0

            for dtype in ['down_field', 'up_field']:
                b_sat = max(self.data[dtype]['field'].v) * (saturation_percent / 100)
                data_plus = self.data[dtype].filter(self.data[dtype]['field'].v >= b_sat)
                data_minus = self.data[dtype].filter(self.data[dtype]['field'].v <= -b_sat)
                std, = plt.plot(abs(data_plus['field'].v), abs(data_plus['mag'].v))
                plt.plot(abs(data_plus['field'].v), ms_all[i] + abs(data_plus['field'].v) * slope_all[i], '--',
                         color=std.get_color())
                i += 1

                std, = plt.plot(abs(data_minus['field'].v), abs(data_minus['mag'].v))
                plt.plot(abs(data_minus['field'].v), ms_all[i] + abs(data_minus['field'].v) * slope_all[i], '--',
                         color=std.get_color())
                i += 1
            plt.legend(loc='best')
            plt.show()
            self.check_plot(uncorrected_data)


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


    ### helper functions

    def check_if_msi(self):
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

    def check_plot(self, uncorrected_data):
        """
        Helper function for consistent check visualization

        Parameters
        ----------
           uncorrected_data: RockPyData
              the pre-correction data.
        """

        for dtype in self.data:
            plt.plot(self.data[dtype]['field'].v, self.data[dtype]['mag'].v, color='g')
            plt.plot(uncorrected_data[dtype]['field'].v, uncorrected_data[dtype]['mag'].v, color='r')

        plt.xlabel('Moment')
        plt.xlabel('Field')
        plt.legend(['original', 'corrected'])
        plt.grid(zorder=1)
        plt.axhline(color='k', zorder=1)
        plt.axvline(color='k', zorder=1)
        plt.xlim([min(self.data['down_field']['field'].v), max(self.data['down_field']['field'].v)])
        plt.show()

    def export_vftb(self, folder=None, filename=None):
        import os


if __name__ == '__main__':
    import RockPy

    vsm_file = RockPy.join(RockPy.test_data_path, 'MUCVSM_test.hys')
    vftb_file = RockPy.join(RockPy.test_data_path, 'MUCVFTB_test.hys')
    s = RockPy.Sample(name='test_sample')
    m = s.add_measurement(mtype='hys', mfile=vsm_file, machine='vsm')
    # m = s.add_measurement(mtype='hys', mfile=vftb_file, machine='vftb')
    m.data_gridding(grid_points=40, tuning=5)
    m.correct_hsym(check=True)
    m.correct_vsym(check=True)
    m.correct_paramag(method='simple', check=True)
    print m.correction