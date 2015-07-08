__author__ = 'volk'
import inspect
import numpy as np
import matplotlib.pyplot as plt
import logging
import base
import RockPy
from RockPy.Structure.data import RockPyData
from scipy import stats
from scipy.optimize import curve_fit
from copy import deepcopy
import scipy as sp
from math import tanh, cosh
from os.path import join
from pprint import pprint
from profilehooks import profile
from lmfit import minimize, Parameters, Parameter, report_fit
from profilehooks import profile


class Hys(base.Measurement):
    """
    Measurement Class for Hysteresis Measurements

    **Corrections**

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

    **Fitting**

    See Also
    --------

       :cite:`Dobeneck1996a`
       :cite:`Fabian2003`
       :cite:`Yu2005b`

    .. testsetup:: *
       >>> import RockPy
       >>> from os.path import join
       >>> vftb_file = join(RockPy.test_data_path,'MUCVFTB_test.hys')
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
        data['up_field'] = RockPyData(column_names=['field', 'mag'], data=np.c_[fields, rev_mag - irrev_mag])
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

    @staticmethod
    def approach2sat_func(h, ms, chi, alpha):
        """
        General approach to saturation function

        Parameters
        ----------
           x: ndarray
              field
           ms: float
              saturation magnetization
           chi: float
              susceptibility
           alpha: float
           beta: float
              not fitted assumed -2

        Returns
        -------
           ndarray:
              :math:`M_s \chi * B + \\alpha * B^{\\beta = -2}`
        """
        return ms + chi * h - alpha * h ** -2  # beta

    @staticmethod
    def fit_tanh(params, x, data=0):
        """
        Function for fitting up to four tanh functions to reversible branch of hysteresis

        Parameters
        ----------
           params: Parameterclass lmfit
              Bti: saturation magnetization of ith component
              Gti: curvature of ith component related to coercivity
           x: array-like
              x-values of data for fit
           data: array-like
              y-values of data for fit

        Returns
        -------
           residual: array-like
              Residual of fitted data and measured data
        """
        Bt1 = params['Bt1'].value
        Bt2 = params['Bt2'].value
        Bt3 = params['Bt3'].value
        Bt4 = params['Bt4'].value
        Gt1 = params['Gt1'].value
        Gt2 = params['Gt2'].value
        Gt3 = params['Gt3'].value
        Gt4 = params['Gt4'].value
        Et = params['Et'].value

        model = Bt1 * np.tanh(Gt1 * x)
        model += Bt2 * np.tanh(Gt2 * x)
        model += Bt3 * np.tanh(Gt3 * x)
        model += Bt4 * np.tanh(Gt4 * x)
        model += Et * x
        return np.array(model - data)

    @staticmethod
    def fit_sech(params, x, data=0):
        """
        Function for fitting up to four sech functions to reversible branch of hysteresis

        Parameters
        ----------
           params: Parameterclass lmfit
              Bsi: saturation magnetization of ith component
              Gsi: curvature of ith component related to coercivity
           x: array-like
              x-values of data for fit
           data: array-like
              y-values of data for fit

        Returns
        -------
           residual: array-like
              Residual of fitted data and measured data
        """
        Bs1 = params['Bs1'].value
        Bs2 = params['Bs2'].value
        Bs3 = params['Bs3'].value
        Bs4 = params['Bs4'].value
        Gs1 = params['Gs1'].value
        Gs2 = params['Gs2'].value
        Gs3 = params['Gs3'].value
        Gs4 = params['Gs4'].value

        model = Bs1 * np.cosh(Gs1 * x) ** -1
        model += Bs2 * np.cosh(Gs2 * x) ** -1
        model += Bs3 * np.cosh(Gs3 * x) ** -1
        model += Bs4 * np.cosh(Gs4 * x) ** -1
        return np.array(model - data)

    @staticmethod
    def unvary_params(params):
        for p in params:
            p.set(vary=False)
            p.set(value=0)
        return params

    # @profile
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
        data = self.machine_data.get_data()
        # get header
        header = self.machine_data.header
        raw_data = RockPyData(column_names=header, data=data[0])  # todo maybe not as attribute
        dfield = np.diff(raw_data['field'].v)

        # get index where change of field value is negative
        idx = [i for i in range(len(dfield)) if dfield[i] <= 0]  # todo implement signchanges in RockPy.data
        idx += [max(idx) + 1]  # add 1 point so down and up field branches start at same values

        virgin_idx = range(0, idx[0] + 1)
        down_field_idx = idx
        up_field_idx = range(idx[-1], len(dfield) + 1)

        self._raw_data['virgin'] = raw_data.filter_idx(virgin_idx).sort('field')
        self._raw_data['down_field'] = raw_data.filter_idx(down_field_idx).sort('field')
        self._raw_data['up_field'] = raw_data.filter_idx(up_field_idx).sort('field')

    def format_vsm(self):
        header = self.machine_data.header
        segments = self.machine_data.segment_info
        data = self.machine_data.out_hysteresis()
        # print header
        if 'adjusted field' in header:
            header[header.index('adjusted field')] = 'field'
            header[header.index('field')] = 'uncorrected field'

        if 'adjusted moment' in header:
            header[header.index('moment')] = 'uncorrected moment'
            header[header.index('adjusted moment')] = 'moment'

        if len(segments['segment number'].v) == 3:
            self._raw_data['virgin'] = RockPyData(column_names=header, data=data[0],
                                                  units=self.machine_data.units).sort('field')
            self._raw_data['down_field'] = RockPyData(column_names=header, data=data[1],
                                                      units=self.machine_data.units).sort('field')
            self._raw_data['up_field'] = RockPyData(column_names=header, data=data[2],
                                                    units=self.machine_data.units).sort('field')

        if len(segments['segment number'].v) == 2:
            self._raw_data['virgin'] = None
            self._raw_data['down_field'] = RockPyData(column_names=header, data=data[0],
                                                      units=self.machine_data.units).sort('field')
            self._raw_data['up_field'] = RockPyData(column_names=header, data=data[1],
                                                    units=self.machine_data.units).sort('field')

        if len(segments['segment number'].v) == 1:
            self._raw_data['virgin'] = RockPyData(column_names=header, data=data[0],
                                                  #units=self.machine_data.units
                                                  ).sort('field')
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
        self._raw_data['down_field'] = self._raw_data['down_field'].sort('field')

        self._raw_data['up_field'] = self.raw_data.filter_idx(up_field_idx)
        self._raw_data['up_field'].define_alias('field', 'raw_applied_field_for_plot_')
        self._raw_data['up_field'].define_alias('mag', 'raw_signal_mx')
        self._raw_data['up_field']['field'] *= 0.1 * 1e-3  # conversion Oe to Tesla
        self._raw_data['up_field'] = self._raw_data['up_field'].sort('field')

    # ## calculations

    """ RESULTS """

    def result_bc(self, recalc=False, **options):
        """
        Calculates :math:`B_c` using a linear interpolation between the points closest to zero.

           recalc: bool
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

    def result_brh(self, recalc=False, **options):
        self.calc_result(dict(), recalc)
        return self.results['brh']

    def result_e_delta_t(self, recalc=False, **options):
        self.calc_result(dict(), recalc)
        return self.results['e_delta_t']

    def result_e_hys(self, recalc=False, **options):
        self.calc_result(dict(), recalc)
        return self.results['e_hys']

    def result_hf_sus(self, saturation_percent=75., method='simple', remove_last=0, recalc=False, **options):
        """
        Calculates the result for high field susceptibility using the specified method

        Parameters
        ----------
           saturation_percent: float
              field at which saturation is assumed. Only data at higher (or lower negative) is used for analysis
           method: str
              method of analysis
              :simple: uses simple linear regression above saturation_percent
           recalc: bool
              forced recalculation of result
           options: dict
              additional arguments

        Returns
        -------
           RockPyData
        """
        calc_method = '_'.join(['hf_sus', method])

        parameter = dict(saturation_percent=saturation_percent,
                         remove_last=remove_last,
                         method=method)

        parameter.update(options)

        self.calc_result(parameter, recalc=recalc, force_method=calc_method)
        return self.results['hf_sus']

    def result_mrs(self, recalc=False, **parameter):
        self.calc_result(parameter = parameter, recalc=recalc)
        return self.results['mrs']

    def result_ms(self, method='simple', recalc=False, **parameter):
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

        calc_method = '_'.join(['ms', method])
        parameter.update(dict(method=method))
        self.calc_result(parameter, recalc, force_method=calc_method)
        return self.results['ms']


    """ CALCULATIONS """

    def fit_hf_slope(self, saturation_percent=75.):  # todo ommit_last n points
        saturation_percent /= 100.0
        ms_all, slope_all = [], []

        for dtype in ['down_field', 'up_field']:
            b_sat = max(self.data[dtype]['field'].v) * saturation_percent
            data_plus = self.data[dtype].filter(self.data[dtype]['field'].v >= b_sat)
            data_minus = self.data[dtype].filter(self.data[dtype]['field'].v <= -b_sat)
            for dir in [data_plus, data_minus]:
                try:
                    slope, intercept, r_value, p_value, std_err = stats.linregress(abs(dir['field'].v), abs(dir['mag'].v))
                    ms_all.append(intercept)
                    slope_all.append(slope)
                except ValueError:
                    print self.sample_obj.name, self.mtype
                    print '-----------------------'
                    print dir['field'].v, dir['mag'].v
        return ms_all, slope_all

    def calculate_ms(self, method='simple', **parameter):
        """
        Wrapper so one can call calculate_ms on its own, giving the method as an argument

        Parameters
        ----------
           method: str
              the method used for calculation
                 simple:
                 app2sat:
           parameter: dict
              additional parameters needed for calculation. If nothin is provided standard parameter will be used.

        """
        method = 'calculate_ms_' + method
        implemented = [i for i in dir(self) if i.startswith('calculate_ms_')]
        if method in implemented:
            out = getattr(self, method)(**parameter)
        return out

    def calculate_ms_simple(self, saturation_percent=75, **parameter):
        """
        Calculates the value for Ms

        Parameters
        ----------
           parameter: dict
              from_field: float
                 from % of this value a linear interpolation will be calculated for all branches (+ & -)

        """
        ms_all, slope_all = self.fit_hf_slope(saturation_percent=saturation_percent)
        self.results['ms'] = [[[np.mean(ms_all), np.std(ms_all)]]]
        parameter.update(dict(method='simple'))
        self.calculation_parameter['ms'].update(parameter)
        return np.mean(ms_all)

    def calculate_mrs(self, **parameter):

        def calc(direction):
            d = self.data[direction]
            data = d['field'].v
            idx = np.argmin(abs(data))  # index of closest to 0
            if data[idx] < 0:
                if data[idx + 1] < 0:
                    i = [idx, idx - 1]
                else:
                    i = [idx + 1, idx]
            else:
                if data[idx + 1] < 0:
                    i = [idx + 1, idx]
                else:
                    i = [idx - 1, idx]

            d = d.filter_idx(i)

            x = d['field'].v
            y = d['mag'].v
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            return abs(intercept)

        df = calc('down_field')
        uf = calc('up_field')
        self.results['mrs'] = np.mean([df, uf])#, np.std([df, uf])]]]
        return (df+ uf)/2

    def calculate_bc(self, **parameter):
        '''

        :return:
        '''
        # Hysteresis.logger.info('CALCULATING << Bc >> parameter from linear interpolation between points closest to m=0')

        def calc(direction):
            d = self.data[direction]
            data = d['mag'].v
            idx = np.argmin(abs(data))  # index of closest to 0
            if data[idx] < 0:
                if data[idx + 1] < 0:
                    i = (idx, idx - 1)
                else:
                    i = (idx + 1, idx)
            else:
                if data[idx + 1] < 0:
                    i = (idx + 1, idx)
                else:
                    i = (idx - 1, idx)

            d = d.filter_idx(i)

            dy = d['mag'].v[1] - d['mag'].v[0]
            dx = d['field'].v[1] - d['field'].v[0]
            m = dy / dx
            b = d['mag'].v[1] - d['field'].v[1] * m
            bc = abs(b / m)
            return bc

        df = calc('down_field')
        uf = calc('up_field')
        self.results['bc'] = [[[np.nanmean([df, uf]), np.nanstd([df, uf])]]]
        return np.mean([df, uf])

    def calculate_brh(self, **parameter):
        pass  # todo implement

    def calculate_e_delta_t(self, **parameter):
        """
        Method calculates the :math:`E^{\Delta}_t` value for the hysteresis.
        It uses scipy.integrate.simps for calculation of the area under the down_field branch for positive fields and
        later subtracts the area under the Msi curve.

        The energy is:

        .. math::

           E^{\delta}_t = 2 \int_0^{B_{max}} (M^+(B) - M_{si}(B)) dB

        """
        if not self.msi_exists:
            self.logger.error('%s\tMsi branch does not exist or not properly saturated. Please check datafile'%self.sample_obj.name)
            self.results['e_delta_t'] = np.nan
            return np.nan

        # getting data for positive down field branch
        df_pos_fields = [v for v in self.data['down_field']['field'].v if v >= 0] + [0.0]  # need to add 0 to fields
        df_pos = self.data['down_field'].interpolate(df_pos_fields)  # interpolate value for 0
        df_pos_area = abs(sp.integrate.simps(y=df_pos['mag'].v, x=df_pos['field'].v))  # calculate area under downfield

        msi_area = abs(sp.integrate.simps(y=self.data['virgin']['mag'].v,
                                          x=self.data['virgin']['field'].v))  # calulate area under virgin

        self.results['e_delta_t'] = abs(2 * (df_pos_area - msi_area))
        self.calculation_parameter['e_delta_t'].update(parameter)
        return self.results['e_delta_t'].v[0]

    def calculate_e_hys(self, **parameter):
        '''
        Method calculates the :math:`E^{Hys}` value for the hysteresis.
        It uses scipy.integrate.simps for calculation of the area under the down_field branch and
        later subtracts the area under the up-field branch.

        The energy is:

        .. math::

           E^{Hys} = \int_{-B_{max}}^{B_{max}} (M^+(B) - M^-(B)) dB

        '''

        df_area = sp.integrate.simps(y=self.data['down_field']['mag'].v,
                                     x=self.data['down_field']['field'].v)  # calulate area under down_field
        uf_area = sp.integrate.simps(y=self.data['up_field']['mag'].v,
                                     x=self.data['up_field']['field'].v)  # calulate area under up_field

        self.results['e_hys'] = abs(df_area - uf_area)
        self.calculation_parameter['e_hys'].update(parameter)
        return self.results['e_hys'].v[0]

    def calculate_hf_sus_simple(self, **parameter):
        """
        Calculates High-Field susceptibility using a simple linear regression on all branches
        :param parameter:
        :return:
        """
        saturation_percent = parameter.get('saturation_percent', 75.)
        ms_all, slope_all = self.fit_hf_slope(saturation_percent=saturation_percent)
        self.results['hf_sus'].data = [[[np.mean(slope_all), np.std(slope_all)]]]
        self.results['hf_sus'] = np.mean(slope_all)

        parameter.update(dict(method='simple'))
        self.calculation_parameter['hf_sus'].update(parameter)

        return self.results['hf_sus'].v[0]

    def calculate_hf_sus_app2sat(self, **parameter):
        """
        Calculates the high field susceptibility using approach to saturation
        :return:
        """
        saturation_percent = parameter.get('saturation_percent', 75.)
        remove_last = parameter.get('remove_last', 0)

        res_uf1, res_uf2 = self.calc_approach2sat(saturation_percent=saturation_percent, branch='up_field',
                                                  remove_last=remove_last)
        res_df1, res_df2 = self.calc_approach2sat(saturation_percent=saturation_percent, branch='down_field',
                                                  remove_last=remove_last)
        res = np.c_[res_uf1, res_uf2, res_df1, res_df2]

        self.results['ms'] = [[[np.mean(res, axis=1)[0], np.std(res, axis=1)[0]]]]
        self.results['hf_sus'] = [[[np.mean(res, axis=1)[1], np.std(res, axis=1)[1]]]]
        self.results = self.results.append_columns(column_names=['alpha'],
                                                   data=[[[np.mean(res, axis=1)[2], np.std(res, axis=1)[2]]]])

        parameter.update(dict(method='app2sat'))
        self.calculation_parameter['hf_sus'].update(parameter)
        return self.results['hf_sus'].v[0]

    def get_irreversible(self, correct_symmetry=True):
        """
        Calculates the irreversible hysteretic components :math:`M_{ih}` from the data.

        .. math::

           M_{ih} = (M^+(H) + M^-(H)) / 2

        where :math:`M^+(H)` and :math:`M^-(H)` are the upper and lower branches of the hysteresis loop

        Returns
        -------
           Mih: RockPyData

        """
        field_data = sorted(list(set(self.data['down_field']['field'].v) | set(self.data['up_field']['field'].v)))
        uf = self.data['up_field'].interpolate(field_data)
        df = self.data['down_field'].interpolate(field_data)
        M_ih = deepcopy(uf)
        M_ih['mag'] = (df['mag'].v + uf['mag'].v) / 2

        if correct_symmetry:
            M_ih_pos = M_ih.filter(M_ih['field'].v >= 0).interpolate(np.fabs(field_data))
            M_ih_neg = M_ih.filter(M_ih['field'].v <= 0).interpolate(np.fabs(field_data))

            mean_data = np.mean(np.c_[M_ih_pos['mag'].v, -M_ih_neg['mag'].v], axis=1)
            M_ih['mag'] = list(-mean_data).extend(list(mean_data))

        return M_ih.filter(~np.isnan(M_ih['mag'].v))

    def get_reversible(self):
        """
        Calculates the reversible hysteretic components :math:`M_{rh}` from the data.

        .. math::

           M_{ih} = (M^+(H) - M^-(H)) / 2

        where :math:`M^+(H)` and :math:`M^-(H)` are the upper and lower branches of the hysteresis loop

        Returns
        -------
           Mrh: RockPyData

        """
        field_data = sorted(list(set(self.data['down_field']['field'].v) | set(self.data['up_field']['field'].v)))
        uf = self.data['up_field'].interpolate(field_data)
        df = self.data['down_field'].interpolate(field_data)
        M_rh = deepcopy(uf)
        M_rh['mag'] = (df['mag'].v - uf['mag'].v) / 2
        return M_rh.filter(~np.isnan(M_rh['mag'].v))

    def get_interpolated(self, branch):
        """
        calculates interpolated mag values for all field values for up and down field branch
        :param branch:
        :return:
        """
        field_data = sorted(list(set(self.data['down_field']['field'].v) | set(self.data['up_field']['field'].v)))
        uf = self.data['up_field'].interpolate(field_data)
        df = self.data['down_field'].interpolate(field_data)

        if branch == 'down_field':
            return df
        if branch == 'up_field':
            return uf
        if branch == 'all':
            return df, uf

    """ CORRECTIONS """

    def correct_outliers(self, threshold=4, check=False):
        """
        Method that corrects outliers

        Parameters
        ----------
           threshold: int
              standard deviation away from fit

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

        Parameters
        ----------
           method: str
              for implementation of several methods of calculation
           check: str
              plot to check for consistency
        """

        if check:  # for check plot
            uncorrected_data = deepcopy(self.data)

        pos_max = np.mean([np.max(self.data['up_field']['mag'].v), np.max(self.data['down_field']['mag'].v)])
        neg_min = np.mean([np.min(self.data['up_field']['mag'].v), np.min(self.data['down_field']['mag'].v)])
        correct = (pos_max + neg_min) / 2

        for dtype in self.data:
            self.data[dtype]['mag'] = self.data[dtype]['mag'].v - correct
        self.correction.append('vysm')

        if check:
            self.check_plot(uncorrected_data)

    def correct_hsym(self, method='auto', check=False):
        """
        Correction of horizontal symmetry of hysteresis loop. Horizontal displacement is found by looking for the minimum
         of the absolute magnetization value of the :math:`M_{ih}` curve. The hysteresis is then shifted by the field
         value at this point.

        Parameters
        ----------
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

    def correct_paramag(self, saturation_percent=75., method='simple', check=False, **parameter):
        """
        corrects data according to specified method

        Parameters
        ----------
           saturation_percent: float
              default: 75.0
           method: str
              default='simple'
              methods= ...
           check: bool
           parameter: dict

        Returns
        -------

        """

        hf_sus = self.result_hf_sus(method=method).v[0]

        if check:
            # make deepcopy for checkplot
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

    def correct_center(self, check=False):

        if check:
            uncorrected_data = deepcopy(self.data)

        df = self.data['down_field']
        uf = self.data['up_field']

        uf_rotate = self.rotate_branch(uf)
        df_rotate = self.rotate_branch(df)

        fields = sorted(
            list(set(df['field'].v) | set(uf['field'].v) | set(df_rotate['field'].v) | set(uf_rotate['field'].v)))

        # interpolate all branches and rotations
        df = df.interpolate(fields)
        uf = uf.interpolate(fields)
        df_rotate = df_rotate.interpolate(fields)
        uf_rotate = uf_rotate.interpolate(fields)

        down_field_corrected = deepcopy(df)
        up_field_corrected = deepcopy(uf)
        down_field_corrected['mag'] = (df['mag'].v + uf_rotate['mag'].v) / 2

        up_field_corrected['field'] = - down_field_corrected['field'].v
        up_field_corrected['mag'] = - down_field_corrected['mag'].v

        self.data.update(dict(up_field=up_field_corrected, down_field=down_field_corrected))

        if check:
            self.check_plot(uncorrected_data=uncorrected_data)


    def correct_slope(self):  # todo redundant
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

    def correct_holder(self):
        raise NotImplementedError

    def fit_irrev(self, nfunc, check=False):
        """
        Fitting of the irreversible part of the hysteresis

        :param nfunc:
        :return:
        """
        hf_sus = self.result_hf_sus().v[0]
        ms = self.result_ms().v[0]

        # create a set of Parameters
        params = Parameters()
        params.add('Bt1', value=ms, min=0)
        params.add('Bt2', value=ms, min=0)
        params.add('Bt3', value=ms, min=0)
        params.add('Bt4', value=ms, min=0)

        params.add('Gt1', value=0.1)
        params.add('Gt2', value=0.1)
        params.add('Gt3', value=0.1)
        params.add('Gt4', value=0.1)

        # params.add('Et',   value= 9.81e-5,  vary=False)
        params.add('Et', value=hf_sus, vary=True)

        # set parameters to zero and fix them if less functions are required
        if nfunc < 4:
            self.unvary_params([params['Bt4'], params['Gt4']])
        if nfunc < 3:
            self.unvary_params([params['Bt3'], params['Gt3']])
        if nfunc < 2:
            self.unvary_params([params['Bt2'], params['Gt2']])

        data = self.get_irreversible()
        result = minimize(self.fit_tanh, params, args=(data['field'].v, data['mag'].v))

        if check:
            plt.plot(data['field'].v, data['mag'].v / max(data['mag'].v))
            plt.plot(data['field'].v, (data['mag'].v + result.residual) / max(data['mag'].v))
            plt.plot(data['field'].v, result.residual / max(result.residual))
            plt.show()

            print 'FITTING RESULTS FOR IRREVERSIBLE (TANH) %i COMPONENTS' % nfunc
            report_fit(params)

        return result

    def fit_rev(self, nfunc, check):
        """
        Fitting of the irreversible part of the hysteresis

        :param nfunc:
        :return:
        """
        mrs = self.result_mrs().v[0]
        # create a set of Parameters
        rev_params = Parameters()
        rev_params.add('Bs1', value=mrs, min=0)
        rev_params.add('Bs2', value=mrs, min=0)
        rev_params.add('Bs3', value=mrs, min=0)
        rev_params.add('Bs4', value=mrs, min=0)

        rev_params.add('Gs1', value=1)
        rev_params.add('Gs2', value=1)
        rev_params.add('Gs3', value=1)
        rev_params.add('Gs4', value=1)

        # set parameters to zero and fix them if less functions are required
        if nfunc < 4:
            self.unvary_params([rev_params['Bs4'], rev_params['Gs4']])
        if nfunc < 3:
            self.unvary_params([rev_params['Bs3'], rev_params['Gs3']])
        if nfunc < 2:
            self.unvary_params([rev_params['Bs2'], rev_params['Gs2']])

        data = self.get_reversible()
        result = minimize(self.fit_sech, rev_params, args=(data['field'].v, data['mag'].v))
        if check:
            plt.plot(data['field'].v, data['mag'].v / max(data['mag'].v))
            plt.plot(data['field'].v, (data['mag'].v + result.residual) / max(data['mag'].v))
            plt.plot(data['field'].v, result.residual / max(result.residual))
            plt.show()

            print 'FITTING RESULTS FOR REVERSIBLE (SECH) %i COMPONENTS' % nfunc
            report_fit(rev_params)
        return result

    # @profile
    def fit_hysteresis(self, nfunc=1, correct_symmetry=True, check=False):
        """
        Fitting of hysteresis functions. Removes virgin branch in process.
        :param nfunc:
        :return:
        """
        if check:
            initial_data = deepcopy(self.data)

        # calclate irrev & reversible data
        irrev_data = self.get_irreversible(correct_symmetry=correct_symmetry)
        rev_data = self.get_reversible()

        # calculate fit for each component
        irrev_result = self.fit_irrev(nfunc=nfunc, check=check)
        rev_result = self.fit_rev(nfunc=nfunc, check=check)

        # generate new data
        fields = np.linspace(min(irrev_data['field'].v), max(irrev_data['field'].v), 300)
        irrev_mag = self.fit_tanh(irrev_result.params, fields)
        rev_mag = self.fit_sech(rev_result.params, fields)

        df_data = RockPyData(column_names=['field', 'mag'],
                             data=np.array([[fields[i], irrev_mag[i] + rev_mag[i]] for i in xrange(len(fields))]))
        uf_data = RockPyData(column_names=['field', 'mag'],
                             data=np.array([[fields[i], irrev_mag[i] - rev_mag[i]] for i in xrange(len(fields))]))

        self.data['down_field'] = df_data
        self.data['up_field'] = uf_data
        self.data['virgin'] = None

        if check:
            self.check_plot(uncorrected_data=initial_data)

    ### helper functions
    @property
    def msi_exists(self):
        """
        Checks if Msi branch is present in data by comparing the starting point of the virginbranch with Ms.
        If virgin(0) >= 0.7 * Ms it returns True

        Returns
        -------
           bool
        """
        if self.data['virgin']:
            mrs = self.result_mrs().v
            if abs(self.data['virgin']['mag'].v[0]) >= 0.7 * mrs:
                return True

    def data_gridding(self, method='second', grid_points=20, tuning=1, **parameter):
        """
        Data griding after :cite:`Dobeneck1996a`. Generates an interpolated hysteresis loop with
        :math:`M^{\pm}_{sam}(B^{\pm}_{exp})` at mathematically defined (grid) field values, identical for upper
        and lower branch.

        .. math::

           B_{\text{grid}}(i) = \\frac{|i|}{i} \\frac{B_m}{\lambda} \\left[(\lambda + 1 )^{|i|/n} - 1 \\right]

        Parameters
        ----------

           method: str
              method with which the data is fitted between grid points.

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

        if len(self.data['down_field']['field'].v) <= 50:
            self.logger.warning('Hysteresis branches have less than 50 (%i) points, gridding not possible' % (
                len(self.data['down_field']['field'].v)))
            return

        bmax = max([max(self.data['down_field']['field'].v), max(self.data['up_field']['field'].v)])
        bmin = min([min(self.data['down_field']['field'].v), min(self.data['up_field']['field'].v)])
        bm = max([abs(bmax), abs(bmin)])

        grid = Hys.get_grid(bmax=bm, grid_points=grid_points, tuning=tuning, **parameter)
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
            if dtype == 'virging':
                dtype = [i for i in dtype if i >= 0]

            interp_data = RockPyData(column_names=['field', 'mag'])
            d = self.data[dtype]
            for i in range(1, len(grid) - 1):  # cycle through gridpoints
                idx = [j for j, v in enumerate(d['field'].v) if
                       grid[i - 1] <= v <= grid[i + 1]]  # indices of points within the grid points
                if len(idx) > 0:  # if no points between gridpoints -> no interpolation
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
                        self.logger.error('Length of data for interpolation < 2')
                        self.logger.error(
                            'consider reducing number of points for interpolation or lower tuning parameter')

            if 'temperature' in self.data[dtype].column_names:
                temp = np.mean(self.data[dtype]['temperature'].v)
                std_temp = np.std(self.data[dtype]['temperature'].v)
                temp = np.ones(len(interp_data['mag'].v)) * temp
                interp_data = interp_data.append_columns(column_names='temperature', data=temp)

            self.data.update({dtype: interp_data})

    def rotate_branch(self, branch, data='data'):
        """
        rotates a branch by 180 degrees, by multiplying the field and mag values by -1

        :Parameters:

           data: str
              e.g. data, grid_data, corrected_data

           branch: str or. RockPyData
              up-field or down-field
              RockPyData: will rotate the data
        """
        if isinstance(branch, str):
            data = deepcopy(getattr(self, data)[branch])
        if isinstance(branch, RockPyData):
            data = deepcopy(branch)
        data['field'] = -data['field'].v
        data['mag'] = -data['mag'].v
        return data.sort()

    def calc_approach2sat(self, saturation_percent, branch, remove_last):
        """
        calculates approach to saturation
        :param branch:
        :return:
        """
        saturation_percent /= 100.0

        #### POSITIVE BRANCH
        # get idx of downfield branch where b > 0
        df_pos = deepcopy(self.data[branch].filter(self.data[branch]['field'].v >= saturation_percent * max(
            self.data[branch]['field'].v)))  # down field with positive field data

        df_neg = deepcopy(self.data[branch].filter(self.data[branch]['field'].v <= -saturation_percent * max(
            self.data[branch]['field'].v)))  # down field with positive field data
        df_neg['field'] = -df_neg['field'].v
        df_neg['mag'] = -df_neg['mag'].v

        popt_pos, pcov_pos = curve_fit(self.approach2sat_func, df_pos['field'].v,
                                       df_pos['mag'].v, p0=[max(df_pos['mag'].v), 1e-3, 0])
        popt_neg, pcov_neg = curve_fit(self.approach2sat_func, df_neg['field'].v,
                                       df_neg['mag'].v, p0=[max(df_pos['mag'].v), 1e-3, 0])
        return popt_pos, popt_neg

    def set_field_limit(self, field_limit):
        """
        Cuts fields with higer or lower values

        Parameters
        ----------
           field_limit: float
              cut-off field, after which the data is removed from self.data. It is still in self.raw_data
        """

        for dtype in self._data:
            self._data[dtype] = self._data[dtype].filter(abs(self._data[dtype]['field'].v) <= field_limit)

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

    def check_plot(self, corrected_data=None, uncorrected_data=None, noshow=False):
        """
        Helper function for consistent check visualization

        Parameters
        ----------
           uncorrected_data: RockPyData
              the pre-correction data.
        """
        if not corrected_data:
            corrected_data = self.data
        f, ax = plt.subplots()

        for dtype in corrected_data:
            try:
                ax.plot(corrected_data[dtype]['field'].v, corrected_data[dtype]['mag'].v, color='g', marker='.')
                ax.plot(uncorrected_data[dtype]['field'].v, uncorrected_data[dtype]['mag'].v, color='r', marker='.',
                        ls='')
            except TypeError:
                pass

        if not noshow:
            ax.set_ylabel('Moment')
            ax.set_xlabel('Field')
            ax.legend(['corrected / fitted', 'original'], loc='best')
            ax.grid(zorder=1)
            ax.axhline(color='k', zorder=1)
            ax.axvline(color='k', zorder=1)
            ax.set_xlim([min(corrected_data['down_field']['field'].v), max(corrected_data['down_field']['field'].v)])
            plt.show()

    def export_vftb(self, folder=None, filename=None):
        from os import path

        abbrev = {'hys': 'hys', 'backfield': 'coe', 'irm_acquisition': 'irm', 'temp_ramp': 'rmp'}

        if not folder:
            folder = RockPy.join(path.expanduser('~'), 'Desktop')

        if self.get_mtype_prior_to(mtype='mass'):
            mass = self.get_mtype_prior_to(mtype='mass').data['data']['mass'].v[0] * 1e5  # mass converted from kg to mg

        if not filename:
            filename = RockPy.get_fname_from_info(sample_group='RockPy', sample_name=self.sample_obj.name,
                                                 mtype='HYS', machine=self.machine, mass=mass, mass_unit='mg')[
                       :-4].replace('.', ',') \
                       + '.' + abbrev[self.mtype]

        line_one = 'name: ' + self.sample_obj.name + '\t' + 'weight: ' + '%.0f mg' % mass
        line_two = ''
        line_three = 'Set 1:'
        line_four = ' field / Oe	mag / emu / g	temp / centigrade	time / s	std dev / %	suscep / emu / g / Oe'
        field, mag, temp, time, std, sus = [], [], [], [], [], []
        for dtype in ['virgin', 'down_field', 'up_field']:
            if 'field' in self.data[dtype].column_names:
                field.extend(
                    self.data[dtype]['field'].v * 10000)  # converted from tesla to Oe #todo unit check and conversion
            if 'mag' in self.data[dtype].column_names:
                mag.extend(
                    self.data[dtype]['mag'].v / mass)  # converted from tesla to Oe #todo unit check and conversion
            if 'temperature' in self.data[dtype].column_names:
                temp.extend(self.data[dtype]['temperature'].v - 274.15)
            else:
                temp = np.zeros(len(field))
            if 'time' in self.data[dtype].column_names:
                time.extend(self.data[dtype]['time'].v)
            else:
                time = np.zeros(len(field))
            if 'std' in self.data[dtype].column_names:
                std.extend(self.data[dtype]['std'].v)
            else:
                std = np.zeros(len(field))
            if 'sus' in self.data[dtype].column_names:
                sus.extend(self.data[dtype]['sus'].v)
            else:
                sus = np.zeros(len(field))
        data = np.c_[field, mag, temp, time, std, sus]
        data = ['\t'.join(map(str, i)) for i in data]
        data = '\n'.join(data)
        with open(RockPy.join(folder, filename), 'w+') as f:
            f.writelines(line_one + '\n')
            f.writelines(line_two + '\n')
            f.writelines(line_three + '\n')
            f.writelines(line_four + '\n')
            f.writelines(data)


