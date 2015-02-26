__author__ = 'volk'
import numpy as np
import matplotlib.pyplot as plt
from copy import deepcopy
from RockPy.Structure.data import RockPyData
import base
import RockPy
import time
from RockPy.Functions import general


class Thellier(base.Measurement):
    # todo format_sushibar
    # todo format_jr6
    _standard_parameter = {'slope': {'t_min': 20, 't_max': 700, 'component': 'mag'}}

    @classmethod
    def simulate(cls, sample_obj, **parameter):
        """
        return simulated instance of measurement depending on parameters
        """
        b_lab = parameter.get('b_lab', 35.0)
        b_anc = parameter.get('b_anc', 35.0)

        aniso = parameter.get('aniso', [[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        check_freq = parameter.get('check_freq', 2)
        # temps = parameter.get('temps', [20, 300, 450, 490, 500, 510, 515, 520, 525, 530, 535, 540, 545, 550, 560])
        temps = parameter.get('temps', [20] + range(100, 650, 25))
        max_moment = parameter.get('max_moment', len(temps)/np.sqrt(3))
        th_steps = []
        pt_steps = []

        ac_steps = []
        ck_steps = []
        tr_steps = []
        # checks
        n = 0
        for i, v in enumerate(temps):
            th_steps.append([n, v])
            n += 1
            if (i - 1) % check_freq == 0 and len(temps) - 2 >= i >= check_freq:
                ck_steps.append([n, temps[i - check_freq], temps[i]])
                n += 1
            pt_steps.append([n, v])
            n += 1
            if (i - 1) % check_freq == 0 and len(temps) - 2 >= i >= check_freq:
                ac_steps.append([n, temps[i - check_freq], temps[i]])
                n += 1
            if (i - 1) % check_freq == 0 and len(temps) - 2 >= i >= check_freq:
                tr_steps.append([n, temps[i]])
                n += 1

        th_steps = np.array(th_steps)
        pt_steps = np.array(pt_steps)#[1:]
        ac_steps = np.array(ac_steps)
        ck_steps = np.array(ck_steps)
        tr_steps = np.array(tr_steps)

        """ Generate data """

        mdata = {'th': None, 'pt': None}  # , 'ac': None, 'ck': None, 'tr': None}  #initialize

        th_data = np.linspace(max_moment, 0, len(temps)).T

        t = [time.clock() for i in range(len(th_data))]
        mdata['th'] = RockPyData(column_names=['temp', 'x', 'y', 'z', 'sm', 'time'])
        mdata['pt'] = RockPyData(column_names=['temp', 'x', 'y', 'z', 'sm', 'time'])
        mdata['ac'] = RockPyData(column_names=['temp', 'x', 'y', 'z', 'sm', 'time'])
        mdata['ck'] = RockPyData(column_names=['temp', 'x', 'y', 'z', 'sm', 'time'])
        mdata['tr'] = RockPyData(column_names=['temp', 'x', 'y', 'z', 'sm', 'time'])

        mdata['th']['temp'] = th_steps[:, 1]
        mdata['th']['time'] = th_steps[:, 0]
        mdata['th']['x'] = th_data
        mdata['th']['y'] = th_data
        mdata['th']['z'] = th_data

        mdata['pt']['temp'] = pt_steps[:, 1]
        mdata['pt']['time'] = pt_steps[:, 0]
        mdata['pt']['x'] = np.ones(len(pt_steps[:, 0]))* max_moment
        mdata['pt']['y'] = np.ones(len(pt_steps[:, 0]))* max_moment
        mdata['pt']['z'] = np.ones(len(pt_steps[:, 0]))* max_moment

        mdata['nrm'] = mdata['th'].filter_idx([0])

        ck_index = [i for i, v in enumerate(mdata['pt']['temp'].v) if v in ck_steps[:, 1]]
        ck_th_index = [i for i, v in enumerate(mdata['th']['temp'].v) if v in ck_steps[:, 2]]
        ck_thj_index = [i for i, v in enumerate(mdata['th']['temp'].v) if v in ck_steps[:, 1]]

        pt_copy = mdata['pt'].filter_idx(ck_index)
        thi_copy = mdata['th'].filter_idx(ck_th_index)
        thj_copy = mdata['th'].filter_idx(ck_thj_index)

        mdata['ck'] = thi_copy
        mdata['ck']['x'] = thi_copy['x'].v + (pt_copy['x'].v - thj_copy['x'].v )
        mdata['ck']['y'] = thi_copy['y'].v + (pt_copy['y'].v - thj_copy['y'].v )
        mdata['ck']['z'] = thi_copy['z'].v + (pt_copy['z'].v - thj_copy['z'].v )
        mdata['ck']['time'] = ck_steps[:, 0]
        mdata['ck']['temp'] = ck_steps[:, 1]

        tr_index = [i for i, v in enumerate(mdata['th']['temp'].v) if v in tr_steps[:, 1]]
        mdata['tr'] = mdata['th'].filter_idx(tr_index)
        mdata['tr']['time'] = tr_steps[:, 0]

        ac_pt_index = [i for i, v in enumerate(mdata['pt']['temp'].v) if v in ac_steps[:, 2]]
        ac_th_index = [i for i, v in enumerate(mdata['th']['temp'].v) if v in ac_steps[:, 1]]

        pt_copy = mdata['pt'].filter_idx(ac_pt_index)
        thi_copy = mdata['th'].filter_idx(ac_th_index)

        mdata['ac'] = pt_copy
        mdata['ac']['x'] = (pt_copy['x'].v - (max_moment - thi_copy['x'].v))
        mdata['ac']['y'] = (pt_copy['y'].v - (max_moment - thi_copy['y'].v))
        mdata['ac']['z'] = (pt_copy['z'].v - (max_moment - thi_copy['z'].v))
        mdata['ac']['time'] = ac_steps[:, 0]
        mdata['ac']['temp'] = ac_steps[:, 1]

        for dtype in mdata:
            for d in ['x', 'y','z']:
                mdata[dtype][d] = mdata[dtype][d].v + np.random.normal(0.0, 0.1, len(mdata[dtype][d].v))
                mdata[dtype][d] = np.round(mdata[dtype][d].v)
            mdata[dtype].define_alias('m', ( 'x', 'y', 'z'))
            mdata[dtype] = mdata[dtype].append_columns('mag', mdata[dtype].magnitude('m'))

        return cls(sample_obj, mtype='thellier', mfile=None, mdata=mdata, machine='simulation', **parameter)


    def __init__(self, sample_obj,
                 mtype, mfile, machine,
                 **options):


        # # ## initialize data
        self.steps = ['nrm', 'th', 'pt', 'ac', 'tr', 'ck', 'ptrm', 'sum', 'difference']
        # self._data = {}

        super(Thellier, self).__init__(sample_obj, mtype, mfile, machine, **options)
        self.reset__data()

    @property
    def standard_parameter(self):
        out = {}
        for i in self._standard_parameter:
            out[i] = {}
            if self._standard_parameter[i] is None:
                out[i].update(Thellier._standard_parameter['slope'])
            else:
                out[i].update(self._standard_parameter)
        return out

    def reset__data(self, recalc_m=True):
        self._data.update({'ptrm': self._ptrm(recalc_m)})
        self._data.update({'sum': self._sum(recalc_m)})
        self._data.update({'difference': self._difference(recalc_m)})
        # self._data = {i: getattr(self, i) for i in self.steps}
        # for i in self.data:
        # print i
        # print self.data[i]

    @property
    def data(self):
        if not 'ptrm' in self._data.keys():
            self.reset__data()
        return self._data

    @data.setter
    def data(self, data_dict):
        for dtype in data_dict:
            setattr(self, dtype, data_dict[dtype])
        if not 'ptrm' in data_dict:
            self.reset__data()

    def format_cryomag(self):
        """
        Formats cryomag output dictionary into thellier measurement data format.

        Beware: NRM step has to be called NRM or TH

        :return:
        """
        steps = self.machine_data.steps
        data = self.machine_data.get_float_data()
        row_labels = [v + '[%.0f]' % (data[i, 0]) for i, v in enumerate(steps)]

        self.all_data = RockPyData(column_names=self.machine_data.float_header,
                                   data=data,
                                   row_names=row_labels)

        self.all_data.rename_column('step', 'temp')
        self.all_data = self.all_data.append_columns('time', self.machine_data.get_time_data())
        nrm_idx = [i for i, v in enumerate(steps) if v == 'nrm']
        self.machine_data.get_time_data()
        # generating the palint data for all steps
        for step in ['nrm', 'th', 'pt', 'ac', 'tr', 'ck']:
            idx = [i for i, v in enumerate(steps) if v == step]
            if step in ['th', 'pt']:
                idx.append(nrm_idx[0])
            if step == 'nrm' and len(idx) == 0:
                idx = [i for i, v in enumerate(steps) if v == 'th'][0]
            if len(idx) != 0:
                rp_data = self.all_data.filter_idx(idx)  # finding step_idx
                rp_data = rp_data.eliminate_duplicate_variable_rows(substfunc='last')
                rp_data.define_alias('m', ( 'x', 'y', 'z'))
                rp_data = rp_data.append_columns('mag', rp_data.magnitude('m'))
                rp_data = rp_data.sort('temp')
                rp_data.define_alias('variable', 'temp')
                self._data.update({step: rp_data})
            else:
                self._data.update({step: None})
        self.reset__data()

    def format_generic(self):
        for step in ['nrm', 'th', 'pt', 'ac', 'tr', 'ck']:
            self._data.update({step: None})

    def _ptrm(self, recalc_m=True):
        idx = self._get_idx_equal_val('pt', 'th')

        pt = self._data['pt'].filter_idx(idx[:, 0])
        th = self._data['th'].filter_idx(idx[:, 1])

        ptrm = pt - th
        row_labels = ['ptrm[%i]'%i for i in pt['temp'].v]
        ptrm['time'] = pt['time'].v  # copy old pt times into ptrm
        if recalc_m:
            ptrm.define_alias('m', ( 'x', 'y', 'z'))
            if not 'mag' in ptrm.column_names:
                ptrm = ptrm.append_columns('mag', ptrm.magnitude('m'))
            ptrm['mag'] = ptrm.magnitude('m')
        ptrm._row_names = row_labels
        return ptrm

    def _sum(self, recalc_m=True):
        idx = self._get_idx_equal_val('pt', 'th')
        pt = self._data['pt'].filter_idx(idx[:, 0])
        th = self._data['th'].filter_idx(idx[:, 1])
        pt_th_sum = th + pt - th
        if recalc_m:
            pt_th_sum.define_alias('m', ( 'x', 'y', 'z'))
            if not 'mag' in pt_th_sum.column_names:
                pt_th_sum = pt_th_sum.append_columns('mag', pt_th_sum.magnitude('m'))
            pt_th_sum['mag'] = pt_th_sum.magnitude('m')
        return pt_th_sum

    def _difference(self, recalc_m=True):
        idx = self._get_idx_equal_val('pt', 'th')
        pt = self._data['pt'].filter_idx(idx[:, 0])
        th = self._data['th'].filter_idx(idx[:, 1])
        ptrm = pt - th
        difference = th - ptrm
        if recalc_m:
            difference.define_alias('m', ( 'x', 'y', 'z'))
            if not 'mag' in difference.column_names:
                difference = ptrm.append_columns('mag', difference.magnitude('m'))
            else:
                difference['mag'] = difference.magnitude('m')
        return difference

    def _get_idx_tmin_tmax(self, step, t_min, t_max):
        idx = (getattr(self, step)['temp'].v <= t_max) & (t_min <= getattr(self, step)['temp'].v)
        return idx

    def _get_idx_equal_val(self, step_x, step_y, key='temp'):

        idx = np.array([(xi, yi) for xi, v1 in enumerate(self._data[step_x][key].v)
                        for yi, v2 in enumerate(self._data[step_y][key].v)
                        if v1 == v2])
        return idx

    def _get_idx_step_var_val(self, step, var, val, *args):
        """
        returns the index of the closest value with the variable(var) and the step(step) to the value(val)

        option: inverse:
           returns all indices except this one

        """
        out = [np.argmin(abs(self.data[step][var].v - val))]
        return out

    def correct_step(self, step='th', var='variable', val='last', initial_state=True):
        """
        corrects the remaining moment from the last th_step

        :param step:
        :param var:
        :param val:
        :param initial_state: also corrects the iinitial state if one exists
        """

        try:
            calc_data = self.data[step]
        except KeyError:
            self.log.error('REFERENCE << %s >> can not be found ' % (step))

        if val == 'last':
            val = calc_data[var].v[-1]
        if val == 'first':
            val = calc_data[var].v[0]

        idx = self._get_idx_step_var_val(step=step, var=var, val=val)

        correction = self.th.filter_idx(idx)  # correction step
        for dtype in ['nrm','th','pt','ac','ck','tr']:
            # store variables so calculation does not affect
            # vars = self.data[dtype]['temp'].v
            # calculate correction
            self._data[dtype]['m'] = self._data[dtype]['m'].v - correction['m'].v
            # refill variables with original data
            # self.data[dtype]['temp'] = vars
            # recalc mag for safety
            self.data[dtype]['mag'] = self.data[dtype].magnitude(('x', 'y', 'z'))
        self.reset__data()

        if self.initial_state and initial_state:
            for dtype in self.initial_state.data:
                self.initial_state.data[dtype]['m'] = self.initial_state.data[dtype]['m'].v - correction['m'].v
                self.initial_state.data[dtype]['mag'] = self.initial_state.data[dtype].magnitude(('x', 'y', 'z'))
        return self

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
        plt.ylabel('Moment [%s]' % ('Am2'))
        plt.xlim([min(self.th['temp']), max(self.th['temp'])])
        plt.show()

    def plt_arai(self, **options):
        equal = set(self.th['temp'].v) & set(self.ptrm['temp'].v)
        idx = [i for i, v in enumerate(self.th['temp'].v) if v in equal]
        th = self.th.filter_idx(idx)
        plt.plot(self.ptrm['mag'].v, th['mag'].v, '.-', zorder=1)
        plt.plot([min(self.ptrm['mag'].v), max(self.ptrm['mag'].v)],
                 self.result_slope().v * np.array(
                     [min(self.ptrm['mag'].v), max(self.ptrm['mag'].v)]) + self.result_y_int().v, '--')
        plt.grid()
        plt.title('Arai Diagram %s' % (self.sample_obj.name))
        plt.xlabel('NRM remaining [%s]' % ('C'))
        plt.ylabel('pTRM gained [%s]' % ('Am2'))
        plt.show()

    def delete_temp(self, temp):
        for step in self.steps:
            o_len = len(getattr(self, step)['temp'].v)
            idx = [i for i, v in enumerate(getattr(self, step)['temp'].v) if v != temp]
            if o_len - len(idx) != 0:
                self.log.info(
                    'DELETING << %i, %s >> entries for << %.2f >> temperature' % (o_len - len(idx), step, temp))
                setattr(self, step, getattr(self, step).filter_idx(idx))
            else:
                self.log.debug('UNABLE to find entriy for << %s, %.2f >> temperature' % (step, temp))


    """ RESULT SECTION """

    """
    Arai plot statistics
    ====================
    
    A note on data indexing
    +++++++++++++++++++++++
        
    Statistic: :math:`i` and :math:`n_{max}`
    
    The index :math:`i` is used to denote the :math:`i^{th}` temperature step of the paleointensity experiment.
    :math:`i` is used to index Arai plot data (e.g., :math:`x_i`, or :math:`y_i`) and ranges from :math:`i=1` to
    :math:`n_{max}`, where :math:`n_{max}` is the total number of steps on the Arai plot.
    
     
    
    Statistic: :math:`start` and :math:`end`
    
    :math:`start` and :math:`end` denote the :math:`i` indices of the selected steps used for analyzing the
    paleointensity results. :math:`i=start` denotes the first selected data point and :math:`i=end` denotes the last.
    
     
    
    Statistic: :math:`T_{min}` and :math:`T_{max}`
    
    The minimum and maximum temperatures used for the best-fit linear segment on the Arai plot, 
    where :math:`T_{min} \equiv T_{i=start}` and :math:`T_{max} \equiv T_{i=end}`.
    
    """

    def result_slope(self, t_min=None, t_max=None, component=None, recalc=False):
        """
        Gives result for calculate_slope(t_min, t_max), returns slope value if not calculated already
        """
        parameter = {'t_min': t_min,
                     't_max': t_max,
                     'component': component,
        }

        self.calc_result(parameter, recalc)
        return self.results['slope']

    def result_n(self, t_min=None, t_max=None, component=None, recalc=False):
        """
        Gives result for calculate_slope(t_min, t_max), returns slope value if not calculated already
        """
        parameter = {'t_min': t_min,
                     't_max': t_max,
                     'component': component,
        }

        self.calc_result(parameter, recalc, force_method='slope')
        return self.results['n']

    def result_sigma(self, t_min=None, t_max=None, component=None, recalc=False, **options):
        parameter = {'t_min': t_min,
                     't_max': t_max,
                     'component': component,
        }

        self.calc_result(parameter, recalc, force_method='slope')
        return self.results['sigma']

    def result_x_int(self, t_min=None, t_max=None, component=None, recalc=False, **options):
        parameter = {'t_min': t_min,
                     't_max': t_max,
                     'component': component,
        }

        self.calc_result(parameter, recalc, force_method='slope')
        return self.results['x_int']

    def result_y_int(self, t_min=None, t_max=None, component=None, recalc=False, **options):
        parameter = {'t_min': t_min,
                     't_max': t_max,
                     'component': component,
        }

        self.calc_result(parameter, recalc, force_method='slope')
        return self.results['y_int']

    def result_b_anc(self, t_min=None, t_max=None, component=None, b_lab=35.0, recalc=False, **options):
        parameter_a = {'t_min': t_min,
                       't_max': t_max,
                       'component': component,
        }
        parameter_b = {'b_lab': b_lab}

        self.calc_result(parameter_a, recalc,
                         force_method='slope')  # force caller because if not calculate_b_anc will be called
        self.calc_result(parameter_b, recalc)
        return self.results['b_anc']

    def result_sigma_b_anc(self, t_min=None, t_max=None, component=None, b_lab=35.0, recalc=False, **options):
        parameter_a = {'t_min': t_min,
                       't_max': t_max,
                       'component': component,
        }

        parameter_b = {'b_lab': b_lab}
        self.calc_result(parameter_a, recalc, force_method='slope')
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

    """ CALCULATE SECTION """

    def calculate_slope(self, **parameter):
        """
        calculates the least squares slope for the specified temperature interval

        :param parameter:

        """
        t_min = parameter.get('t_min', self.standard_parameter['slope']['t_min'])
        t_max = parameter.get('t_max', self.standard_parameter['slope']['t_max'])
        component = parameter.get('component', self.standard_parameter['slope']['component'])

        equal_steps = list(set(self.th['temp'].v) & set(self.ptrm['temp'].v))
        th_steps = (t_min <= self.th['temp'].v) & (self.th['temp'].v <= t_max)  # True if step between t_min, t_max
        ptrm_steps = (t_min <= self.ptrm['temp'].v) & (self.ptrm['temp'].v <= t_max)  # True if step between t_min, t_max

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
        self.results['sigma'] = sigma
        self.results['y_int'] = y_int
        self.results['x_int'] = x_int
        self.results['n'] = len(th_data[component].v)

        self.calculation_parameter['slope'] = {'t_min': t_min, 't_max': t_max, 'component': component}

    def calculate_b_anc(self, **parameter):
        """
        calculates the :math:`B_{anc}` value for a given lab field in the specified temperature interval.

        :param parameter:

        """

        b_lab = parameter.get('b_lab', 35.0)
        self.results['b_anc'] = b_lab * abs(self.results['slope'].v)
        self.calculation_parameter['b_anc'] = {'b_lab': b_lab}

    def calculate_sigma_b_anc(self, **parameter):
        """
        calculates the standard deviation of the least squares slope for the specified temperature interval

        :param parameter:

        """

        b_lab = parameter.get('b_lab', 35.0)
        self.results['sigma_b_anc'] = b_lab * abs(self.results['sigma'].v)
        self.calculation_parameter['sigma_b_anc'] = {'b_lab': b_lab}

    def calculate_vds(self, **parameter):  # todo move in rockpydata?
        """
        The vector difference sum of the entire NRM vector :math:`\\mathbf{NRM}`.

        .. math::

           VDS=\\left|\\mathbf{NRM}_{n_{max}}\\right|+\\sum\\limits_{i=1}^{n_{max}-1}{\\left|\\mathbf{NRM}_{i+1}-\\mathbf{NRM}_{i}\\right|}

        where :math:`\\left|\\mathbf{NRM}_{i}\\right|` denotes the length of the NRM vector at the :math:`i^{th}` step.


        :param parameter:
        :return:

        """
        NRM_t_max = self.th['mag'].v[-1]
        NRM_sum = np.sum(self.calculate_vd(**parameter))
        self.results['vds'] = NRM_t_max + NRM_sum

    def calculate_vd(self, **parameter):  # todo move in rockpydata?
        """
        Vector differences

        :param parameter:
        :return:

        """
        t_min = parameter.get('t_min', self.standard_parameter['vd']['t_min'])
        t_max = parameter.get('t_max', self.standard_parameter['vd']['t_max'])

        idx = (self.th['temp'].v <= t_max) & (t_min <= self.th['temp'].v)
        data = self.th.filter(idx)
        vd = np.array([np.linalg.norm(i) for i in np.diff(data['m'].v, axis=0)])
        return vd

    def calculate_x_dash(self, **parameter):
        """

        :math:`x_0 and :math:`y_0` the x and y points on the Arai plot projected on to the best-fit line. These are
        used to
        calculate the NRM fraction and the length of the best-fit line among other parameters. There are
        multiple ways of calculating :math:`x_0 and :math:`y_0`, below is one example.

        ..math:

          x_i' = \\frac{1}{2} \\left( x_i + \\frac{y_i - Y_{int}}{b}


        :param parameter:
        :return:

        """

        t_min = parameter.get('t_min', self.standard_parameter['x_dash']['t_min'])
        t_max = parameter.get('t_max', self.standard_parameter['x_dash']['t_max'])
        component = parameter.get('component', self.standard_parameter['x_dash']['component'])
        # self.log.info('CALCULATING\t << %s >> x_dash << t_min=%.1f , t_max=%.1f >>' % (component, t_min, t_max))

        equal_steps = list(set(self.th['temp'].v) & set(self.ptrm['temp'].v))
        th_steps = (t_min <= self.th['temp'].v) & (self.th['temp'].v <= t_max)  # True if step between t_min, t_max
        ptrm_steps = (t_min <= self.ptrm['temp'].v) & (
            self.ptrm['temp'].v <= t_max)  # True if step between t_min, t_max

        th_data = self.th.filter(th_steps)  # filtered data for t_min t_max
        ptrm_data = self.ptrm.filter(ptrm_steps)  # filtered data for t_min t_max

        # filtering for equal variables
        th_idx = [i for i, v in enumerate(th_data['temp'].v) if v in equal_steps]
        ptrm_idx = [i for i, v in enumerate(ptrm_data['temp'].v) if v in equal_steps]

        y = self.th.filter(th_idx)
        x = self.ptrm.filter(ptrm_idx)

        x_dash = 0.5 * (
            x[component].v + ((y[component].v - self.result_y_int(**parameter).v) / self.result_slope(**parameter).v))
        return x_dash

    def calculate_y_dash(self, **parameter):
        """

        :math:`x_0` and :math:`y_0` the x and y points on the Arai plot projected on to the best-fit line. These are
        used to
        calculate the NRM fraction and the length of the best-fit line among other parameters. There are
        multiple ways of calculating :math:`x_0` and :math:`y_0`, below is one example.

        ..math:

           y_i' = \\frac{1}{2} \\left( x_i + \\frac{y_i - Y_{int}}{b}


        :param parameter:
        :return:

        """
        t_min = parameter.get('t_min', self.standard_parameter['y_dash']['t_min'])
        t_max = parameter.get('t_max', self.standard_parameter['y_dash']['t_max'])
        component = parameter.get('component', self.standard_parameter['y_dash']['component'])


        equal_steps = list(set(self.th['temp'].v) & set(self.ptrm['temp'].v)) #steps that are in th and also in ptrm
        th_steps = (t_min <= self.th['temp'].v) & (self.th['temp'].v <= t_max)  # True if step between t_min, t_max
        ptrm_steps = (t_min <= self.ptrm['temp'].v) & (self.ptrm['temp'].v <= t_max)  # True if step between t_min, t_max

        th_data = self.th.filter(th_steps)  # filtered data for t_min t_max
        ptrm_data = self.ptrm.filter(ptrm_steps)  # filtered data for t_min t_max

        # filtering for equal variables
        th_idx = [i for i, v in enumerate(th_data['temp'].v) if v in equal_steps]
        ptrm_idx = [i for i, v in enumerate(ptrm_data['temp'].v) if v in equal_steps]

        y = th_data.filter_idx(th_idx)  # filtered data for equal t(th) & t(ptrm)
        x = ptrm_data.filter_idx(ptrm_idx)  # filtered data for equal t(th) & t(ptrm)

        y_dash = 0.5 * (y[component].v + self.result_slope(**parameter).v *
                        x[component].v + self.result_y_int(**parameter).v)
        return y_dash

    def calculate_delta_x_dash(self, **parameter):
        """

        :math:`\Delta x_0` is the TRM length of the best-fit line on the Arai plot.

        """
        x_dash = self.calculate_x_dash(**parameter)
        out = abs(np.max(x_dash)) - np.min(x_dash)
        return out

    def calculate_delta_y_dash(self, **parameter):
        """

        :math:`\Delta y_0`  is the NRM length of the best-fit line on the Arai plot.

        """
        y_dash = self.calculate_y_dash(**parameter)
        # print (np.max(y_dash)), np.min(y_dash), self.result_y_int().v[0]
        # print (np.max(y_dash)) - np.min(y_dash), self.result_y_int().v[0]
        # print ((np.max(y_dash)) - np.min(y_dash)) / self.result_y_int().v[0]
        out = abs(np.max(y_dash) - np.min(y_dash))
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

        # self.log.debug('CALCULATING\t f parameter')
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

        :math:`\beta` is a measure of the relative data scatter around the best-fit line and is the ratio of the
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
        # self.log.debug('CALCULATING\t quality parameter')

        beta = self.result_beta(**parameter).v
        f = self.result_f(**parameter).v
        gap = self.result_g(**parameter).v

        self.results['q'] = (f * gap) / beta

    def calculate_w(self, **parameter):
        """
        Weighting factor of Prevot et al. (1985). It is calculated by

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

    """
    PTRM CHECK statistics
    =====================

    A pTRM check is a repeat TRM acquisition step to test for changes in a specimen's ability to acquire TRM at
    blocking temperatures below the temperature of the check. The difference between a pTRM check and the original TRM
    is calculated as the scalar intensity difference. That is,

    :math:
    dpTRMi,j = pTRM checki,j -TRMi = pTRM checki,j -xi,

    where pTRM checki,j is the pTRM check to the ith temperature step after heating to the jth tem- perature step.
    The order of the difference is such that pTRM checks smaller than the original TRM yield negative dpTRMi,j and pTRM
    checks larger than the original TRM give positive dpTRMi,j. For a pTRM check to be included in the analysis,
    both Ti and Tj must be less than or equal to Tmax.
    """

    def get_d_ptrm(self, **parameter):
        """
        The difference between a pTRM check and the original TRM is calculated as the scalar intensity difference

        :math:

           \delta pTRM_{i,j} = pTRM_{check i,j} - TRM_i = pTRM_{check i,j} - TH_i

        :param parameter:
        :return: RockPy data object of CK - TH
        """
        t_min = parameter.get('t_min', self.standard_parameter['slope']['t_min'])
        t_max = parameter.get('t_max', self.standard_parameter['slope']['t_max'])

        temps = self.ck['temp'].v
        ptrm_temps = self.ptrm['temp'].v

        #get th_prior_2_ck
        out = np.array([(v, i, i2) for i, v in enumerate(temps) for i2, v2 in enumerate(ptrm_temps)
                        if v == v2
                        if v >= t_min
                        if v <= t_max])

        ck_data = self.ck.filter_idx(out[:, 1]) #ck data in temperatre range
        ptrm_ij = self.get_pTRM_ij(ck_data) # calculate the

        ptrm_data = self.ptrm.filter_idx(out[:, 2])
        out = deepcopy(ptrm_ij)
        for i in ['x', 'y', 'z']:
            out[i] = out[i].v - ptrm_data[i].v
        out['mag'] = out.magnitude(('x', 'y', 'z'))
        return out

    def get_pTRM_ij(self, ck_data):
        """
        searches for the th_i step before each CK-step
        :return: rpdata
        """


        ck_times = ck_data['time'].v  # times of CK step
        th_times = self.th['time'].v  # times of TH steps

        # get index of the th step measured directly before the ac step
        idx = np.array([(i, max([j for j, v2 in enumerate(th_times) if v2 - v < 0])) for i, v in enumerate(ck_times)])
        ck = ck_data.filter_idx(idx[:, 0])
        th_i = self.th.filter_idx(idx[:, 1])

        out = deepcopy(ck)

        for i in ['x', 'y', 'z', 'mag']:
            out[i] = out[i].v - th_i[i].v
        out['mag'] = out.magnitude('m')

        return out

    def result_n_ptrm(self, t_min=None, t_max=None, recalc=False, **options):
        parameter = {'t_min': t_min,
                     't_max': t_max,
        }
        self.calc_result(parameter, recalc)
        return self.results['n_ptrm']

    def result_ck_check_percent(self, t_min=None, t_max=None, component=None, recalc=False, **options):
        parameter = {'t_min': t_min,
                     't_max': t_max,
                     'component': component,

        }
        self.calc_result(parameter, recalc)
        return self.results['ck_check_percent']

    def result_delta_ck(self, t_min=None, t_max=None, component=None, recalc=False, **options):

        parameter = {'t_min': t_min,
                     't_max': t_max,
                     'component': component,
        }
        self.calc_result(parameter, recalc)
        return self.results['delta_ck']

    def result_drat(self, t_min=None, t_max=None, component=None, recalc=False, **options):

        parameter = {'t_min': t_min,
                     't_max': t_max,
                     'component': component,
        }
        self.calc_result(parameter, recalc)
        return self.results['drat']

    def result_ck_max_dev(self, t_min=None, t_max=None, component=None, recalc=False, **options):

        parameter = {'t_min': t_min,
                     't_max': t_max,
                     'component': component,
        }
        self.calc_result(parameter, recalc)
        return self.results['ck_max_dev']

    def calculate_n_ptrm(self, **parameter):
        """
        The number of pTRM checks (CK) used to analyze the best-fit segment on the Arai plot
        (i.e., the number of pTRMi,j with Ti <= Tmax and Tj <= Tmax).
        :param parameter:

        """
        t_min = parameter.get('t_min', self.standard_parameter['slope']['t_min'])
        t_max = parameter.get('t_max', self.standard_parameter['slope']['t_max'])

        temps = self.ck['temp'].v
        out = [i for i in temps
               if i >= t_min
               if i <= t_max]

        self.results['n_ptrm'] = len(out)

    def calculate_ck_check_percent(self, **parameter):
        """
        The number of pTRM checks (CK) used to analyze the best-fit segment on the Arai plot
        (i.e., the number of pTRMi,j with Ti <= Tmax and Tj <= Tmax).
        :param parameter:

        """
        t_min = parameter.get('t_min', self.standard_parameter['slope']['t_min'])
        t_max = parameter.get('t_max', self.standard_parameter['slope']['t_max'])
        component = parameter.get('component', self.standard_parameter['slope']['component'])

        dptrm = self.get_d_ptrm(**parameter)

        temps = dptrm['temp'].v
        pt_temps = self.pt['temp'].v
        out = np.array([(v, i, i2) for i, v in enumerate(temps) for i2, v2 in enumerate(pt_temps)
                        if v == v2
                        if v >= t_min
                        if v <= t_max])
        pt_data = self.pt.filter_idx(out[:, 2])
        percentages = (dptrm / pt_data) * 100

        max_idx = np.argmax(abs(percentages[component].v))
        out = percentages.filter_idx(max_idx)[component].v
        self.results['ck_check_percent'] = abs(out)

    def calculate_delta_ck(self, **parameter):
        """
        Maximum absolute difference produced by a pTRM check, normalized by the total TRM (obtained from the
        intersection of the best-fit line and the x-axis on an Arai plot; Leonhardt et al., 2004a).

        :math:

           \delta{CK}=\\frac`{\max{ \left\{ \left| \delta{pTRM_{i,j}} \right| \right\} }_{i \leq end \textbf{ and } j \leq end}}{\left|X_{Int.}\right|}\times{100}

        """

        t_min = parameter.get('t_min', self.standard_parameter['slope']['t_min'])
        t_max = parameter.get('t_max', self.standard_parameter['slope']['t_max'])
        component = parameter.get('component', self.standard_parameter['slope']['component'])

        dptrm = self.get_d_ptrm(**parameter)

        max_idx = np.argmax(abs(dptrm[component].v))
        out = ( abs(dptrm.filter_idx(max_idx)[component].v) / self.result_x_int(**parameter).v[0] ) * 100
        self.results['delta_ck'] = out

    def calculate_drat(self, **parameter):
        """
        Maximum absolute difference produced by a pTRM check, normalized by the length of the best-fit line
        (Selkin and Tauxe, 2000).

        :math:

           DRAT=\\frac`{\max{\left\{\left|\delta{pTRM_{i,j}} \right| \right\}}_{i \leq end \textbf{ and } j \leq end}}{L}\times{100},

        where `L` is the length of the best-fit line on the Arai plot. `L` is given by:

        :math:

           L=\sqrt{ (\Delta{x'})^2 + (\Delta{y'})^2 }

        where `\Delta{x'}` and `\Delta{y'}` are TRM and NRM lengths of the best-fit line on the Arai plot, respectively (Section 3).
        """
        component = parameter.get('component', self.standard_parameter['slope']['component'])

        dptrm = self.get_d_ptrm(**parameter)
        L = np.sqrt((self.calculate_delta_x_dash(**parameter)) ** 2 + (self.calculate_delta_y_dash(**parameter)) ** 2)
        max_idx = np.argmax(abs(dptrm[component].v))
        out = ( abs(dptrm.filter_idx(max_idx)[component].v) / L ) * 100
        self.results['drat'] = out
        # self.calculation_parameter['drat'].update(parameter)

    def calculate_ck_max_dev(self, **parameter):
        """
        Maximum absolute difference produced by a pTRM check, normalized by the length of the TRM segment of the
        best-fit line on the Arai plot (Blanco et al., 2012).

        math::

           maxDEV=\\frac`{\max{\left\{\left|\delta{pTRM_{i,j}} \right| \right\}}_{i \leq end \textbf{ and } j \leq end}}{\Delta{x'}}\times{100}

        """
        component = parameter.get('component', self.standard_parameter['slope']['component'])

        dptrm = self.get_d_ptrm(**parameter)
        max_idx = np.argmax(abs(dptrm[component].v))
        out = ( dptrm.filter_idx(max_idx)[component].v / self.calculate_delta_x_dash(**parameter) ) * 100
        self.results['ck_max_dev'] = abs(out)




    """
    Cumulative pTRM check parameters
    ********************************

    Most cumulative pTRM checks can be calculated in two fashions. The first method, is the summation of the signed
    pTRM differences (i.e., :math:`\pm \delta{pTRM}`), the second is to calculate the sum of the absolute pTRM difference
    (i.e., :math:`\left|\delta{pTRM} \right|`). The convention of the Standard Paleointensity Definition is to denote the
    second approach with a prime (`'`). For example, `CDRAT` is calculated by the first method and `CDRAT'`
    by the second.

    """

    def result_cdrat(self, t_min=None, t_max=None, component=None, recalc=False, **options):

        parameter = {'t_min': t_min,
                     't_max': t_max,
                     'component': component,
        }
        self.calc_result(parameter, recalc)
        return self.results['cdrat']

    def result_drats(self, t_min=None, t_max=None, component=None, recalc=False, **options):

        parameter = {'t_min': t_min,
                     't_max': t_max,
                     'component': component,
        }
        self.calc_result(parameter, recalc)
        return self.results['drats']

    def result_mean_drat(self, t_min=None, t_max=None, component=None, recalc=False, **options):

        parameter = {'t_min': t_min,
                     't_max': t_max,
                     'component': component,
        }
        self.calc_result(parameter, recalc)
        return self.results['mean_drat']

    def result_mean_dev(self, t_min=None, t_max=None, component=None, recalc=False, **options):

        parameter = {'t_min': t_min,
                     't_max': t_max,
                     'component': component,
        }
        self.calc_result(parameter, recalc)
        return self.results['mean_dev']

    def result_delta_pal(self, t_min=None, t_max=None, component=None, recalc=False, **options):

        parameter = {'t_min': t_min,
                     't_max': t_max,
                     'component': component,
        }
        self.calc_result(parameter, recalc)
        return self.results['delta_pal']

    def calculate_cdrat(self, **parameter):
        """
        Cumulative `DRAT` (Kissel and Laj, 2004).

        .. math::

          CDRAT=\\frac{\\left|\\sum\\limits_{i=1}^{end}{\\delta{pTRM_{i,j}}}\\right|}{L}\\times{100} \\
          CDRAT'=\\frac{\\sum\\limits_{i=1}^{end}{\\left|\\delta{pTRM_{i,j}}\\right|}}{L}\\times{100}


        """
        component = parameter.get('component', self.standard_parameter['slope']['component'])

        dptrm = self.get_d_ptrm(**parameter)
        L = np.sqrt((self.calculate_delta_x_dash(**parameter)) ** 2 + (self.calculate_delta_y_dash(**parameter)) ** 2)

        signed_sum = np.abs(np.sum(dptrm[component].v))
        unsigned_sum = np.sum(np.fabs(dptrm[component].v))  # for cdrat' not used

        out = (signed_sum / L) * 100
        self.results['cdrat'] = out

    def calculate_drats(self, **parameter):
        """
        Cumulative pTRM check difference normalized by the pTRM gained at the maximum temperature used for the
        best-fit on the Arai diagram (Tauxe and Staudigel, 2004).


        .. math::

           DRATS &=\\frac{\\left|\\sum\\limits_{i=1}^{end}{\\delta{pTRM_{i,j}}}\\right|}{x_{end}}\\times{100} \\\\
           DRATS' &=\\frac{\\sum\\limits_{i=1}^{end}{\\left|\\delta{pTRM_{i,j}}\\right|}}{x_{end}}\\times{100}
        """

        t_min = parameter.get('t_min', self.standard_parameter['slope']['t_min'])
        t_max = parameter.get('t_max', self.standard_parameter['slope']['t_max'])
        component = parameter.get('component', self.standard_parameter['slope']['component'])

        dptrm = self.get_d_ptrm(**parameter)

        # finding last ptrm step for normalization of dck

        equal_steps = list(set(self.th['temp'].v) & set(self.ptrm['temp'].v))
        th_steps = (t_min <= self.th['temp'].v) & (self.th['temp'].v <= t_max)  # True if step between t_min, t_max
        ptrm_steps = (t_min <= self.ptrm['temp'].v) & (self.ptrm['temp'].v <= t_max)  # True if step betw. t_min, t_max

        ptrm_data = self.ptrm.filter(ptrm_steps)  # filtered data for t_min & t_max
        max_idx = np.argmax(ptrm_data['temp'].v)
        ptrm_data = ptrm_data.filter_idx(max_idx)

        signed_sum = np.abs(np.sum(dptrm[component].v))
        unsigned_sum = np.sum(np.fabs(dptrm[component].v))  # for cdrat' not used

        out = (signed_sum / ptrm_data[component].v[0] ) * 100
        self.results['drats'] = out

    def calculate_mean_drat(self, **parameter):
        """
        The average difference produced by a pTRM check, normalized by the length of the best-fit line.

        .. math::

           \\textrm{Mean }DRAT=\\frac{1}{n_{pTRM}}\\frac{\\left|\\sum\\limits_{i=1}^{end}{\\delta{pTRM_{i,j}}}\\right|}{L}\\times{100} \\
           \\textrm{Mean }DRAT'=\\frac{1}{n_{pTRM}}\\frac{\\sum\\limits_{i=1}^{end}{\\left|\\delta{pTRM_{i,j}}\\right|}}{L}\\times{100}
        """
        out = (1 / self.result_n_ptrm(**parameter).v) * self.result_drat(**parameter).v
        self.results['mean_drat'] = out

    def calculate_mean_dev(self, **parameter):
        """
        Mean deviation of a pTRM check (Blanco et al., 2012).

        .. math::

           \\textrm{Mean }DEV=\\frac{1}{n_{pTRM}}\\frac{\\left|\\sum\\limits_{i=1}^{end}\\delta{pTRM_{i,j}}\\right|}{\\Delta{x'}}\\times{100} \\
           \\textrm{Mean }DEV'=\\frac{1}{n_{pTRM}}\\frac{\\sum\\limits_{i=1}^{end}\\left|\\delta{pTRM_{i,j}}\\right|}{\\Delta{x'}}\\times{100}

        """
        component = parameter.get('component', self.standard_parameter['slope']['component'])

        dptrm = self.get_d_ptrm(**parameter)

        signed_sum = np.abs(np.sum(dptrm[component].v))
        unsigned_sum = np.sum(np.fabs(dptrm[component].v))  # for cdrat' not used

        out = (1 / self.result_n_ptrm(**parameter).v) * (signed_sum / self.calculate_delta_x_dash(**parameter)) * 100
        self.results['mean_dev'] = out

    def calculate_delta_pal(self, **parameter):
        """
        A measure of cumulative alteration determined by the difference of the alteration corrected intensity estimate 
        (Valet et al., 1996) and the uncorrected estimate, normalized by the uncorrected estimate 
        (Leonhardt et al., 2004a).

        We first calculate the cumulative sum of the pTRM checks up to the :math:`i^{th}` step of the experiment:
        
        .. math::
        
           \\mathbf{C}_i=\\sum\\limits_{l=1}^{l=i}{ \\mathbf{\\delta{pTRM}}_{l,j} }, ~~\\textrm{for} ~i=1,\\ldots, n_{max}, 
        
        where :math:`\mathbf{\delta{pTRM}}_{l,j}` is the vector difference between :math:`\mathbf{TRM}_l`
        and :math:`\mathbf{pTRM\_check}_{l,j}`, i.e.,

        .. math::

           \\mathbf{\\delta{pTRM}}_{l,j}=\\mathbf{TRM}_l - \\mathbf{pTRM\\_check}_{l,j}.

        When no pTRM check is performed :math:`\mathbf{\delta{pTRM}}_l=[0,0,0]`.

        The :math:`\mathbf{TRM}_i` vector is then corrected by adding the cumulative effect of the alteration,
        :math:`\mathbf{C}_i`:

        .. math::

           \mathbf{TRM}_i^*=\mathbf{TRM}_i+\mathbf{C}_{i}, ~~ \\textrm{for} ~i=1,\ldots, n_{max}.

        Since no pTRM check is performed at the first step:

        .. math::

           \mathbf{TRM}_1^*=\mathbf{TRM}_1.

        The corrected TRM values on the Arai plot (:math:`x_i^*`) can be calculated by determining the vector
        lengths of :math:`\mathbf{TRM}_i^*`.
        The corrected slope on the Arai plot (:math:`b^*`) can be calculated using the selected points and the
        standard approach outlined in Section 3.

        :math:`\delta{pal}` is then given by:

        .. math::

           \delta{pal}=\left|\\frac{b-b^*}{b}\right|\times100.

        """
        component = parameter.get('component', self.standard_parameter['slope']['component'])
        # todo
        #
        # dptrm = self.get_d_ptrm(**parameter)
        #
        # signed_sum = np.abs(np.sum(dptrm[component].v))
        # unsigned_sum = np.sum(np.fabs(dptrm[component].v))  # for cdrat' not used
        #
        # out = (1 / self.result_n_ptrm(**parameter).v) * (signed_sum / self.calculate_delta_x_dash(**parameter)) *100
        # self.results['mean_dev'] = out


    def get_d_tail(self, **parameter):
        """
        pTRM tails check statistics (TR)
        ================================

        A pTRM tail check is a repeat demagnetization step to test for changes in a specimen's magnetization carried in the
        blocking temperature range above the temperature of the check. The difference between the first NRM measurement and
        the pTRM tail check is calculated as the scalar intensity difference:

        .. math::

           \delta{tail_i}=tail\_check_i - NRM_i = tail\_check_i - y_i,

        where :math:`tail\_check_i` is the pTRM tail check to the :math:`i^{th}` temperature step. The order of the
        difference is such that tail checks smaller than the original NRM yield negative :math:`\delta{tail_i}` and tail
        checks larger than the original NRM give positive :math:`\delta{tail_i}`. For a pTRM tail check to be included
        in the analysis, :math:`T_i` must be less than or equal to :math:`T_{max}`.

        The difference between a pTRM check and the original TRM is calculated as the scalar intensity difference

        :math:

           \delta pTRM_{i,j} = pTRM_{check i,j} - TRM_i = pTRM_{check i,j} - TH_i

        :param parameter:
        :return: RockPy data object of CK - TH
        """

        t_min = parameter.get('t_min', self.standard_parameter['slope']['t_min'])
        t_max = parameter.get('t_max', self.standard_parameter['slope']['t_max'])

        temps = self.tr['temp'].v
        th_steps = self.th['temp'].v

        out = np.array([(v, i, i2) for i, v in enumerate(temps) for i2, v2 in enumerate(th_steps)
                        if v == v2
                        if v >= t_min
                        if v <= t_max])

        tr_data = self.tr.filter_idx(out[:, 1])
        th_data = self.th.filter_idx(out[:, 2])

        out = tr_data - th_data
        # out['mag'] = out.magnitude(('x', 'y', 'z'))
        return out

    def result_n_tail(self, t_min=None, t_max=None, recalc=False, **options):
        parameter = {'t_min': t_min,
                     't_max': t_max,
        }
        self.calc_result(parameter, recalc)
        return self.results['n_tail']

    def result_drat_tail(self, t_min=None, t_max=None, component=None, recalc=False, **options):

        parameter = {'t_min': t_min,
                     't_max': t_max,
                     'component': component,
        }
        self.calc_result(parameter, recalc)
        return self.results['drat_tail']

    def result_delta_tr(self, t_min=None, t_max=None, component=None, recalc=False, **options):

        parameter = {'t_min': t_min,
                     't_max': t_max,
                     'component': component,
        }
        self.calc_result(parameter, recalc)
        return self.results['delta_tr']

    def result_md_vds(self, t_min=None, t_max=None, component=None, recalc=False, **options):

        parameter = {'t_min': t_min,
                     't_max': t_max,
                     'component': component,
        }
        self.calc_result(parameter, recalc)
        return self.results['md_vds']

    def result_d_t(self, t_min=None, t_max=None, component=None, recalc=False, **options):

        parameter = {'t_min': t_min,
                     't_max': t_max,
                     'component': component,
        }
        self.calc_result(parameter, recalc)
        return self.results['d_t']

    def calculate_n_tail(self, **parameter):
        """
        The number of pTRM tail checks conducted below the maximum temperature used for the best-fit segment on the
        Arai plot (i.e., the number of pTRM tail checks used to analyze the best-fit segment on the Arai plot).
        :param parameter:

        """
        t_min = parameter.get('t_min', self.standard_parameter['slope']['t_min'])
        t_max = parameter.get('t_max', self.standard_parameter['slope']['t_max'])

        temps = self.tr['temp'].v
        out = [i for i in temps
               if i >= t_min
               if i <= t_max]

        self.results['n_tail'] = len(out)

    def calculate_drat_tail(self, **parameter):
        """
        Maximum absolute difference produced by a pTRM tail check, normalized by the length of the best-fit line
        (Biggin et al., 2007).

        .. math::

           DRAT_{Tail}=\\frac`{\max{\{\left| \delta{tail_i} \right|\}}_{i=1, \ldots, end}}{L}\times{100}

        """
        component = parameter.get('component', self.standard_parameter['slope']['component'])

        dtail = self.get_d_tail(**parameter)
        L = np.sqrt((self.calculate_delta_x_dash(**parameter)) ** 2 + (self.calculate_delta_y_dash(**parameter)) ** 2)
        max_idx = np.argmax(abs(dtail[component].v))
        out = ( abs(dtail.filter_idx(max_idx)[component].v) / L ) * 100
        self.results['drat_tail'] = out

    def calculate_delta_tr(self, **parameter):
        """
        Maximum absolute difference produced by a pTRM tail check, normalized by the NRM (obtained from the
        intersection of the best-fit line and the y-axis on an Arai plot; Leonhardt et al., 2004a).

        .. math::

           \delta{TR}=\\frac`{\max{\{\left| \delta{tail_i} \right|\}}_{i=1, \ldots, end}}{\left|Y_{Int.}\right|}\times{100}

        """
        component = parameter.get('component', self.standard_parameter['slope']['component'])

        dtail = self.get_d_tail(**parameter)
        max_idx = np.argmax(abs(dtail[component].v))
        out = ( abs(dtail.filter_idx(max_idx)[component].v) / abs(self.result_y_int(**parameter).v)) * 100
        self.results['delta_tr'] = out

    def calculate_md_vds(self, **parameter):
        """
        Maximum absolute difference produced by a pTRM tail check, normalized by the vector difference sum of the
        NRM (Tauxe and Staudigel, 2004).

        .. math::

           MD_{VDS}=\\frac`{\max{\{\left| \delta{tail_i} \right|\}}_{i=1, \ldots, end}}{VDS}\times{100}

        .. note::
        Some versions of PmagPy and ThellierGUI use a pTRM tail check statistic called $$MD(\%)$$. This is identical
        to $$MD_{VDS}$$, but the change in name emphasizes its calculation method.
        """
        component = parameter.get('component', self.standard_parameter['slope']['component'])

        dtail = self.get_d_tail(**parameter)
        max_idx = np.argmax(abs(dtail[component].v))
        out = ( abs(dtail.filter_idx(max_idx)[component].v) / abs(self.result_vds(**parameter).v)) * 100
        self.results['md_vds'] = out

    def calculate_d_t(self, **parameter):
        """
        The extent of a pTRM tail after correction for angular dependence (Leonhardt et al., 2004a; 2004b).

        The applied laboratory field vector (:math:`\mathbf{B}_{Lab}`) is typically applied along a principle axis in the
        sample coordinate system (i.e., :math:`\pm x`, :math:`\pm y`, or :math:`\pm z`). Therefore,
        for simplicity, :math:`\delta{t^*}` should be calculated in the sample coordinate system only.
        Figure 7 is a schematic illustration of aspects of the calculation of :math:`\delta{t^*}`.

        Figure 7.Schematic illustration of an NRM vector (:math:`\mathbf{NRM}_i`) and a pTRM tail
        check vector (:math:`\mathbf{tail\_check}_i`) for a sample that exhibits a pTRM tail.
        Modified after Leonhardt et al. (2004b).

        Let :math:`N_{x,i}`, :math:`N_{y,i}`, and :math:`N_{z,i}` denote the Cartesian coordinates of the NRM
        vector at step :math:`i` (i.e., :math:`\mathbf{NRM}_i = [N_{x,i}, N_{y,i}, N_{z,i}]`).
        Similarly, let :math:`T_{x,i}`, :math:`T_{y,i}`, and :math:`T_{z,i}` denote the Cartesian
        coordinates of the repeat demagnetization vector at step
        :math:`i` (i.e., :math:`\mathbf{tail\_check}_i = ` [:math:`T_{x,i}`, :math:`T_{y,i}`, :math:`T_{z,i}`]).

        Assuming that :math:`\mathbf{B}_{Lab}` is applied along the z-axis, the difference
        in the horizontal (:math:`\delta{H_i}`) and vertical components (:math:`\delta{Z_i}`)
        between :math:`\mathbf{NRM}_i` and :math:`\mathbf{tail\_check}_i` (Figure 7) are given by:
        
        .. math::
        
           \\delta{H_i}=\\sqrt{N_{x,i}^2 + N_{y,i}^2} - \\sqrt{T_{x,i}^2 + T_{y,i}^2} \\] and \\[ \\delta{Z_i}=N_{z,i} - T_{z,i}. \\]

        pTRM tails have an angular dependence and the calculation of $$\delta{t^*}$$
        requires two angular differences. Let $$\Delta{\theta}_i$$ denote the angle between
        $$\mathbf{B}_{Lab}$$ and $$\mathbf{NRM}_i$$ (see Section 4 for advice on calculating the
        angle between two vectors). Let $$\delta{Inc}_i$$ denote the difference in inclinations
        between the $$\mathbf{B}_{Lab}$$ and $$\mathbf{NRM}_i$$:

        .. math::
        
           \\delta{Inc_i}=Inc(\\mathbf{B}_{Lab}) - Inc(\\mathbf{NRM}_i)=\\arctan{\\left(\\\\frac`{B_{Lab,z}}{\\sqrt{B_{Lab,x}^2 + B_{Lab,y}^2}}\\right)} - \\arctan{\\left(\\\\frac`{N_{z,i}}{\\sqrt{N_{x,i}^2 + N_{x,i}^2}}\\right)}.

        In the ThellierTool software (v4.22 and previous) :math:$$\mathbf{B}_{Lab}$$ is determined from
        each :math:$$\mathbf{TRM}_i$$. Given that :math:$$\mathbf{B}_{Lab}$$ is almost always known, the convention of
        SPD is to use the known :math:$$\mathbf{B}_{Lab}$$ and not as estimated from :math:$$\mathbf{TRM}_i$$,
        which may suffer from the effects of experimental noise.

        As will be seen below, the calculation of :math:$$\delta{t^*}$$ requires :math:$$\\frac`{1}{\tan{(\Delta{\theta}_i)}}$$.
        As :math:$$\Delta{\theta}_i$$ approaches zero or 180 this fraction tends to infinity. To tackle this,
        :math:$$\delta{t^*}$$ is calculated in a piecewise fashion that depends on upper and lower angular limits
        (:math:$$Lim_{upper}$$ and :math:$$Lim_{lower}$$, respectively). Below is pseudo-code that describes the logic
        of the calculation procedure.

        In v4.22 of the ThellierTool :math:$$Lim_{lower} = 0.175$$ (:math:$$\approx10$$) radi


        :math:$$\delta{t^*}$$ is then calculated as:

        .. math::
        
           \\delta{t^*}=\\left\\{ \\begin{array}{lc}	\\max{ \\left\\{ t^*_i\\right\\} }_{i=1, \\ldots, end}	&	\\mbox{ if } (\\max{ \\left\\{ t^*_i\\right\\} }_{i=1, \\ldots, end} > 0)\\\\ 0	&	\\mbox{ if } (\\max{ \\left\\{ t^*_i\\right\\} }_{i=1, \\ldots, end} < 0)\\end{array}\\right.

        Only positive values of :math:$$t^*$$ and :math:$$\delta{t^*}$$ can be attributed to the effects of pTRM
        tails, hence :math:$$\delta{t^*}$$ is calculated as the maximum of :math:$$t^*$$ and not the maximum of :math:$$\left|t^*\right|$$.

        It should be noted that an implicit assumption in the above calculations is that :math:$$\mathbf{B}_{Lab}$$
        is applied along the :math:$$z$$-axis. In situations where :math:$$\mathbf{B}_{Lab}$$ is applied along the
        :math:$$x$$- or :math:$$y$$-axes, the definition of ``horizontal'' and ``vertical'' can be redefined such that
        :math:$$\mathbf{B}_{Lab}$$ is applied in the ``vertical'' direction. For example, if :math:$$\mathbf{B}_{Lab}$$
        is along the :math:$$x$$-axis, :math:$$\delta{H_i}$$ and :math:$$\delta{Z_i}$$ can be defined as:

        .. math::
        
           \\delta{H_i}=\\sqrt{N_{y,i}^2 + N_{z,i}^2} - \\sqrt{T_{y,i}^2 + T_{z,i}^2} \\] and \\[ \\delta{Z_i}=N_{x,i} - T_{x,i},

        and
        
        .. math::
        
           \\delta{Inc_i}=\\arctan{\\left(\\frac{B_{Lab,x}}{\\sqrt{B_{Lab,y}^2 + B_{Lab,z}^2}}\\right)} - \\arctan{\\left(\\\\frac`{N_{x,i}}{\\sqrt{N_{y,i}^2 + N_{z,i}^2}}\\right)}.

        The remaining calculations can proceed as described above.
        """
        self.results['delta_tr'] = np.nan

    """
    Additivity check statistics
    ===========================

    An additivity check is a repeat demagnetization step to test the validity of Thellier's law of additivity
    (Krasa et al., 2003). In the course of a paleointensity experiment, a pTRM at temperature :math:`T_j` is imparted,
    pTRM(:math:`T_j`, :math:`T_0`), where :math:`T_0` is room temperature. An additivity check demagnetizes
    pTRM(:math:`T_j`, :math:`T_0`) by heating to :math:`T_i`, where :math:`T_i < T_j`. The remaining pTRM
    (pTRM(:math:`T_j`, :math:`T_i`)) is subtracted from the previous pTRM acquisition step,
    pTRM(:math:`T_j`, :math:`T_0`), to estimate pTRM:math:`^*`(:math:`T_i`, :math:`T_0`). That is

    .. math::

       pTRM^*(T_i, T_0)=pTRM(T_j, T_0)-pTRM(T_j, T_i)

    where * denotes an estimated value. This estimated value can be compared with a previously observed
    value of pTRM(:math:`T_i`, :math:`T_0`) that was measured earlier in the experiment. The difference
    between the estimated and observed pTRMs is a measure of the violation of
    additivity between :math:`T_i` and :math:`T_0`. The additivity check difference (:math:`AC_{i,j}`)
    is the scalar intensity difference between the two pTRMs:

    .. math::

       AC_{i,j}=pTRM^*(T_i, T_0)-pTRM(T_i, T_0).

    For an additivity check to be included in the analysis, both :math:`T_i` and :math:`T_j`
    must be less than or equal to :math:`T_{max}`.

    """

    def get_d_ac(self, **parameter):
        """
        Additivity check statistics
        ===========================

        An additivity check is a repeat demagnetization step to test the validity of Thellier's law of additivity
        (Krasa et al., 2003). In the course of a paleointensity experiment, a pTRM at temperature :math:`T_j` is imparted,
        pTRM(:math:`T_j`, :math:`T_0`), where :math:`T_0` is room temperature. An additivity check demagnetizes
        pTRM(:math:`T_j`, :math:`T_0`) by heating to :math:`T_i`, where :math:`T_i < T_j`. The remaining pTRM
        (pTRM(:math:`T_j`, :math:`T_i`)) is subtracted from the previous pTRM acquisition step,
        pTRM(:math:`T_j`, :math:`T_0`), to estimate pTRM:math:`^*`(:math:`T_i`, :math:`T_0`). That is

        .. math::

           pTRM^*(T_i, T_0)=pTRM(T_j, T_0)-pTRM(T_j, T_i)

        where * denotes an estimated value. This estimated value can be compared with a previously observed
        value of pTRM(:math:`T_i`, :math:`T_0`) that was measured earlier in the experiment. The difference
        between the estimated and observed pTRMs is a measure of the violation of
        additivity between :math:`T_i` and :math:`T_0`. The additivity check difference (:math:`AC_{i,j}`)
        is the scalar intensity difference between the two pTRMs:

        .. math::

           AC_{i,j}=pTRM^*(T_i, T_0)-pTRM(T_i, T_0).

        For an additivity check to be included in the analysis, both :math:`T_i` and :math:`T_j`
        must be less than or equal to :math:`T_{max}`.

        """

        t_min = parameter.get('t_min', self.standard_parameter['slope']['t_min'])
        t_max = parameter.get('t_max', self.standard_parameter['slope']['t_max'])

        ptrm_i0 = self.get_ptrm_i0()

        ac_temps = ptrm_i0['temp'].v
        ptrm_temps = self.ptrm['temp'].v

        # filter indices according to t_min and t_max requirement, also ptrm* and ptrm have to have the same temperature step
        out = np.array([(v, i, i2) for i, v in enumerate(ac_temps) for i2, v2 in enumerate(ptrm_temps)
                        if v == v2
                        if v >= t_min
                        if v <= t_max])

        ptrm_i0_data = ptrm_i0.filter_idx(out[:, 1])
        ptrm_i_data = self.ptrm.filter_idx(out[:, 2])

        d_ac = ptrm_i0_data - ptrm_i_data
        d_ac['time'] = ptrm_i0_data['time'].v
        d_ac['mag'] = d_ac.magnitude(('x', 'y', 'z'))
        return d_ac

    def get_ptrm_ij(self):
        """
        Calculates the ptrm_i step from AC-demagnetization steps
        :return: rpdata
        """
        ac_times = self.ac['time'].v  # times of AC step
        th_times = self.th['time'].v  # times of PTRM steps

        # get index of the ptrm step measured directly before the ac step
        idx = np.array([(i, max([j for j, v2 in enumerate(th_times) if v2 - v < 0])) for i, v in enumerate(ac_times)])
        ac_i = self.ac.filter_idx(idx[:, 0])
        th_j = self.th.filter_idx(idx[:, 1])

        ptrm_ij = deepcopy(ac_i)

        for key in ['x','y','z', 'mag']:
            ptrm_ij[key] = ptrm_ij[key].v - th_j[key].v

        # ptrm_ij['mag'] = ptrm_ij.magnitude(('x', 'y', 'z'))
        return ptrm_ij

    def get_ptrm_i0(self):
        """
        Calculates the ptrm_i step from AC-demagnetization steps
        :return: rpdata
        """
        ac_times = self.ac['time'].v  # times of AC step
        ptrm_times = self.ptrm['time'].v  # times of PTRM steps

        # get index of the ptrm step measured directly before the ac step
        idx = np.array([(i, max([j for j, v2 in enumerate(ptrm_times) if v2 - v < 0])) for i, v in enumerate(ac_times)])
        ac_i = self.ac.filter_idx(idx[:, 0])
        ptrm_j = self.ptrm.filter_idx(idx[:, 1])

        ptrm_ij = self.get_ptrm_ij()
        ptrm_i0 = deepcopy(self.get_ptrm_ij())

        for key in ['x','y','z']:
            ptrm_i0[key] = ptrm_j[key].v - ptrm_i0[key].v
        ptrm_i0['mag'] = ptrm_i0.magnitude(('x', 'y', 'z', 'mag'))
        return ptrm_i0

    def result_n_ac(self, t_min=None, t_max=None, recalc=False, **options):
        parameter = {'t_min': t_min,
                     't_max': t_max,
        }
        self.calc_result(parameter, recalc)
        return self.results['n_ac']

    def result_delta_ac(self, t_min=None, t_max=None, recalc=False, **options):
        parameter = {'t_min': t_min,
                     't_max': t_max,
        }
        self.calc_result(parameter, recalc)
        return self.results['delta_ac']

    def calculate_n_ac(self, **parameter):
        """
        The number of additivity checks used to analyze the best-fit segment on the Arai plot 
        (i.e., the number of :math:`AC_{i,j}` with :math:`T_i \leq T_{max}` and :math:`T_j \leq T_{max}`).

        :param parameter:

        """
        t_min = parameter.get('t_min', self.standard_parameter['slope']['t_min'])
        t_max = parameter.get('t_max', self.standard_parameter['slope']['t_max'])

        temps = self.ac['temp'].v
        out = [i for i in temps
               if i >= t_min
               if i <= t_max]

        self.results['n_ac'] = len(out)

    def calculate_delta_ac(self, **parameter):
        """
        The maximum absolute additivity check difference normalized by the total TRM (obtained from the intersection 
        of the best-fit line and the x-axis on an Arai plot; Leonhardt et al., 2004a). 
        
        .. math::
        
           \\delta{AC}=\\frac{\\max{ \\left\\{ \\left| AC_{i,j} \\right| \\right\\} }_{i \\leq end \\textbf{ and } j \\leq end}}{\\left|X_{Int.}\\right|}\\times{100}.

        """
        component = parameter.get('component', self.standard_parameter['slope']['component'])

        d_ac = self.get_d_ac(**parameter)
        max_idx = np.argmax(abs(d_ac[component].v))
        out = ( abs(d_ac.filter_idx(max_idx)[component].v) / abs(self.result_x_int(**parameter).v)) * 100
        self.results['delta_ac'] = out


    """ CHECK SECTION """

    def _get_ck_data(self):
        """
        Helper function, returns the preceding th steps to each ck step

        :returns: list [ck_ij, th_i, ptrm_j, th_j]
           where ck_ij  = the ptrm check to the ith temperature after heating to the jth temperature
                 th_i   = the th step at temeprtature i
                 ptrm_j = the ptrm step at temeprtature j
                 th_j = the th step at temeprtature j
        """
        out = []

        for ck in self.ck.v:
            th_j = [0, 0, 0, 0, 0, 0]
            for th in self.th.v:
                if ck[-2] - th[-2] > 0:  # if the time diff >0 => ck past th step
                    if th_j[-2] < th[-2]:
                        th_j = th
                if ck[0] == th[0]:
                    th_i = th
            for ptrm in self.ptrm.v:
                if ptrm[0] == th_j[0]:
                    ptrm_j = ptrm
            for pt in self.pt.v:
                if pt[0] == th_i[0]:
                    pt_i = pt
            d_ck = ck[1:4] - th_j[1:4]
            d_ck_m = np.linalg.norm(d_ck)
            d_ck = np.array([ck[0], d_ck[0], d_ck[1], d_ck[2], ck[4] + th_j[4], ck[-2], d_ck_m])

            out.append([d_ck, th_i, ptrm_j, th_j])
        for i in out:
            from pprint import pprint

            print i[0][0], i[1][0], i[2][0], i[3][0]
            print 'ck_ij'
            pprint(i[0])
            print 'th_i'
            pprint(i[1])
            print 'ptrm_j'
            pprint(i[2])
            print 'th_j'
            pprint(i[3])
        return out

    def _get_ac_data(self):
        """
        Helper function, returns the preceding th steps to each ck step

        :returns: list [ck_ij, th_i, ptrm_j, th_j]
           where ck_ij = the ptrm check to the ith temperature after heating to the jth temperature
        """
        out = []

        for ac in self.ac:
            th_j = [0, 0, 0, 0, 0]
            for th in self.th:
                if ac[-1] > th[-1]:
                    if th_j[-1] < th[-1]:
                        th_j = th
                if ac[0] == th[0]:
                    th_i = th
            for ptrm in self.ptrm:
                if ptrm[0] == th_j[0]:
                    ptrm_j = ptrm
            for pt in self.pt:
                if pt[0] == th_j[0]:
                    pt_i = pt

            d_ac = pt_i[1:4] - ac[1:4]
            d_ac_m = np.linalg.norm(d_ac)
            d_ac = np.array([ac[0], d_ac[0], d_ac[1], d_ac[2], d_ac_m, ac[-1]])

            out.append([d_ac, th_i, ptrm_j, th_j])
        # for i in out:
        # print i[0][0], i[1][0], i[2][0], i[3][0]
        # print i[0][4], i[1][4], i[2][4], i[3][4]
        return out


    """ EXPORT SECTION """

    def export_tdt(self, folder=None, filename=None):
        import os
        i = ['%s_%.2f_%s'%(t.ttype, t.value, t.unit) for t in self.treatments]
        if not folder:
            folder = os.path.join(os.path.expanduser('~'), 'Desktop')
        if not filename:
            filename = '#'.join([self.sample_obj.name, ';'.join(i), '.tdt'])
        # v = 115.2 #standard volume 8mm diameter
        # v = 4.86E-8  # standard volume 6mm diameter
        volume = 1

        # tdt = {'th': 0.00, 'pt': 0.11, 'ac': 0.14, 'ck': 0.12, 'tr': 0.13} #long version
        tdt = {'th': 0.0, 'pt': 0.1, 'ac': 0.4, 'ck': 0.2, 'tr': 0.3}

        th = deepcopy(self.data['th'])
        pt = deepcopy(self.data['pt'])
        pt = pt.filter_idx(range(1, len(pt['temp'].v)))
        ac = deepcopy(self.data['ac'])
        ck = deepcopy(self.data['ck'])
        tr = deepcopy(self.data['tr'])
        steps = ['th', 'pt', 'ac', 'ck', 'tr']

        out = None

        for idx, i in enumerate([th, pt, ac, ck, tr]):
            i['x'] = i['x'].v / volume
            i['y'] = i['y'].v / volume
            i['z'] = i['z'].v / volume
            i['mag'] = i.magnitude('m')
            i['temp'] = i['temp'].v + tdt[steps[idx]]
            if not out:
                out = i
            else:
                out = out.append_rows(i)
        out = out.sort('time')

        lines = ['Thellier-tdt\r\n','35.0\t0\t0\t0\t0\r\n']
        for i, v in enumerate(out['m']):
            DIL = general.XYZ2DIL(v[:, 0])
            lines.append(
                '%s\t%.01f\t%.03E\t%.03f\t%.03f\r\n' % (self.sample_obj.name, out['temp'].v[i], DIL[2], DIL[0], DIL[1]))

        with open(os.path.join(folder, filename), 'w+') as f:
            for line in lines:
                f.writelines(line)


if __name__ == '__main__':
    s = RockPy.Sample(name='ThellierTest')
    m = s.add_simulation(mtype='thellier', sim_params={'max_moment':10})
    # for dtype in m.data:
    #     print dtype
    #     print m.data[dtype]
    print s.calc_all()
    m.export_tdt()