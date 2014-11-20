# coding=utf-8
__author__ = 'volk'
import numpy as np
import matplotlib.pyplot as plt

from RockPy.Structure.data import RockPyData
import base


class Thellier(base.Measurement):
    # todo format_sushibar
    # todo format_jr6

    def __init__(self, sample_obj,
                 mtype, mfile, machine,
                 **options):
        super(Thellier, self).__init__(sample_obj, mtype, mfile, machine, **options)

        # # ## initialize data
        self.standard_parameters['slope'] = {'t_min': 20, 't_max': 700, 'component': 'mag'}
        self.steps = ['th', 'pt', 'ac', 'tr', 'ck', 'ptrm', 'sum', 'difference']
        self._data = {i : getattr(self, i) for i in self.steps[:5]}
        for i in self.standard_parameters:
            if self.standard_parameters[i] is None:
                self.standard_parameters[i] = self.standard_parameters['slope']

    def format_cryomag(self):
        '''
        Formats cryomag output dictionary into thellier measurement data format.

        Beware: NRM step has to be called NRM or TH

        :return:
        '''
        steps = self.machine_data.steps
        data = self.machine_data.get_float_data()
        row_labels = [v + '[%.0f]' % (data[i, 0]) for i, v in enumerate(steps)]

        self.all_data = RockPyData(column_names=self.machine_data.float_header,
                                   data=data,
                                   row_names=row_labels)
        self.all_data.rename_column('step', 'temp')
        self.all_data.append_columns('time', self.machine_data.get_time_data())
        nrm_idx = [i for i, v in enumerate(steps) if v == 'nrm']
        self.machine_data.get_time_data()
        # generating the palint data for all steps
        for step in ['nrm', 'th', 'pt', 'ac', 'tr', 'ck']:
            idx = [i for i, v in enumerate(steps) if v == step]
            if step in ['th', 'pt']:
                idx.append(nrm_idx[0])
            if len(idx) != 0:
                self.__dict__[step] = self.all_data.filter_idx(idx)  # finding step_idx
                self.__dict__[step] = self.__dict__[step].eliminate_duplicate_variable_rows(substfunc='last')
                self.__dict__[step].define_alias('m', ( 'x', 'y', 'z'))
                self.__dict__[step] = self.__dict__[step].append_columns('mag', self.__dict__[step].magnitude('m'))
                self.__dict__[step] = self.__dict__[step].sort('temp')
            else:
                self.__dict__[step] = None


        # ## PTRM
        self.ptrm = self.pt - self.th
        self.ptrm.define_alias('m', ( 'x', 'y', 'z'))
        self.ptrm['mag'] = self.ptrm.magnitude('m')
        # ## SUM
        self.sum = self.th + self.ptrm
        self.sum.define_alias('m', ( 'x', 'y', 'z'))
        self.sum['mag'] = self.sum.magnitude('m')
        # ## DIFFERENCE
        self.difference = self.th - self.ptrm
        self.difference.define_alias('m', ( 'x', 'y', 'z'))
        self.difference['mag'] = self.sum.magnitude('m')


    def _get_idx_tmin_tmax(self, step, t_min, t_max):
        idx = (getattr(self, step)['temp'].v <= t_max) & (t_min <= getattr(self, step)['temp'].v)
        return idx

    def _get_idx_equal_val(self, step_a, step_b, key='temp'):

        idx = np.array([(ix, iy) for iy, v1 in enumerate(getattr(self, step_a)[key].v)
                        for ix, v2 in enumerate(getattr(self, step_b)[key].v)
                        if v1 == v2])
        return idx

    def correct_last_step(self):
        idx = [len(self.th['temp'].v) - 1]
        last_step = self.th.filter_idx(idx)
        self.th = self.th - last_step
        print self.th

    # ## plotting functions
    def plt_dunlop(self):
        plt.plot(self.th['temp'], self.th['mag'], '.-', zorder=1)
        # plt.plot(self.ptrm['temp'], self.ptrm['moment'], '.-', zorder=1)
        plt.plot(self.ptrm['temp'], self.ptrm['mag'], '.-', zorder=1)
        plt.plot(self.sum['temp'], self.sum['mag'], '.--', zorder=1)
        plt.plot(self.tr['temp'], self.tr['mag'], 's')
        plt.grid()
        plt.title('Dunlop Plot %s' % (self.sample_obj.name))
        plt.xlabel('Temperature [%s]' % ('C'))
        plt.ylabel('Moment [%s]' % ('Am^2'))
        plt.xlim([min(self.th['temp']), max(self.th['temp'])])
        plt.show()

    def plt_arai(self, **options):
        equal = set(self.th['temp']) & set(self.ptrm['temp'])
        idx = [i for i, v in enumerate(self.th['temp']) if v in equal]
        th = self.th.filter_idx(idx)
        plt.plot(self.ptrm['mag'], th['mag'], '.-', zorder=1)
        plt.grid()
        plt.title('Arai Diagram %s' % (self.sample_obj.name))
        plt.xlabel('NRM remaining [%s]' % ('C'))
        plt.ylabel('pTRM gained [%s]' % ('Am^2'))
        plt.show()

    def delete_temp(self, temp):
        for step in self.steps:
            o_len = len(getattr(self, step)['temp'].v)
            idx = [i for i, v in enumerate(getattr(self, step)['temp'].v) if v != temp]
            if o_len - len(idx) != 0:
                self.log.info(
                    'DELETING << %i, %s >> entries for << %.2f >> temperature' % (o_len - len(idx), step, temp))
                self.__dict__[step] = getattr(self, step).filter_idx(idx)
            else:
                self.log.debug('UNABLE to find entriy for << %s, %.2f >> temperature' % (step, temp))


    ''' RESULT SECTION '''

    def result_slope(self, t_min=None, t_max=None, component=None, recalc=False):
        '''
        Gives result for calculate_slope(t_min, t_max), returns slope value if not calculated already
        '''
        parameter = {'t_min': t_min,
                     't_max': t_max,
                     'component': component,
        }

        self.calc_result(parameter, recalc)
        return self.results['slope']

    def result_n(self, t_min=None, t_max=None, component=None, recalc=False):
        '''
        Gives result for calculate_slope(t_min, t_max), returns slope value if not calculated already
        '''
        parameter = {'t_min': t_min,
                     't_max': t_max,
                     'component': component,
        }

        self.calc_result(parameter, recalc, force_caller='slope')
        return self.results['n']

    def result_sigma(self, t_min=None, t_max=None, component=None, recalc=False, **options):
        parameter = {'t_min': t_min,
                     't_max': t_max,
                     'component': component,
        }

        self.calc_result(parameter, recalc, force_caller='slope')
        return self.results['sigma']

    def result_x_int(self, t_min=None, t_max=None, component=None, recalc=False, **options):
        parameter = {'t_min': t_min,
                     't_max': t_max,
                     'component': component,
        }

        self.calc_result(parameter, recalc, force_caller='slope')
        return self.results['x_int']

    def result_y_int(self, t_min=None, t_max=None, component=None, recalc=False, **options):
        parameter = {'t_min': t_min,
                     't_max': t_max,
                     'component': component,
        }

        self.calc_result(parameter, recalc, force_caller='slope')
        return self.results['y_int']

    def result_b_anc(self, t_min=None, t_max=None, component=None, b_lab=35.0, recalc=False, **options):
        parameter_a = {'t_min': t_min,
                       't_max': t_max,
                       'component': component,
        }
        parameter_b = {'b_lab': b_lab}

        self.calc_result(parameter_a, recalc,
                         force_caller='slope')  # force caller because if not calculate_b_anc will be called
        self.calc_result(parameter_b, recalc)
        return self.results['b_anc']

    def result_sigma_b_anc(self, t_min=None, t_max=None, component=None, b_lab=35.0, recalc=False, **options):
        parameter_a = {'t_min': t_min,
                       't_max': t_max,
                       'component': component,
        }

        parameter_b = {'b_lab': b_lab}
        self.calc_result(parameter_a, recalc, force_caller='slope')
        self.calc_result(parameter_b, recalc)
        return self.results['sigma_b_anc']

    def result_vds(self, t_min=None, t_max=None, recalc=False, **options):
        parameter = {'t_min': t_min,
                     't_max': t_max,
        }
        self.calc_result(parameter, recalc)
        return self.results['vds']

    def result_f(self, t_min=None, t_max=None, recalc=False, **options):
        parameter = {'t_min': t_min,
                     't_max': t_max,
        }
        self.calc_result(parameter, recalc)
        return self.results['f']

    def result_f_vds(self, t_min=None, t_max=None, recalc=False, **options):
        parameter = {'t_min': t_min,
                     't_max': t_max,
        }
        self.calc_result(parameter, recalc)
        return self.results['f_vds']

    def result_frac(self, t_min=None, t_max=None, recalc=False, **options):
        parameter = {'t_min': t_min,
                     't_max': t_max,
        }
        self.calc_result(parameter, recalc)
        return self.results['frac']

    def result_beta(self, t_min=None, t_max=None, recalc=False, **options):
        parameter = {'t_min': t_min,
                     't_max': t_max,
        }
        self.calc_result(parameter, recalc)
        return self.results['beta']

    def result_g(self, t_min=None, t_max=None, recalc=False, **options):
        parameter = {'t_min': t_min,
                     't_max': t_max,
        }
        self.calc_result(parameter, recalc)
        return self.results['g']

    def result_gap_max(self, t_min=None, t_max=None, recalc=False, **options):
        parameter = {'t_min': t_min,
                     't_max': t_max,
        }
        self.calc_result(parameter, recalc)
        return self.results['gap_max']

    def result_q(self, t_min=None, t_max=None, recalc=False, **options):
        parameter = {'t_min': t_min,
                     't_max': t_max,
        }
        self.calc_result(parameter, recalc)
        return self.results['q']

    def result_w(self, t_min=None, t_max=None, recalc=False, **options):
        parameter = {'t_min': t_min,
                     't_max': t_max,
        }
        self.calc_result(parameter, recalc)
        return self.results['w']

    ''' CALCULATE SECTION '''

    def calculate_slope(self, **parameter):
        """
        calculates the least squares slope for the specified temperature interval

        :param parameter:

        """
        t_min = parameter.get('t_min', self.standard_parameters['slope']['t_min'])
        t_max = parameter.get('t_max', self.standard_parameters['slope']['t_max'])
        component = parameter.get('component', self.standard_parameters['slope']['component'])

        self.log.info('CALCULATING\t << %s >> arai line fit << t_min=%.1f , t_max=%.1f >>' % (component, t_min, t_max))

        equal_steps = list(set(self.th['temp'].v) & set(self.ptrm['temp'].v))
        th_steps = (t_min <= self.th['temp'].v) & (self.th['temp'].v <= t_max)  # True if step between t_min, t_max
        ptrm_steps = (t_min <= self.ptrm['temp'].v) & (
            self.ptrm['temp'].v <= t_max)  # True if step between t_min, t_max

        th_data = self.th.filter(th_steps)  # filtered data for t_min t_max
        ptrm_data = self.ptrm.filter(ptrm_steps)  # filtered data for t_min t_max

        # filtering for equal variables
        th_idx = [i for i, v in enumerate(th_data['temp'].v) if v in equal_steps]
        ptrm_idx = [i for i, v in enumerate(ptrm_data['temp'].v) if v in equal_steps]

        th_data = th_data.filter_idx(th_idx)  # filtered data for equal t(th) & t(ptrm)
        ptrm_data = ptrm_data.filter_idx(ptrm_idx)  # filtered data for equal t(th) & t(ptrm)

        data = RockPyData(['th', 'ptrm'])

        # setting the data
        data['th'] = th_data[component].v
        data['ptrm'] = ptrm_data[component].v

        slope, sigma, y_int, x_int = data.lin_regress('ptrm', 'th')
        self.results['slope'] = slope
        # self.results['slope']= sigma
        self.results['sigma'] = sigma
        self.results['y_int'] = y_int
        self.results['x_int'] = x_int
        self.results['n'] = len(th_data[component].v)

        self.calculation_parameters['slope'] = {'t_min': t_min, 't_max': t_max, 'component': component}

    def calculate_b_anc(self, **parameter):
        """
        calculates the :math:`B_{anc}` value for a given lab field in the specified temperature interval.

        :param parameter:

        """

        b_lab = parameter.get('b_lab')
        self.results['b_anc'] = b_lab * abs(self.results['slope'].v)
        self.calculation_parameters['b_anc'] = {'b_lab': b_lab}

    def calculate_sigma_b_anc(self, **parameter):
        """
        calculates the standard deviation of the least squares slope for the specified temperature interval

        :param parameter:

        """

        b_lab = parameter.get('b_lab')
        self.results['sigma_b_anc'] = b_lab * abs(self.results['sigma'].v)
        self.calculation_parameters['sigma_b_anc'] = {'b_lab': b_lab}

    def calculate_vds(self, **parameter):  # todo move in rockpydata?
        '''
        The vector difference sum of the entire NRM vector :math:`\\mathbf{NRM}`.

        .. math::

           VDS=\\left|\\mathbf{NRM}_{n_{max}}\\right|+\\sum\\limits_{i=1}^{n_{max}-1}{\\left|\\mathbf{NRM}_{i+1}-\\mathbf{NRM}_{i}\\right|}

        where :math:`\\left|\\mathbf{NRM}_{i}\\right|` denotes the length of the NRM vector at the :math:`i^{th}` step.


        :param parameter:
        :return:

        '''
        NRM_t_max = self.th['mag'].v[-1]
        NRM_sum = np.sum(self.calculate_vd(**parameter))
        self.results['vds'] = NRM_t_max + NRM_sum

    def calculate_vd(self, **parameter):  # todo move in rockpydata?
        '''
        Vector differences

        :param parameter:
        :return:

        '''
        t_min = parameter.get('t_min', self.standard_parameters['vd']['t_min'])
        t_max = parameter.get('t_max', self.standard_parameters['vd']['t_max'])

        idx = (self.th['temp'].v <= t_max) & (t_min <= self.th['temp'].v)
        data = self.th.filter(idx)
        vd = np.array([np.linalg.norm(i) for i in np.diff(data['m'].v, axis=0)])
        return vd

    def calculate_x_dash(self, **parameter):
        '''

        :math:`x_0 and :math:`y_0` the x and y points on the Arai plot projected on to the best-ﬁt line. These are
        used to
        calculate the NRM fraction and the length of the best-ﬁt line among other parameters. There are
        multiple ways of calculating :math:`x_0 and :math:`y_0`, below is one example.

        ..math:

          x_i' = \\frac{1}{2} \\left( x_i + \\frac{y_i - Y_{int}}{b}


        :param parameter:
        :return:

        '''

        t_min = parameter.get('t_min', self.standard_parameters['x_dash']['t_min'])
        t_max = parameter.get('t_max', self.standard_parameters['x_dash']['t_max'])
        component = parameter.get('component', self.standard_parameters['x_dash']['component'])
        self.log.info('CALCULATING\t << %s >> x_dash << t_min=%.1f , t_max=%.1f >>' % (component, t_min, t_max))

        idx = (self.th['temp'] <= t_max) & (t_min <= self.th['temp'])  # filtering for t_min/t_max
        y = self.th.filter(idx)

        idx = (self.ptrm['temp'] <= t_max) & (t_min <= self.ptrm['temp'])
        x = self.ptrm.filter(idx)

        idx = np.array([(ix, iy) for iy, v1 in enumerate(self.ptrm['temp'])
                        for ix, v2 in enumerate(self.th['temp'])
                        if v1 == v2])  # filtering for equal var

        x = x.filter_idx(idx[:, 0])
        y = y.filter_idx(idx[:, 1])

        x_dash = 0.5 * (
            x[component] + ((y[component] - self.result_y_int(**parameter)) / self.result_slope(**parameter)))
        return x_dash

    def calculate_y_dash(self, **parameter):
        '''

        :math:`x_0 and :math:`y_0` the x and y points on the Arai plot projected on to the best-ﬁt line. These are
        used to
        calculate the NRM fraction and the length of the best-ﬁt line among other parameters. There are
        multiple ways of calculating :math:`x_0 and :math:`y_0`, below is one example.

        ..math:

           y_i' = \\frac{1}{2} \\left( x_i + \\frac{y_i - Y_{int}}{b}


        :param parameter:
        :return:

        '''
        t_min = parameter.get('t_min', self.standard_parameters['y_dash']['t_min'])
        t_max = parameter.get('t_max', self.standard_parameters['y_dash']['t_max'])
        component = parameter.get('component', self.standard_parameters['y_dash']['component'])

        self.log.info('CALCULATING\t << %s >> y_dash << t_min=%.1f , t_max=%.1f >>' % (component, t_min, t_max))

        idx = self._get_idx_tmin_tmax('th', t_min, t_max)  # filtering for t_min/t_max
        y = self.th.filter(idx)

        idx = self._get_idx_tmin_tmax('ptrm', t_min, t_max)  # filtering for t_min/t_max
        x = self.ptrm.filter(idx)

        idx = self._get_idx_equal_val('th', 'ptrm', 'temp')  # filtering for equal var

        x = x.filter_idx(idx[:, 0])
        y = y.filter_idx(idx[:, 1])

        y_dash = 0.5 * (
            y[component].v + self.result_slope(**parameter).v * x[component].v + self.result_y_int(**parameter).v)
        return y_dash

    def calculate_delta_x_dash(self, **parameter):
        '''

        ∆x0 and ∆y0 are TRM and NRM lengths of the best-ﬁt line on the Arai plot, respectively.

        '''
        x_dash = self.calculate_x_dash(**parameter)
        out = abs(np.max(x_dash)) - np.min(x_dash)
        return out

    def calculate_delta_y_dash(self, **parameter):
        '''

        ∆x0 and ∆y0 are TRM and NRM lengths of the best-ﬁt line on the Arai plot, respectively.

        '''
        y_dash = self.calculate_y_dash(**parameter)
        out = abs(np.max(y_dash)) - np.min(y_dash)
        return out

    def calculate_f(self, **parameter):
        """

        The remanence fraction, f, was defined by Coe et al. (1978) as:

        .. math::

           f =  \\frac{\\Delta y^T}{y_0}

        where :math:`\Delta y^T` is the length of the NRM/TRM segment used in the slope calculation.


        :param parameter:
        :return:

        """

        self.log.debug('CALCULATING\t f parameter')
        delta_y_dash = self.calculate_delta_y_dash(**parameter)
        y_int = self.results['y_int'].v
        self.results['f'] = delta_y_dash / abs(y_int)

    def calculate_f_vds(self, **parameter):
        """

        NRM fraction used for the best-fit on an Arai diagram calculated as a vector difference sum (Tauxe and Staudigel, 2004).

        .. math::

           f_{VDS}=\\frac{\Delta{y'}}{VDS}

        :param parameter:
        :return:

        """
        delta_y = self.calculate_delta_y_dash(**parameter)
        VDS = self.result_vds(**parameter).v
        self.results['f_vds'] = delta_y / VDS

    def calculate_frac(self, **parameter):
        """

        NRM fraction used for the best-fit on an Arai diagram determined entirely by vector difference sum
        calculation (Shaar and Tauxe, 2013).

        .. math::

            FRAC=\\frac{\sum\limits_{i=start}^{end-1}{ \left|\\mathbf{NRM}_{i+1}-\\mathbf{NRM}_{i}\\right| }}{VDS}

        :param parameter:
        :return:

        """

        NRM_sum = np.sum(np.fabs(self.calculate_vd(**parameter)))
        VDS = self.result_vds(**parameter).v
        self.results['frac'] = NRM_sum / VDS

    def calculate_beta(self, **parameter):
        """

        :math`\beta` is a measure of the relative data scatter around the best-fit line and is the ratio of the
        standard error of the slope to the absolute value of the slope (Coe et al., 1978)

        .. math::

           \\beta = \\frac{\sigma_b}{|b|}


        :param parameters:
        :return:

        """

        slope = self.result_slope(**parameter).v
        sigma = self.result_sigma(**parameter).v
        self.results['beta'] = sigma / abs(slope)

    def calculate_g(self, **parameter):
        """

        Gap factor: A measure of the gap between the points in the chosen segment of the Arai plot and the least-squares
        line. :math:`g` approaches :math:`(n-2)/(n-1)` (close to unity) as the points are evenly distributed.

        """
        y_dash = self.calculate_y_dash(**parameter)
        delta_y_dash = self.calculate_delta_y_dash(**parameter)
        y_dash_diff = [(y_dash[i + 1] - y_dash[i]) ** 2 for i in range(len(y_dash) - 1)]
        y_sum_dash_diff_sq = np.sum(y_dash_diff, axis=0)

        self.results['g'] = 1 - y_sum_dash_diff_sq / delta_y_dash ** 2

    def calculate_gap_max(self, **parameter):
        """

        The gap factor defined above is measure of the average Arai plot point spacing and may not represent extremes
        of spacing. To account for this Shaar and Tauxe (2013)) proposed :math:`GAP_{\text{MAX}}`, which is the maximum
        gap between two points determined by vector arithmetic.

        .. math::
           GAP_{\\text{MAX}}=\\frac{\\max{\{\\left|\\mathbf{NRM}_{i+1}-\\mathbf{NRM}_{i}\\right|\}}_{i=start, \\ldots, end-1}}
           {\\sum\\limits_{i=start}^{end-1}{\\left|\\mathbf{NRM}_{i+1}-\\mathbf{NRM}_{i}\\right|}}

        :return:

        """
        vd = self.calculate_vd(**parameter)
        max_vd = np.max(vd)
        sum_vd = np.sum(vd)
        self.results['gap_max'] = max_vd / sum_vd

    def calculate_q(self, **parameter):
        """

        The quality factor (:math:`q`) is a measure of the overall quality of the paleointensity estimate and combines
        the relative scatter of the best-fit line, the NRM fraction and the gap factor (Coe et al., 1978).

        .. math::
           q=\\frac{\\left|b\\right|fg}{\\sigma_b}=\\frac{fg}{\\beta}

        :param parameter:
        :return:

        """
        self.log.debug('CALCULATING\t quality parameter')

        beta = self.result_beta(**parameter).v
        f = self.result_f(**parameter).v
        gap = self.result_g(**parameter).v

        self.results['q'] = (f * gap) / beta

    def calculate_w(self, **parameter):
        """
        Weighting factor of Prévot et al. (1985). It is calculated by

        .. math::

           w=\\frac{q}{\\sqrt{n-2}}

        Originally it is :math:`w=\\frac{fg}{s}`, where :math:`s^2` is given by

        .. math::

           s^2 = 2+\\frac{2\\sum\\limits_{i=start}^{end}{(x_i-\\bar{x})(y_i-\\bar{y})}}
              {\\left( \\sum\\limits_{i=start}^{end}{(x_i- \\bar{x})^{\\frac{1}{2}}}
              \\sum\\limits_{i=start}^{end}{(y_i-\\bar{y})^2} \\right)^2}

        It can be noted, however, that :math:`w` can be more readily calculated as:

        .. math::

           w=\\frac{q}{\\sqrt{n-2}}

        :param parameter:
        """
        q = self.result_q(**parameter).v
        n = self.result_n(**parameter).v
        self.results['w'] = q / np.sqrt((n - 2))

    ''' EXPORT SECTION '''

    def export_tdt(self):
        raise NotImplementedError()