def plot_app2sat(m, sat_perc=80):
    sat_perc /= 100
    dfp = m.data['down_field'].filter(m.data['down_field']['field'].v > sat_perc * max(m.data['down_field']['field'].v))
    dfm = m.data['down_field'].filter(
        m.data['down_field']['field'].v < -sat_perc * max(m.data['down_field']['field'].v))
    ufp = m.data['up_field'].filter(m.data['up_field']['field'].v > sat_perc * max(m.data['up_field']['field'].v))
    ufm = m.data['up_field'].filter(m.data['up_field']['field'].v < -sat_perc * max(m.data['up_field']['field'].v))
    x = np.linspace(sat_perc * max(m.data['up_field']['field'].v), max(m.data['up_field']['field'].v))
    y = [m.approach2sat_func(i, m.results['ms'].v, m.results['hf_sus'].v, m.results['alpha'].v) for i in x]
    plt.plot(dfp['field'].v, dfp['mag'].v)
    plt.plot(-dfm['field'].v, -dfm['mag'].v)
    plt.plot(-ufm['field'].v, -ufm['mag'].v)
    plt.plot(ufp['field'].v, ufp['mag'].v)
    plt.plot(x, y)
    # plt.xlim([1, 2])
    # plt.ylim([0.000296, 0.000299])
    plt.show()

