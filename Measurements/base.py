__author__ = 'volk'

import logging
import inspect
import itertools

from copy import deepcopy
import numpy as np

import os.path

import RockPy
import RockPy.Functions.general
import RockPy.Readin.base
from RockPy.Readin import *
from RockPy.core import to_list
from RockPy.Structure.data import RockPyData, _to_tuple

class Measurement(object):
    """

    HOW TO get at stuff
    ===================
    HowTo:
    ======
       stypeS
       ++++++
        want all series types (e.g. pressure, temperature...):

        as list: measurement.stypes
           print measurement.stypes
           >>> ['pressure']
        as dictionary with corresponding series as value: measurement.tdict
           print measurement.tdict
           >>> {'pressure': <RockPy.Series> pressure, 0.60, [GPa]}
        as dictionary with itself as value: measurement._self_tdict
           >>> {'pressure': {0.6: <RockPy.Measurements.thellier.Thellier object at 0x10e2ef890>}}

       svalUES
       +++++++
       want all values for any series in a measurement

        as list: measurement.svals
        print measuremtn.svals
        >>> [0.6]


    """

    logger = logging.getLogger('RockPy.MEASUREMENT')

    @classmethod
    def simulate(cls, **parameter):
        """
        pseudo abstract method that should be overridden in subclasses to return a simulated measurement
        based on given parameters
        """
        return None

    @classmethod
    def implemented_machines(cls):
        # setting implemented machines
        # looking for all subclasses of RockPy.Readin.base.Machine
        # generating a dictionary of implemented machines : {implemented out_* method : machine_class}
        implemented_machines = {cl.__name__.lower(): cl for cl in RockPy.Readin.base.Machine.__subclasses__()}
        return implemented_machines

    @classmethod
    def inheritors(cls):
        subclasses = set()
        work = [cls]
        while work:
            parent = work.pop()
            for child in parent.__subclasses__():
                if child not in subclasses:
                    subclasses.add(child)
                    work.append(child)
        return subclasses

    @classmethod
    def implemented_measurements(self):
        return {i.__name__.lower(): i for i in Measurement.inheritors()}

    @classmethod
    def measurement_formatters(cls):
        # measurement formatters are important!
        # if they are not inside the measurement class, the measurement has not been implemented for this machine.
        # the following machine formatters:
        # 1. looks through all implemented measurements
        # 2. for each measurement stores the machine and the applicable readin class in a dictonary

        measurement_formatters = {cl.__name__.lower():
                                      {'_'.join(i.split('_')[1:]).lower():
                                           Measurement.implemented_machines()['_'.join(i.split('_')[1:]).lower()]
                                       for i in dir(cl) if i.startswith('format_')}
                                  for cl in Measurement.inheritors()}
        return measurement_formatters

    @classmethod
    def get_subclass_name(cls):
        return cls.__name__

    def __init__(self, sample_obj,
                 mtype, mfile, machine, mdata=None, color=None,
                 series = None,
                 **options):
        """
           sample_obj:
           mtype:
           mfile:
           machine:
           mdata: when mdata is set, this will be directly used as measurement data without formatting from file
           color: color used for plotting if specified
           options:
        :return:
        """

        self.logger = logging.getLogger('RockPy.MEASURMENT.' + self.get_subclass_name())

        self.color = color
        self.has_data = True
        self._data = {}
        self._raw_data = {}
        self.is_initial_state = False
        self.is_mean = False  # flag for mean measurements

        if machine is not None:
            machine = machine.lower()  # for consistency in code

        if mtype is not None:
            mtype = mtype.lower()  # for consistency in code

        ''' initialize parameters '''
        self.machine_data = None  # returned data from Readin.machines()
        self.suffix = options.get('suffix', '')

        ''' initial state '''
        self.is_machine_data = None  # returned data from Readin.machines()
        self.initial_state = None

        ''' series '''
        self._series = []
        self._series_opt = series

        self.__initialize()

        if mtype in Measurement.measurement_formatters():
            self.logger.debug('MTYPE << %s >> implemented' % mtype)
            self.mtype = mtype  # set mtype

            if mdata is not None:  # we have mdata -> ignore mfile and just use that data directly
                self.logger.debug('mdata passed -> using as measurement data without formatting')
                self.sample_obj = sample_obj
                self._data = mdata
                return  # done
            if machine in Measurement.measurement_formatters()[mtype] or machine == 'combined':
                self.logger.debug('MACHINE << %s >> implemented' % machine)
                self.machine = machine  # set machine
                self.sample_obj = sample_obj  # set sample_obj
                if not mfile:
                    self.logger.debug('NO machine or mfile passed -> no raw_data will be generated')
                    return
                else:
                    self.mfile = mfile
                    self.import_data()
                    self.has_data = self.machine_data.has_data
                    if not self.machine_data.has_data:
                        self.logger.error('NO DATA passed: check sample name << %s >>' % sample_obj.name)
            else:
                self.logger.error('UNKNOWN MACHINE: << %s >>' % machine)
                self.logger.error(
                    'most likely cause is the \"format_%s\" method is missing in the measurement << %s >>' % (
                        machine, mtype))
        else:
            self.logger.error('UNKNOWN\t MTYPE: << %s >>' % mtype)


        # dynamic data formatting
        # checks if format_'machine_name' exists. If exists it formats self.raw_data according to format_'machine_name'
        if machine == 'combined':
            pass
        elif callable(getattr(self, 'format_' + machine)):
            if self.has_data:
                self.logger.debug('FORMATTING raw data from << %s >>' % machine)
                getattr(self, 'format_' + machine)()
            else:
                self.logger.debug('NO raw data transfered << %s >>' % machine)
        else:
            self.logger.error(
                'FORMATTING raw data from << %s >> not possible, probably not implemented, yet.' % machine)

        # add series if provied
        # has to come past __initialize()
        if self._series_opt:
            self._add_series_from_opt()

    @property
    def m_idx(self):
        return self.sample_obj.measurements.index(self)

    @property
    def fname(self):
        """
        Returns only filename from self.file

        Returns
        -------
           str: filename from full path
        """
        return os.path.split(self.mfile)[-1]

    def __initialize(self):
        """
        Initialize function is called inside the __init__ function, it is also called when the object is reconstructed
        with pickle.

        :return:
        """


        # dynamical creation of entries in results data. One column for each results_* method.
        # calculation_* methods are not creating columns -> if a result is calculated a result_* method
        # has to be written
        self.result_methods = [i[7:] for i in dir(self) if i.startswith('result_') if
                               not i.endswith('generic') if
                               not i.endswith('result')]  # search for implemented results methods

        self.results = RockPyData(
            column_names=self.result_methods,
            data=[np.nan for i in self.result_methods])  # dynamic entry creation for all available result methods

        # ## warning with calculation of results:
        # M.result_slope() -> 1.2
        # M.calculate_vds(t_min=300) -> ***
        # M.results['slope'] -> 1.2
        # M.result_slope(t_min=300) -> 0.9
        #
        # the results are stored for the calculation parameters that were used to calculate it.
        # This means calculating a different result with different parameters can lead to inconsistencies.
        # One has to be aware that comparing the two may not be useful

        # dynamically generating the calculation and standard parameters for each calculation method.
        # This just sets the values to non, the values have to be specified in the class itself
        self.calculation_methods = [i for i in dir(self) if i.startswith('calculate_') if not i.endswith('generic')]
        self.calculation_parameter = {i: dict() for i in self.result_methods}
        self._standard_parameter = {i[10:]: None for i in dir(self) if i.startswith('calculate_') if
                                    not i.endswith('generic')}

        if self._series:
            for t in self._series:
                self._add_sval_to_results(t)
        # self._add_sval_to_data(t)

        self.is_normalized = False  # normalized flag for visuals, so its not normalized twize
        self.norm = None  # the actual parameters

        self._info_dict = self.__create_info_dict()

    def __getstate__(self):
        '''
        returned dict will be pickled
        :return:
        '''
        pickle_me = {k: v for k, v in self.__dict__.iteritems() if k in
                     (
                         'mtype', 'machine', 'mfile',
                         'has_data', 'machine_data',
                         '_raw_data', '_data',
                         'initial_state', 'is_initial_state',
                         'sample_obj',
                         '_series_opt', '_series',
                         'suffix',
                     )
                     }
        return pickle_me

    def __setstate__(self, d):
        '''
        d is unpickled data
           d:
        :return:
        '''
        self.__dict__.update(d)
        self.__initialize()

    def reset__data(self, recalc_mag=False):
        pass

    def __getattr__(self, attr):
        # print attr, self.__dict__.keys()
        if attr in self.__getattribute__('_data').keys():
            return self._data[attr]
        if attr in self.__getattribute__('result_methods'):
            return getattr(self, 'result_' + attr)().v[0]
        raise AttributeError(attr)

    def import_data(self, rtn_raw_data=None, **options):
        '''
        Importing the data from mfile and machine
           rtn_raw_data:
           options:
        :return:
        '''

        self.logger.info('IMPORTING << %s , %s >> data' % (self.machine, self.mtype))

        machine = options.get('machine', self.machine)
        mtype = options.get('mtype', self.mtype)
        mfile = options.get('mfile', self.mfile)
        raw_data = self.measurement_formatters()[mtype][machine](mfile, self.sample_obj.name)
        if raw_data is None:
            self.logger.error('IMPORTING\t did not transfer data - CHECK sample name and data file')
            return
        else:
            if rtn_raw_data:
                self.logger.info('RETURNING raw_data for << %s , %s >> data' % (machine, mtype))
                return raw_data
            else:
                self.machine_data = raw_data


    def set_initial_state(self,
                          mtype, mfile, machine,  # standard
                          **options):
        """
        creates a new measurement (ISM) as initial state of base measurement (BSM).
        It dynamically calls the measurement _init_ function and assigns the created measurement to the
        self.initial_state value. It also sets a flag for the ISM to check if a measurement is a MIS.

        Parameters
        ----------
           mtype: str
              measurement type
           mfile: str
              measurement data file
           machine: str
              measurement machine
           options:
        """
        mtype = mtype.lower()
        machnine = machine.lower()

        self.logger.info('CREATING << %s >> initial state measurement << %s >> data' % (mtype, self.mtype))
        implemented = {i.__name__.lower(): i for i in Measurement.inheritors()}

        # can only be created if the measurement is actually implemented
        if mtype in implemented:
            self.initial_state = implemented[mtype](self.sample_obj, mtype, mfile, machine)
            self.initial_state.is_initial_state = True
        else:
            self.logger.error('UNABLE to find measurement << %s >>' % (mtype))

    ### INFO DICTIONARY

    @property
    def info_dict(self):
        if not hasattr(self,'_info_dict'):
            self._info_dict = self.__create_info_dict()
        if not all( i in self._info_dict['series'] for i in self.series):
            self._recalc_info_dict()
        return self._info_dict

    def __create_info_dict(self):
        """
        creates all info dictionaries

        Returns
        -------
           dict
              Dictionary with a permutation of ,type, stype and sval.
        """
        d = ['stype', 'sval']
        keys = ['_'.join(i) for n in range(3) for i in itertools.permutations(d, n) if not len(i) == 0]
        out = {i: {} for i in keys}
        out.update({'series': []})
        return out

    def _recalc_info_dict(self):
        """
        Re-calculates the info_dictionary for the measurement
        """
        self._info_dict = self.__create_info_dict()
        map(self.add_s2_info_dict, self.series)

    def add_s2_info_dict(self, series):
        """
        adds a measurement to the info dictionary.

        Parameters
        ----------
           series: RockPy.Series
              Series to be added to the info_dictionary
        """

        if not series in self._info_dict['series']:
            self._info_dict['stype'].setdefault(series.stype, []).append(self)
            self._info_dict['sval'].setdefault(series.value, []).append(self)

            self._info_dict['sval_stype'].setdefault(series.value, {})
            self._info_dict['sval_stype'][series.value].setdefault(series.stype, []).append(self)
            self._info_dict['stype_sval'].setdefault(series.stype, {})
            self._info_dict['stype_sval'][series.stype].setdefault(series.value, []).append(self)

            self._info_dict['series'].append(series)

    @property
    def stypes(self):
        """
        list of all stypes
        """
        out = [t.stype for t in self.series]
        return self.__sort_list_set(out)

    @property
    def svals(self):
        """
        list of all stypes
        """
        out = [t.value for t in self.series]
        return self.__sort_list_set(out)

    @property
    def stype_dict(self):
        """
        dictionary of stype: series}
        """
        out = {t.stype: t for t in self.series}
        return out

    @property
    def tdict(self):
        """
        dictionary of stype: series}
        """
        out = {t.stype: t.value for t in self.series}
        return out

    @property
    def _self_tdict(self):
        """
        dictionary of stype: {svalue: self}
        """
        out = {i.stype: {i.value: self} for i in self.series}
        return out


    @property
    def data(self):
        if not self._data:
            self._data = deepcopy(self._raw_data)
        return self._data

    # ## DATA RELATED
    ### Calculation and parameters

    def result_generic(self, recalc=False):
        '''
        Generic for for result implementation. Every calculation of result should be in the self.results data structure
        before calculation.
        It should then be tested if a value for it exists, and if not it should be created by calling
        _calculate_result_(result_name).

        '''
        parameter = {}

        self.calc_result(parameter, recalc)
        return self.results['generic']

    def calculate_generic(self, **parameter):
        '''
        actual calculation of the result

        :return:
        '''

        self.results['generic'] = 0

    def calculate_result(self, result, **parameter):
        """
        Helper function to dynamically call a result. Used in VisualizeV3

        Parameters
        ----------
           result:
           parameter:
        """

        if not self.has_result(result):
            self.logger.warning('%s does not have result << %s >>' % self.mtype, result)
            return
        else:
            # todo figuer out why logger wrong when called from VisualizeV3
            self.logger = logging.getLogger('RockPy.MEASURMENT.' + self.mtype+'[%s]'%self.sample_obj.name)
            self.logger.info('CALCULATING << %s >>' % result)
            out = getattr(self, 'result_'+result)(**parameter)
        return out


    def calc_generic(self, **parameter):
        '''
        helper function
        actual calculation of the result

        :return:
        '''

        self.results['generic'] = 0

    def calc_result(self, parameter=None, recalc=False, force_method=None):
        '''
        Helper function:
        Calls any calculate_* function, but checks first:

            1. does this calculation method exist
            2. has it been calculated before

               NO : calculate the result

               YES: are given parameters equal to previous calculation parameters

               if YES::

                  NO : calculate result with new parameters
                  YES: return previous result

           parameter: dict
                        dictionary with parameters needed for calculation
           force_caller: not dynamically retrieved caller name.

        :return:
        '''
        if not parameter: parameter = dict()
        caller = '_'.join(inspect.stack()[1][3].split('_')[1:])  # get calling function

        if force_method is not None:
            method = force_method  # method for calculation if any: result_CALLER_method
        else:
            method = caller  # if CALLER = METHOD

        if callable(getattr(self, 'calculate_' + method)):  # check if calculation function exists
            # check for None and replaces it with standard
            parameter = self.compare_parameters(method, parameter, recalc)
            if self.results[caller] is None or self.results[
                caller] == np.nan or recalc:  # if results dont exist or force recalc
                if recalc:
                    self.logger.debug('FORCED recalculation of << %s >>' % (method))
                else:
                    self.logger.debug('CANNOT find result << %s >> -> calculating' % (method))
                getattr(self, 'calculate_' + method)(**parameter)  # calling calculation method
            else:
                self.logger.debug('FOUND previous << %s >> parameters' % (method))
                if self.check_parameters(caller, parameter):  # are parameters equal to previous parameters
                    self.logger.debug('RESULT parameters different from previous calculation -> recalculating')
                    getattr(self, 'calculate_' + method)(**parameter)  # recalculating if parameters different
                else:
                    self.logger.debug('RESULT parameters equal to previous calculation')
        else:
            self.logger.error(
                'CALCULATION of << %s >> not possible, probably not implemented, yet.' % method)

    def calc_all(self, **parameter):
        parameter['recalc'] = True
        for result_method in self.result_methods:
            getattr(self, 'result_' + result_method)(**parameter)
        return self.results

    def compare_parameters(self, caller, parameter, recalc):
        """
        checks if given parameter[key] is None and replaces it with standard parameter or calculation_parameter.

        e.g. calculation_generic(A=1, B=2)
             calculation_generic() # will calculate with A=1, B=2
             calculation_generic(A=3) # will calculate with A=3, B=2
             calculation_generic(A=2, recalc=True) # will calculate with A=2 B=standard_parameter['B']

           caller: str
                     name of calling function ('result_generic' should be given as 'generic')
           parameter:
                        Parameters to check
           recalc: Boolean
                     True if forced recalculation, False if not
        :return:
        """
        # caller = inspect.stack()[1][3].split('_')[-1]

        for key, value in parameter.iteritems():
            if value is None:
                if self.calculation_parameter[caller] and not recalc:
                    parameter[key] = self.calculation_parameter[caller][key]
                else:
                    parameter[key] = self.standard_parameter[caller][key]
        return parameter

    def delete_dtype_var_val(self, dtype, var, val):
        """
        deletes step with var = var and val = val

           dtype: the step type to be deleted e.g. th
           var: the variable e.g. temperature
           val: the value of that step e.g. 500

        example: measurement.delete_step(step='th', var='temp', val=500) will delete the th step where the temperature is 500
        """
        idx = self._get_idx_dtype_var_val(dtype=dtype, var=var, val=val)
        self.data[dtype] = self.data[dtype].filter_idx(idx, invert=True)
        return self

    def check_parameters(self, caller, parameter):
        '''
        Checks if previous calculation used the same parameters, if yes returns the previous calculation
        if no calculates with new parameters

           caller: str
           name of calling function ('result_generic' should be given as 'result')
           parameter:
        :return:
        '''
        if self.calculation_parameter[caller]:
            a = [parameter[i] for i in self.calculation_parameter[caller]]
            b = [self.calculation_parameter[caller][i] for i in self.calculation_parameter[caller]]
            if a != b:
                return True
            else:
                return False
        else:
            return True

    def has_result(self, result):
        """
        Checks if the measurement contains a certain result

        Parameters
        ----------
           result: str
              the result that should be found e.g. result='ms' would give True for 'hys' and 'backfield'
        Returns
        -------
           out: bool
              True if it has result, False if not
        """
        if result in self.result_methods:
            return True
        else:
            return False

    ### series RELATED
    def has_series(self, stype=None, sval=None):
        """
        checks if a measurement actually has a series
        :return:
        """
        if self._series and not stype:
            return True
        if self._series and self.get_series(stypes=stype, svals=sval):
            return True
        else:
            return False

    @property
    def series(self):
        if self.has_series():
            return self._series
        else:
            series = RockPy.Series(stype='none', value=np.nan, unit='')
            return [series]

    def _get_series_from_suffix(self):
        """
        takes a given suffix and extracts series data-for quick assessment. For more series control
        use add_series method.

        suffix must be given in the form of
            stype: s_value [s_unit] | next series...
        :return:
        """
        if self.suffix:
            s_type = self.suffix.split(':')[0]
            if len(s_type) > 1:
                s_value = float(self.suffix.split()[1])
                try:
                    s_unit = self.suffix.split('[')[1].strip(']')
                except IndexError:
                    s_unit = None
                return s_type, s_value, s_unit
        else:
            return None

    def _add_series_from_opt(self):
        """
        Takes series specified in options and adds them to self.series
        :return:
        """
        series = self._get_series_from_opt()
        for t in series:
            self.add_svalue(stype=t[0], sval=t[1], unit=t[2])

    def _get_series_from_opt(self):
        """
        creates a list of series from the series option

        e.g. Pressure_1_GPa;Temp_200_C
        :return:
        """
        if self._series_opt:
            series = self._series_opt.replace(' ', '').replace(',', '.').split(';')  # split ; for multiple series
            series = [i.split('_') for i in series]  # split , for type, value, unit
            for i in series:
                try:
                    i[1] = float(i[1])
                except:
                    raise TypeError('%s can not be converted to float' % i)
        else:
            series = None
        return series

    def get_series(self, stypes=None, svals=None):
        """
        searches for given stypes and svals in self.series and returns them

        Parameters
        ----------
           stypes: list, str
              stype or stypes to be looked up
           svals: float
              sval or svals to be looked up

        Returns
        """
        out = self.series
        if stypes:
            stypes = to_list(stypes)
            out = [i for i in out if i.stype in stypes]
        if svals:
            svals = to_list(map(float, svals))
            out = [i for i in out if i.value in svals]
        return out

    def add_svalue(self, stype, sval, unit=None, comment=''):
        """
        adds a series to measurement.series, then adds is to the data and results datastructure
        
        Parameters
        ----------
           stype: str
              series type to be added
           sval: float or int
              series value to be added
           unit: str
              unit to be added. can be None #todo change so it uses Pint
           comment: str
              adds a comment to the series

        Returns
        -------
           RockPy.Series instance
        """
        series = RockPy.Series(stype=stype, value=sval, unit=unit, comment=comment)
        self._series.append(series)
        self._add_sval_to_data(series)
        self._add_sval_to_results(series)
        print self.sample_obj
        self.sample_obj.add_series2_mdict(series=series, mobj=self)
        return series

    def _add_sval_to_data(self, sobj):
        """
        Adds stype as a column and adds svals to data. Only if stype != none.

        Parameter
        ---------
           sobj: series instance
        """
        if sobj.stype != 'none':
            for dtype in self._raw_data:
                if self._raw_data[dtype]:
                    data = np.ones(len(self.data[dtype]['variable'].v)) * sobj.value
                    if not 'stype ' + sobj.stype in self.data[dtype].column_names:
                        self.data[dtype] = self.data[dtype].append_columns(column_names='stype ' + sobj.stype,
                                                                           data=data)  # , unit=sobj.unit) #todo add units

    def _add_sval_to_results(self, sobj):
        """
        Adds the stype as a column and the value as value to the results. Only if stype != none.

        Parameter
        ---------
           sobj: series instance
        """
        if sobj.stype != 'none':
            # data = np.ones(len(self.results['variable'].v)) * sobj.value
            if not 'stype ' + sobj.stype in self.results.column_names:
                self.results = self.results.append_columns(column_names='stype ' + sobj.stype,
                                                           data=[sobj.value])  # , unit=sobj.unit) #todo add units

    def __sort_list_set(self, values):
        """
        returns a sorted list of non duplicate values
           values:
        :return:
        """
        return sorted(list(set(values)))

    def _get_idx_dtype_var_val(self, dtype, var, val, *args):
        """
        returns the index of the closest value with the variable(var) and the step(step) to the value(val)

        option: inverse:
           returns all indices except this one

        """
        out = [np.argmin(abs(self.data[dtype][var].v - val))]
        return out

    """
    Normalize functions
    +++++++++++++++++++
    """

    def normalize(self, reference='data', ref_dtype='mag', norm_dtypes='all', vval=None, norm_method='max',
                  normalize_variable=False, dont_normalize=None):
        """
        normalizes all available data to reference value, using norm_method

        Parameter
        ---------
           reference: str
              reference state, to which to normalize to e.g. 'NRM'
              also possible to normalize to mass
           ref_dtype: str
              component of the reference, if applicable. standard - 'mag'
           norm_dtypes: list
              dtype to be normalized, if dtype = 'all' all variables will be normalized
           vval: float
              variable value, if reference == value then it will search for the point closest to the vval
           norm_method: str
              how the norm_factor is generated, could be min
           normalize_variable: bool
              if True, variable is also normalized
              default: False
           dont_normalize: list
              list of dtypes that will not be normalized
              default: None
        """
        # todo normalize by results
        #getting normalization factor
        norm_factor = self._get_norm_factor(reference, ref_dtype, vval, norm_method)
        norm_dtypes = _to_tuple(norm_dtypes)  # make sure its a list/tuple
        for dtype, dtype_data in self.data.iteritems():  #cycling through all dtypes in data
            if dtype_data: #if dtype_data == None
                if 'all' in norm_dtypes:  # if all, all non stype data will be normalized
                    norm_dtypes = [i for i in dtype_data.column_names if not 'stype' in i]

                ### DO not normalize:
                # variable
                if not normalize_variable:
                    variable = dtype_data.column_names[dtype_data.column_dict['variable'][0]]
                    norm_dtypes = [i for i in norm_dtypes if not i == variable]

                if dont_normalize:
                    dont_normalize = _to_tuple(dont_normalize)
                    norm_dtypes = [i for i in norm_dtypes if not i in dont_normalize]

                for ntype in norm_dtypes:  #else use norm_dtypes specified
                    try:
                        dtype_data[ntype] = dtype_data[ntype].v / norm_factor
                    except KeyError:
                        self.logger.warning('CAN\'T normalize << %s, %s >> to %s' %(self.sample_obj.name, self.mtype, ntype))

                if 'mag' in dtype_data.column_names:
                    try:
                        self.data[dtype]['mag'] = self.data[dtype].magnitude(('x', 'y', 'z'))
                    except:
                        self.logger.debug('no (x,y,z) data found keeping << mag >>')

        if self.initial_state:
            for dtype, dtype_rpd in self.initial_state.data.iteritems():
                self.initial_state.data[dtype] = dtype_rpd / norm_factor
                if 'mag' in self.initial_state.data[dtype].column_names:
                    self.initial_state.data[dtype]['mag'] = self.initial_state.data[dtype].magnitude(('x', 'y', 'z'))
        return self

    def normalizeOLD(self, reference='data', rtype='mag', dtype='mag', vval=None, norm_method='max'):
        """
        normalizes all available data to reference value, using norm_method

        Parameter
        ---------
           reference: str
              reference state, to which to normalize to e.g. 'NRM'
              also possible to normalize to mass
            rtype: str
               component of the reference, if applicable. standard - 'mag'
            dtype: str
               dtype to be normalized, if dtype = 'all' all variables will be normalized
            vval: float
               variable value, if reference == value then it will search for the point closest to the vval
            norm_method: str
               how the norm_factor is generated, could be min
        """

        norm_factor = self._get_norm_factor(reference, rtype, vval, norm_method)
        for dtype, dtype_rpd in self.data.iteritems():
            stypes = [i for i in dtype_rpd.column_names if 'stype' in i]
            self.data[dtype] = dtype_rpd / norm_factor
            if stypes:
                for tt in stypes:
                    self.data[dtype][tt] = np.ones(len(dtype_rpd['variable'].v)) * self.stype_dict[tt[6:]].value
            if 'mag' in self.data[dtype].column_names:
                try:
                    self.data[dtype]['mag'] = self.data[dtype].magnitude(('x', 'y', 'z'))
                except:
                    self.logger.debug('no (x,y,z) data found keeping << mag >>')

        if self.initial_state:
            for dtype, dtype_rpd in self.initial_state.data.iteritems():
                self.initial_state.data[dtype] = dtype_rpd / norm_factor
            if 'mag' in self.initial_state.data[dtype].column_names:
                self.initial_state.data[dtype]['mag'] = self.initial_state.data[dtype].magnitude(('x', 'y', 'z'))

        self.is_normalized = True
        self.norm = [reference, rtype, vval, norm_method, norm_factor]
        return self

    def _get_norm_factor(self, reference, rtype, vval, norm_method):
        """
        Calculates the normalization factor from the data according to specified input

        Parameter
        ---------
           reference: str
              the type of data to be referenced. e.g. 'NRM' -> norm_factor will be calculated from self.data['NRM']
              if not given, will return 1
           rtype:
           vval:
           norm_method:

        Returns
        -------
           normalization factor: float
        """
        norm_factor = 1  # inititalize

        if reference:
            if reference == 'nrm' and reference not in self.data and 'data' in self.data:
                reference = 'data'

            if reference in self.data:
                norm_factor = self._norm_method(norm_method, vval, rtype, self.data[reference])

            if reference in ['is', 'initial', 'initial_state']:
                if self.initial_state:
                    norm_factor = self._norm_method(norm_method, vval, rtype, self.initial_state.data['data'])
                if self.is_initial_state:
                    norm_factor = self._norm_method(norm_method, vval, rtype, self.data['data'])

            if reference == 'mass':
                m = self.get_mtype_prior_to(mtype='mass')
                norm_factor = m.data['data']['mass'].v[0]

            if isinstance(reference, float) or isinstance(reference, int):
                norm_factor = float(reference)
        return norm_factor

    def _norm_method(self, norm_method, vval, rtype, data):
        methods = {'max': max,
                   'min': min,
                   # 'val': self.get_val_from_data,
                   }
        if not vval:
            if not norm_method in methods:
                raise NotImplemented('NORMALIZATION METHOD << %s >>' % norm_method)
                return
            else:
                return methods[norm_method](data[rtype].v)

        if vval:
            idx = np.argmin(abs(data['variable'].v - vval))
            out = data.filter_idx([idx])[rtype].v[0]
            return out

    def get_mtype_prior_to(self, mtype, include_parameter_m = False):
        """
        search for last mtype prior to self

        Parameters
        ----------
           mtype: str
              the type of measurement that is supposed to be returned
           include_parameter_m: bool
              if True measurements from the parameter category are also normalized. e.g. mass, volume, length...

        Returns
        -------
           RockPy.Measurement
        """
        measurements = self.sample_obj.get_measurements(mtype)
        if measurements:
            out = [i for i in measurements if i.m_idx <= self.m_idx]
            return out[-1]
        else:
            return None

    def _add_stype_to_results(self):
        """
        adds a column with stype stype.name to the results for each stype in measurement.series
        :return:
        """
        if self._series:
            for t in self.series:
                if t.stype:
                    if t.stype not in self.results.column_names:
                        self.results.append_columns(column_names='stype ' + t.stype,
                                                    data=t.value,
                                                    # unit = t.unit      # todo add units
                                                    )

    def get_series_labels(self):
        out = ''
        if self.has_series():
            for series in self.series:
                if not str(series.value) + ' ' + series.unit in out:
                    out += str(series.value) + ' ' + series.unit
                    out += ' '
        return out

    """
    CORRECTIONS
    """

    def correct_dtype(self, dtype='th', var='variable', val='last', initial_state=True):
        """
        corrects the remaining moment from the last th_step

           dtype:
           var:
           val:
           initial_state: also corrects the iinitial state if one exists
        """

        try:
            calc_data = self.data[dtype]
        except KeyError:
            self.log.error('REFERENCE << %s >> can not be found ' % (dtype))

        if val == 'last':
            val = calc_data[var].v[-1]
        if val == 'first':
            val = calc_data[var].v[0]

        idx = self._get_idx_dtype_var_val(step=dtype, var=var, val=val)

        correction = self.data[dtype].filter_idx(idx)  # correction step

        for dtype in self.data:
            # calculate correction
            self._data[dtype]['m'] = self._data[dtype]['m'].v - correction['m'].v
            # recalc mag for safety
            self.data[dtype]['mag'] = self.data[dtype].magnitude(('x', 'y', 'z'))
        self.reset__data()

        if self.initial_state and initial_state:
            for dtype in self.initial_state.data:
                self.initial_state.data[dtype]['m'] = self.initial_state.data[dtype]['m'].v - correction['m'].v
                self.initial_state.data[dtype]['mag'] = self.initial_state.data[dtype].magnitude(('x', 'y', 'z'))
        return self


    '''' PLOTTING '''''

    @property
    def plottable(self):
        """
        returns a list of all possible Visuals for this measurement
        :return:
        """
        out = {}
        for visual in RockPy.Visualize.base.Generic.inheritors():
            if visual._required == [self.mtype]:
                out.update({visual.__name__: visual})
        return out

    def show_plots(self):
        for visual in self.plottable:
            self.plottable[visual](self, show=True)

    def set_get_attr(self, attr, value=None):
        """
        checks if attribute exists, if not, creates attribute with value None
           attr:
        :return:
        """
        if not hasattr(self, attr):
            setattr(self, attr, value)
        return getattr(self, attr)