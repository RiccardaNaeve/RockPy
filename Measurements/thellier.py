# coding=utf-8
__author__ = 'volk'
from Structure.rockpydata import RockPyData
import base
import numpy as np
import scipy as sp
import Structure.data
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import sys
import copy


class Thellier(base.Measurement):
    def __init__(self, sample_obj,
                 mtype, mfile, machine,
                 **options):
        super(Thellier, self).__init__(sample_obj, mtype, mfile, machine)

        # # ## initialize data
        self.standard_parameters['slope'] = {'t_min': 20, 't_max': 700, 'component': 'mag'}

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
        self.all_data = RockPyData(column_names=self.machine_data.float_header, data=data)
        self.all_data.rename_column('step', 'temp')

        nrm_idx = [i for i, v in enumerate(steps) if v == 'nrm']

        # generating the palint data for all steps
        for step in ['nrm', 'trm', 'th', 'pt', 'ac', 'tr', 'ck']:
            idx = [i for i, v in enumerate(steps) if v == step]
            if step in ['th', 'pt']:
                idx.append(nrm_idx[0])
            if len(idx) != 0:
                self.__dict__[step] = self.all_data.filter_idx(idx)  # finding step_idx
                self.__dict__[step].define_alias('m', ( 'x', 'y', 'z'))
                self.__dict__[step].append_columns('mag', self.__dict__[step].magnitude('m'))
                self.__dict__[step].sort('temp')
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

    def format_sushibar(self):
        raise NotImplementedError

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

    def plt_arai(self):
        equal = set(self.th['temp']) & set(self.ptrm['temp'])
        idx = [i for i, v in enumerate(self.th['temp']) if v in equal]
        th = self.th.filter_idx(idx)
        plt.plot(self.ptrm['mag'], th['mag'], '.-', zorder=1)
        plt.grid()
        plt.title('Arai Diagram %s' % (self.sample_obj.name))
        plt.xlabel('NRM remaining [%s]' % ('C'))
        plt.ylabel('pTRM gained [%s]' % ('Am^2'))
        plt.show()


    @property
    def slope(self):
        '''
        helper function that returns the value for slope of arai line fit. If result not available will calculate
        it with standard parameters
        '''
        return self.result_slope()

    @property
    def sigma(self):
        '''
        helper function that returns the value for slope of arai line fit. If result not available will calculate
        it with standard parameters
        '''
        return self.result_sigma()

    @property
    def x_int(self):
        '''
        helper function that returns the value for slope of arai line fit. If result not available will calculate
        it with standard parameters
        '''
        return self.result_x_int()

    @property
    def y_int(self):
        '''
        helper function that returns the value for slope of arai line fit. If result not available will calculate
        it with standard parameters
        '''
        return self.result_y_int()

    @property
    def intensity(self):
        '''
        helper function that returns the value for slope of arai line fit. If result not available will calculate
        it with standard parameters
        '''
        return self.result_b_anc()

    @property
    def sigma_int(self):
        '''
        helper function that returns the value for slope of arai line fit. If result not available will calculate
        it with standard parameters
        '''
        return self.result_sigma_b_anc()

    @property
    def vds(self):
        '''
        helper function that returns the value for slope of arai line fit. If result not available will calculate
        it with standard parameters
        '''
        return self.result_vds()

    def calc_all(self, **parameter):
        parameter['recalc'] = True
        for result_method in self.result_methods:
            getattr(self, 'result_' + result_method)(**parameter)

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


    ''' CALCULATE SECTION '''

    def calculate_slope(self, **parameter):
        """
        calculates the least squares slope for the specified temperature interval

        :param parameter:
        """
        t_min = parameter.get('t_min', self.standard_parameters['slope']['t_min'])
        t_max = parameter.get('t_max', self.standard_parameters['slope']['t_max'])
        component = parameter.get('component', 'mag')

        self.log.info('CALCULATING\t << %s >> arai line fit << t_min=%.1f , t_max=%.1f >>' % (component, t_min, t_max))

        equal_steps = list(set(self.th['temp']) & set(self.ptrm['temp']))
        th_steps = (t_min <= self.th['temp']) & (self.th['temp'] <= t_max)  # True if step between t_min, t_max
        ptrm_steps = (t_min <= self.ptrm['temp']) & (self.ptrm['temp'] <= t_max)  # True if step between t_min, t_max

        th_data = self.th.filter(th_steps)  # filtered data for t_min t_max
        ptrm_data = self.ptrm.filter(ptrm_steps)  # filtered data for t_min t_max

        # filtering for equal variables
        th_idx = [i for i, v in enumerate(th_data['temp']) if v in equal_steps]
        ptrm_idx = [i for i, v in enumerate(ptrm_data['temp']) if v in equal_steps]

        th_data = th_data.filter_idx(th_idx)  # filtered data for equal t(th) & t(ptrm)
        ptrm_data = ptrm_data.filter_idx(ptrm_idx)  # filtered data for equal t(th) & t(ptrm)

        data = RockPyData(['th', 'ptrm'])

        # setting the data
        data['th'] = th_data[component]
        data['ptrm'] = ptrm_data[component]

        slope, sigma, y_int, x_int = data.lin_regress('ptrm', 'th')

        self.results['slope'] = slope
        self.results['sigma'] = sigma
        self.results['y_int'] = y_int
        self.results['x_int'] = x_int

        self.calculation_parameters['slope'] = {'t_min': t_min, 't_max': t_max, 'component': component}

    def calculate_b_anc(self, **parameter):
        b_lab = parameter.get('b_lab')
        self.results['b_anc'] = b_lab * abs(self.results['slope'])
        self.calculation_parameters['b_anc'] = {'b_lab': b_lab}

    def calculate_sigma_b_anc(self, **parameter):
        b_lab = parameter.get('b_lab')
        self.results['sigma_b_anc'] = b_lab * abs(self.results['sigma'])
        self.calculation_parameters['sigma_b_anc'] = {'b_lab': b_lab}

    def calculate_vds(self, **parameter):  # todo move in rockpydata?
        '''
        The vector difference sum of the entire NRM vector :math:`($$\mathbf{NRM}$$)`.

        .. math::

           [ VDS=\left|\mathbf{NRM}_{n_{max}}\right|+\sum\limits_{i=1}^{n_{max}-1}{\left|\mathbf{NRM}_{i+1}-\mathbf{NRM}_{i}\right|}

        where :math:`\left|\mathbf{NRM}_{i}\right|` denotes the length of the NRM vector at the :math:`i^{th}` step.


        :param parameter:
        :return:
        '''
        NRM_t_max = self.th['mag'][-1]
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

        idx = (self.th['temp'] <= t_max) & (t_min <= self.th['temp'])
        data = self.th.filter(idx)
        vd = np.array([np.linalg.norm(i) for i in np.diff(data['m'], axis=0)])
        return vd

    def calculate_x_dash(self, **parameter):
        '''
        :math:`x_0 and :math:`y_0` the x and y points on the Arai plot projected on to the best-ﬁt line. These are
        used to
        calculate the NRM fraction and the length of the best-ﬁt line among other parameters. There are
        multiple ways of calculating :math:`x_0 and :math:`y_0`, below is one example.

        ..math:

          x_i' = \frac{1}{2} \left( x_i + \frac{y_i - Y_{int}}{b}


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

        x_dash = 0.5 * (x[component] + ((y[component] - self.y_int) / self.slope))
        return x_dash

    def calculate_y_dash(self, **parameter):
        '''
        :math:`x_0 and :math:`y_0` the x and y points on the Arai plot projected on to the best-ﬁt line. These are
        used to
        calculate the NRM fraction and the length of the best-ﬁt line among other parameters. There are
        multiple ways of calculating :math:`x_0 and :math:`y_0`, below is one example.

        ..math:

           y_i' = \frac{1}{2} \left( x_i + \frac{y_i - Y_{int}}{b}


        :param parameter:
        :return:
        '''

        t_min = parameter.get('t_min', self.standard_parameters['y_dash']['t_min'])
        t_max = parameter.get('t_max', self.standard_parameters['y_dash']['t_max'])
        component = parameter.get('component', self.standard_parameters['y_dash']['component'])
        self.log.info('CALCULATING\t << %s >> y_dash << t_min=%.1f , t_max=%.1f >>' % (component, t_min, t_max))

        idx = (self.th['temp'] <= t_max) & (t_min <= self.th['temp'])  # filtering for t_min/t_max
        y = self.th.filter(idx)

        idx = (self.ptrm['temp'] <= t_max) & (t_min <= self.ptrm['temp'])
        x = self.ptrm.filter(idx)

        idx = np.array([(ix, iy) for iy, v1 in enumerate(self.ptrm['temp'])
                        for ix, v2 in enumerate(self.th['temp'])
                        if v1 == v2])  # filtering for equal var

        x = x.filter_idx(idx[:, 0])
        y = y.filter_idx(idx[:, 1])

        y_dash = 0.5 * ( y[component] + self.slope * x[component] + self.y_int)

        return y_dash