class Hysteresis(Hys):
    """
    Alias for hys measurement
    """
    pass

if __name__ == '__main__':
    import RockPy

    vsm_file = RockPy.join(RockPy.test_data_path, 'vsm', 'LTPY_527,1a_HYS_VSM#XX[mg]___#TEMP_300_K#STD000.000')
    vftb_file = RockPy.join(RockPy.test_data_path, 'MUCVFTB_test.hys')
    vftb_file = '/Users/mike/Dropbox/Software/RockMagAnalyzer1.1/Examples/example1.hys'
    s = RockPy.Sample(name='test_sample', mass=146.8, mass_unit='mg')
    # m = s.add_measurement(mtype='hys', mfile=vsm_file, machine='vsm')
    m = s.add_measurement(mtype='hys', mfile=vftb_file, machine='vftb')
    m.data['down_field']['mag'] = m.data['down_field']['mag'].v + 1.2e-7
    m.data['up_field']['mag'] = m.data['up_field']['mag'].v + 1.2e-7
    m.correct_center()
    # m.normalizeNEW(reference='mass', ntypes='mag')
    # m.fit_hysteresis(nfunc=2, check=True)
    # m.calc_all()
    # print m.results
    # # m = s.add_measurement(mtype='hys', mfile=vftb_file, machine='vftb')
    # m.correct_hsym()
    # m.correct_vsym()
    # m.calc_all()
    # # m.result_e_delta_t()
    # # m.data_gridding()
    # # m.plt_hysteresis()
    # m.result_hf_sus(method='app2sat', saturation_percent=80)
    # plot_app2sat(m)
    # print m.results
