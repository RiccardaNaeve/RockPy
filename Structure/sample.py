# coding=utf-8
from copy import deepcopy
import itertools
import logging

import os.path
import numpy as np
import tabulate
from profilehooks import profile

from RockPy.core import to_list
from RockPy.Measurements.base import Measurement
from RockPy.Structure.data import RockPyData, condense
import RockPy.Visualize.base
# RockPy.Functions.general.create_logger(__name__)

class Sample(object):
    """
    Sample in a way a container for measurements
    """
    logger = logging.getLogger('RockPy.Sample')
    snum = 0

    @classmethod
    def implemented_measurements(cls):
        return {i.__name__.lower(): i for i in Measurement.inheritors()}

    def __init__(self, name,
                 mass=None, mass_unit='kg', mass_machine='generic',
                 height=None, diameter=None,
                 x_len=None, y_len=None, z_len=None,  # for cubic samples
                 length_unit='mm', length_machine='generic',
                 sample_shape='cylinder',
                 color=None, comment='',
                 **options):
        """
        Parameters
        ----------
           name: str
              name of the sample.
           mass: float
              mass of the sample. If not kg then please specify the mass_unit. It is stored in kg.
           mass_unit: str
              has to be specified in order to calculate the sample mass properly.
           height: float
              sample height - stored in 'm'
           diameter: float
              sample diameter - stored in 'm'
           length_unit: str
              if not 'm' please specify
           length_machine: str
              if not 'm' please specify
           sample_shape: str
              needed for volume calculation
              cylinder: needs height, diameter
              cube: needs x_len, y_len, z_len
              sphere: diameter
           color: color
              used in plots if specified
        """
        self.color = color
        self.name = name
        self.comment = comment

        Sample.logger.info('CREATING\t new sample << %s >>' % self.name)
        self.logger = logging.getLogger('RockPy.Sample[%s]' % name)

        self.raw_measurements = []
        self.measurements = []
        self.results = None

        ''' is sample is a mean sample from sample_goup ect... '''
        self.is_mean = False  # if a calculated mean_sample
        self.mean_measurements = []
        self._mean_results = None
        self._filtered_data = None
        self._info_dict = self.__create_info_dict()

        if mass is not None:
            mass = self.add_measurement(mtype='mass', mfile=None, machine=mass_machine,
                                        value=float(mass), unit=mass_unit)
        if diameter is not None:
            diameter = self.add_measurement(mtype='diameter', mfile=None, machine=length_machine,
                                            value=float(diameter), unit=length_unit)
        if height is not None:
            height = self.add_measurement(mtype='height', mfile=None, machine=length_machine,
                                          value=float(height), unit=length_unit)

        if x_len is not None:
            x_len = self.add_measurement(mtype='length', mfile=None, machine=length_machine,
                                         value=float(x_len), unit=length_unit, direction='x')
        if y_len is not None:
            y_len = self.add_measurement(mtype='length', mfile=None, machine=length_machine,
                                         value=float(y_len), unit=length_unit, direction='y')
        if z_len is not None:
            z_len = self.add_measurement(mtype='length', mfile=None, machine=length_machine,
                                         value=float(z_len), unit=length_unit, direction='z')

        if height and diameter:
            self.add_measurement(mtype='volume', sample_shape=sample_shape, height=height, diameter=diameter)
        if x_len and y_len and z_len:
            self.add_measurement(mtype='volume', sample_shape=sample_shape, x_len=x_len, y_len=y_len, z_len=z_len)

        self.index = Sample.snum
        self.sgroups = []
        self.study = None
        Sample.snum += 1

    """ Parameter """

    @property
    def mass(self):
        """
        Searches for last mass measurement and returns value in kg
        :return:
        """
        m = self.get_measurements(mtype='mass')[-1]
        return m.data['data']['mass'].v[0]

    @property
    def volume(self):
        """
        Searches for last volume measurement and returns value in m^3
        :return:
        """
        m = self.get_measurements(mtype='volume')[-1]
        return m.data['data']['volume'].v[0]

    """ INFO DICTIONARY """

    def __create_info_dict(self):
        """
        creates all info dictionaries

        Returns
        -------
           dict
              Dictionary with a permutation of ,type, stype and sval.
        """
        d = ['mtype', 'stype', 'sval']
        keys = ['_'.join(i) for n in range(4) for i in itertools.permutations(d, n) if not len(i) == 0]
        out = {i: {} for i in keys}
        return out

    def add_m2_info_dict(self, m):
        keys = self._info_dict.keys()
        for t in m.series:
            test = {'mtype': m.mtype, 'stype': t.stype, 'sval': t.value}
            for key in keys:
                levels = key.split('_')
                for i, level in enumerate(levels):
                    if i == 0:
                        if len(levels) == i + 1:
                            if not test[level] in self._info_dict[key]:
                                self._info_dict[key][test[level]] = []
                            self._info_dict[key][test[level]].append(m)
                        else:
                            if not test[level] in self._info_dict[key]:
                                self._info_dict[key][test[level]] = {}
                    if i == 1:
                        if len(levels) == i + 1:
                            if not test[level] in self._info_dict[key][test[levels[0]]]:
                                self._info_dict[key][test[levels[0]]][test[level]] = []
                            self._info_dict[key][test[levels[0]]][test[level]].append(m)
                        else:
                            if not test[level] in self._info_dict[key][test[levels[0]]]:
                                self._info_dict[key][test[levels[0]]][test[level]] = {}
                    if i == 2:
                        if len(levels) == i + 1:
                            if not test[level] in self._info_dict[key][test[levels[0]]][test[levels[1]]]:
                                self._info_dict[key][test[levels[0]]][test[levels[1]]][test[level]] = []
                            self._info_dict[key][test[levels[0]]][test[levels[1]]][test[level]].append(m)

    def recalc_info_dict(self):
        """
        calculates a dictionary with information and the corresponding measurement

        :return:

        """
        self._info_dict = self.__create_info_dict()
        map(self.add_m2_info_dict, self.measurements)

    """ PICKL """

    def __setstate__(self, d):
        self.__dict__.update(d)
        # self.recalc_info_dict()

    def __getstate__(self):
        '''
        returned dict will be pickled
        :return:
        '''
        pickle_me = {k: v for k, v in self.__dict__.iteritems() if k in
                     (
                         'name', 'index', 'color',
                         'measurements',
                         '_filtered_data', 'sgroups',
                         '_info_dict',
                         'is_mean', 'mean_measurements', '_mean_results',
                         'results',
                     )}
        return pickle_me

    @property
    def filtered_data(self):
        if not self._filtered_data:
            if self.is_mean:
                return self.mean_measurements
            else:
                return self.measurements
        else:
            return self._filtered_data

    def mean_results(self, **parameter):
        if not self._mean_results:
            self.calc_all_mean_results(**parameter)
        return self._mean_results

    def __repr__(self):
        return '<< %s - RockPy.Sample >>' % self.name

    def __add__(self, other):
        first = deepcopy(self)

        for m in other.measurements:
            m.sample_obj = first

        first.measurements.extend(other.measurements)
        first.recalc_info_dict()
        return first

    ''' ADD FUNCTIONS '''

    def add_measurement(self,
                        mtype=None, mfile=None, machine='generic',  # general
                        fname=None, folder=None, path=None, # added for automatic import of pathnames
                        idx=None, mdata=None,
                        create_parameter = False,
                        **options):
        '''
        All measurements have to be added here

        Parameters
        ----------
           mtype: str
              the type of measurement
              default: None
           mfile: str
              the measurement file
              default: None
           machine: str
              the machine from which the file is output
              default: 'generic
           idx: index of measurement
              default: None, will be the index of the measurement in sample_obj.measurements
           fname: str
              filename
              default: None
           folder: str
              folder
              default: None
           path: str
              full path. equivalent to os.path.join(folder, fname)
              default: None
           mdata: any kind of data that must fit the required structure of the data of the measurement
                    will be used instead of data from file
           create_parameter: bool
              default: False
              if true it will create the parameter (lenght, mass) measurements before creating the actual measurement


        Returns
        -------
            RockPy.measurement object

        :mtypes:

        - mass
        '''

        file_info = None

        if idx is None:
            idx = len(self.measurements)  # if there is no measurement index

        # if auomatic import through filename is needed:
        # either fname AND folder are given OR the full path is passed
        # then the file_info dictionary is created

        if fname and folder or path:
            if fname and folder:
                path = os.path.join(folder, fname)
            if path:
                file_info = RockPy.get_info_from_fname(path=path)
            file_info.update(dict(sample_obj=self))

        elif mtype:
            mtype = mtype.lower()
            file_info = dict(sample_obj=self,
                             mtype=mtype, mfile=mfile, machine=machine,
                             m_idx=idx, mdata=mdata)
        if options:
            file_info.update(options)

        if file_info:
            mtype = file_info['mtype']
            if mtype in Sample.implemented_measurements():
                self.logger.info(' ADDING\t << measurement >> %s' % mtype)
                measurement = Sample.implemented_measurements()[mtype](**file_info)
                if measurement.has_data:
                    self.measurements.append(measurement)
                    self.raw_measurements.append(measurement)  # todo is it better to store a deepcopy, so you could have a reset_measurement to get rid of possible mistakes?
                    self.add_m2_info_dict(measurement)
                    return measurement
                else:
                    return None
            else:
                self.logger.error(' << %s >> not implemented, yet' % mtype)


    def add_simulation(self, mtype, sim_param=None, idx=None, **options):
        """
        add simulated measurements

        Parameters
        ----------
           mtype: str - the type of simulated measurement
           idx:
           sim_param: dict of parameters to specifiy simulation
        :return: RockPy.measurement object
        """
        mtype = mtype.lower()

        implemented = {i.__name__.lower(): i for i in Measurement.inheritors()}

        if idx is None:
            idx = len(self.measurements)  # if there is no measurement index

        if mtype in implemented:
            self.logger.info(' ADDING\t << simulated measurement >> %s' % mtype)
            measurement = implemented[mtype].simulate(self, m_idx=idx, **options)
            if measurement.has_data:
                self.measurements.append(measurement)
                return measurement
            else:
                return None
        else:
            self.logger.error(' << %s >> not implemented, yet' % mtype)

    def calc_all(self, **parameter):
        """
        Calculates all results using specified parameter for all available measurements

        Parameters
        ----------
           parameter: calculation parameter e.g. t_min, t_max @ Thellier-Thellier

        Returns
        -------
           RockPyData
              containing all results calculated possible

        Notes
        -----
           always recalculates everything

        """
        self.results = self.all_results(**parameter)
        return self.results

    @property
    def info_dict(self):
        # if not hasattr(self, '_info_dict'):
        # self.recalc_info_dict()
        return self._info_dict

    @property
    def mtypes(self):
        """
        returns list of all mtypes
        """
        return sorted(self._info_dict['mtype'].keys())

    @property
    def stypes(self):
        """
        returns a list of all stypes
        """
        return sorted(self._info_dict['stype'].keys())

    @property
    def svals(self):
        """
        returns a list of all stypes
        """

        return sorted(self._info_dict['sval'].keys())

    @property
    def mtype_tdict(self):  # todo: delete?
        """
        dictionary with all measurement_types {mtype:[tretments to corresponding m]}
        """
        out = {}
        for mtype in self.mtypes:
            aux = []
            for m in self.get_measurements(mtype=mtype):
                aux.extend(m.series)
            out.update({mtype: aux})
        return out

    @property
    def stype_dict(self):
        """
        dictionary with all series_types {stype:[list of measurements]}

        example:
        >>> {'pressure': [<RockPy.Measurements.parameters.Mass object at 0x10e196150>, <RockPy.Measurements.parameters.Diameter object at 0x10e1962d0>]}
        """
        return self._info_dict['stype']

    @property
    def mtype_stype_dict(self):
        """
        returns a dictionary of mtypes, with all stypes in that mtype
        """
        # out = {mtype: self.__sort_list_set([stype for m in self.get_measurements(mtype=mtype) for stype in m.stypes])
        # for mtype in self.mtypes}
        return {k: v.keys() for k, v in self._info_dict['mtype_stype'].iteritems()}

    @property
    def mtype_stype_mdict(self):
        """
        returns a dictionary of mtypes, with all stypes in that mtype
        """
        # out = {mtype: {stype: self.get_measurements(mtype=mtype, stype=stype)
        # for stype in self.mtype_stype_dict[mtype]}
        # for mtype in self.mtypes}
        return self._info_dict['mtype_stype']

    @property
    def stype_sval_dict(self):
        # out = {stype: self.__sort_list_set([m.stype_dict[stype].value for m in self.stype_dict[stype]]) for stype in
        # self.stypes}
        return {k: v.keys() for k, v in self._info_dict['stype_sval'].iteritems()}

    @property
    def mtype_stype_sval_mdict(self):
        # out = {mt:
        # {tt: {tv: self.get_measurements(mtype=mt, stype=tt, sval=tv)
        # for tv in self.stype_sval_dict[tt]}
        # for tt in self.mtype_stype_dict[mt]}
        # for mt in self.mtypes}
        return self._info_dict['mtype_stype_sval']

    ''' FILTER FUNCTIONS '''

    def filter(self, mtype=None, stype=None, sval=None, sval_range=None,
               **kwargs):
        """
        used to filter measurement data.

        Parameters
        ----------
           mtype: mtype to be filtered for, if not specified all mtypes are returned
           stype: stype to be filtered for, if not specified all stypes are returned
           sval: sval to be filtered for, can only be used in conjuction with stype
           sval_range: sval_range to be filtered for, can only be used in conjuction with stype
           kwargs:
        """
        self._filtered_data = self.get_measurements(mtype=mtype,
                                                    stype=stype, sval=sval, sval_range=sval_range, filtered=False)
        return self._filtered_data

    def reset_filter(self):
        """
        rests filter applied using sample.filter()
        :return:
        """
        self._filtered_data = None

    ''' FIND FUNCTIONS '''

    def get_measurements(self,
                         mtype=None,
                         stype=None, sval=None, sval_range=None,
                         is_mean=False,
                         filtered=True,
                         reversed=False,
                         **options):
        """
        Returns a list of measurements of type = mtype

        Parameters
        ----------
           stype: str
              series type
           sval: float
              series value
           sval_range: list
              series range e.g. sval_range = [0,2] will give all from 0 to 2
           is_mean:
           filtered:
           revesed:
              if reversed true it returns only measurements that do not meet criteria
           sval_range:
              can be used to look up measurements within a certain range. if only one value is given,
                     it is assumed to be an upper limit and the range is set to [0, sval_range]

           filtered:
              if true measurements will only be searched in filtered data
           mtype:
        """
        if sval is None:
            svalue = np.nan
        else:
            svalue = str(sval)

        if is_mean:
            # self.logger.debug('SEARCHING\t measurements(mean_list) with  << %s, %s, %s >>' % (mtype, stype, svalue))
            out = self.mean_measurements
        else:
            if filtered:
                # self.logger.debug('SEARCHING\t measurements with  << %s, %s, %s >> in filtered data' % (mtype, stype, svalue))
                out = self.filtered_data
            else:
                # self.logger.debug('SEARCHING\t measurements with  << %s, %s, %s >>' % (mtype, stype, svalue))
                out = self.measurements

        if mtype:  # filter mtypes, if given
            mtype = to_list(mtype)
            out = [m for m in out if m.mtype in mtype]
        if stype:
            stype = to_list(stype)
            out = [m for m in out for t in stype if t in m.stypes]

        if sval is not None:
            sval = to_list(sval)
            out = [m for m in out for val in sval if val in m.svals]

        if not sval_range is None:
            if not isinstance(sval_range, list):
                sval_range = [0, sval_range]
            else:
                if len(sval_range) == 1:
                    sval_range = [0] + sval_range
            out = [m for m in out for val in m.svals
                   if val <= max(sval_range)
                   if val >= min(sval_range)]

        if len(out) == 0:
            self.logger.error(
                'UNKNOWN\t << %s, %s, %s >> or no measurement found for sample << %s >>' % (
                    mtype, stype, svalue, self.name))
            return []

        if reversed:
            out = [i for i in self.filtered_data if not i in out]
        return out

    def delete_measurements(self, mtype=None, stype=None, sval=None, sval_range=None, **options):
        measurements_for_del = self.get_measurements(mtype=mtype, stype=stype, sval=sval, sval_range=sval_range)
        if measurements_for_del:
            self.measurements = [m for m in self.measurements if not m in measurements_for_del]

    ''' MISC FUNTIONS '''

    def mean_measurement_from_list(self, mlist, interpolate=False, recalc_magag=False):  # todo redundant?
        """
        takes a list of measurements and creates a mean measurement out of all measurements data

        Parameters
        ----------
           mlist:
           interpolate:
           recalc_magag:
        :return:
        """
        mlist = to_list(mlist)
        measurement = deepcopy(mlist[0])

        for dtype in measurement.data:
            dtype_list = [m.data[dtype] for m in mlist]
            if interpolate:
                varlist = self.__get_variable_list(dtype_list)
                if len(varlist) > 1:
                    dtype_list = [m.interpolate(varlist) for m in dtype_list]

            if len(dtype_list) > 1:  # for single measurements
                measurement.data[dtype] = condense(dtype_list)
                measurement.data[dtype] = measurement.data[dtype].sort('variable')

            if recalc_magag:
                measurement.data[dtype].define_alias('m', ('x', 'y', 'z'))
                measurement.data[dtype]['mag'].v = measurement.data[dtype].magnitude('m')

        if measurement.initial_state:
            for dtype in measurement.initial_state.data:
                dtype_list = [m.initial_state.data[dtype] for m in mlist if m.initial_state]
                measurement.initial_state.data[dtype] = condense(dtype_list)
                measurement.initial_state.data[dtype] = measurement.initial_state.data[dtype].sort('variable')
                if recalc_magag:
                    measurement.initial_state.data[dtype].define_alias('m', ('x', 'y', 'z'))
                    measurement.initial_state.data[dtype]['mag'].v = measurement.initial_state.data[dtype].magnitude(
                        'm')
        measurement.sample_obj = self
        return measurement

    def average_measurements(self,
                             mtype=None, stype=None, sval=None, sval_range=None, mlist=None,
                             interpolate=True, recalc_magag=False,
                             substfunc='mean'):
        """
        Averages a list of measurements and returns a measurement with 'is_mean' flag
        :param mtype:
        :param stype:
        :param sval:
        :param sval_range:
        :param mlist:
        :param interpolate:
        :param recalc_magag:
        :param substfunc:
        :return:
        """

        # make sure a mtype is given
        if not mtype:
            self.logger.error('NO mtype specified. Please specify mtype')
            return

        # get measurement list from criteria
        mlist = self.get_measurements(mtype=mtype, stype=stype, sval=sval, sval_range=sval_range, filtered=True)

        if len(mlist) == 1:
            self.logger.warning('Only one measurement found returning measurement')
            return mlist[0]

        # use first measurement as base
        dtypes = get_common_dtypes_from_list(mlist=mlist)

        base_measurement = deepcopy(mlist[0])
        # delete uncommon dtype from base_measurement
        for key in base_measurement.data:
            if key not in dtypes:
                base_measurement.data.pop(key)

        for dtype in dtypes:  # cycle through all dtypes e.g. 'down_field', 'up_field' for hysteresis
            dtype_list = [m.data[dtype] for m in mlist]  # get all data for dtype in one list
            if interpolate:
                varlist = self.__get_variable_list(dtype_list)
                if len(varlist) > 1:
                    dtype_list = [m.interpolate(varlist) for m in dtype_list]
                    # print dtype_list

    def mean_measurement(self,
                         mtype=None, stype=None, sval=None, sval_range=None, mlist=None,
                         interpolate=True, recalc_magag=False,
                         substfunc='mean'):
        """
        takes a list of measurements and creates a mean measurement out of all measurements data

        Parameters
        ----------
           mlist:
           interpolate:
           recalc_magag:
        :return:
        """
        if not mtype:
            raise ValueError('No mtype specified')

        mlist = self.get_measurements(mtype=mtype, stype=stype, sval=sval, sval_range=sval_range, filtered=True)
        if not mlist:
            return None

        # use first measurement as base
        dtypes = get_common_dtypes_from_list(mlist=mlist)

        # create a base measurement
        base_measurement = RockPy.Functions.general.create_dummy_measurement(mtype=mlist[0].mtype,
                                                                             machine=mlist[0].machine,
                                                                             mdata=deepcopy(mlist[0].data))

        # delete uncommon dtype from base_measurement
        for key in base_measurement.data:
            if key not in dtypes:
                base_measurement.data.pop(key)

        for dtype in dtypes:  # cycle through all dtypes e.g. 'down_field', 'up_field' for hysteresis
            dtype_list = [m.data[dtype] for m in mlist]
            if interpolate:
                varlist = self.__get_variable_list(dtype_list, var='temp')
                if len(varlist) > 1:
                    dtype_list = [m.interpolate(varlist) for m in dtype_list]

            if len(dtype_list) > 1:  # for single measurements
                base_measurement.data[dtype] = condense(dtype_list)
                base_measurement.data[dtype] = base_measurement.data[dtype].sort('variable')

            if recalc_magag:
                base_measurement.data[dtype].define_alias('m', ('x', 'y', 'z'))
                base_measurement.data[dtype]['mag'].v = base_measurement.data[dtype].magnitude('m')

        if base_measurement.initial_state:
            for dtype in base_measurement.initial_state.data:
                dtype_list = [m.initial_state.data[dtype] for m in mlist if m.initial_state]
                base_measurement.initial_state.data[dtype] = condense(dtype_list, substfunc=substfunc)
                base_measurement.initial_state.data[dtype] = base_measurement.initial_state.data[dtype].sort('variable')
                if recalc_magag:
                    base_measurement.initial_state.data[dtype].define_alias('m', ('x', 'y', 'z'))
                    base_measurement.initial_state.data[dtype]['mag'].v = base_measurement.initial_state.data[
                        dtype].magnitude(
                        'm')
        base_measurement.sample_obj = self
        return base_measurement

    def all_results(self, mtype=None,
                    stype=None, sval=None, sval_range=None,
                    mlist=None, filtered=True,
                    **parameter):
        """
        calculates all results for a list of measurements and stores them in a RockPy data object

        Parameters
        ----------
           mlist:
           parameter:
        :return:
        """

        if not mlist:
            mlist = self.get_measurements(mtype=mtype, stype=stype, sval=sval, sval_range=sval_range, filtered=filtered)

        mlist = [m for m in mlist if m.mtype not in ['mass', 'diameter', 'height']]  # get rid of parameter measurements

        if len(mlist) == 0:
            self.logger.warning('all_results: no measurements for results')
            return
        # # initialize
        all_results = None
        rownames = []
        for index, measurement in enumerate(mlist):
            measurement.calc_all(**parameter)
            rownames.append(measurement.mtype + ' %02i' % index)
            results = measurement.results
            if not all_results:
                all_results = results
            else:
                # add new columns to all_results
                # column_add_all_results = list(set(results.column_names) -
                # set(all_results.column_names))  # cols in results but not in all_results
                #
                # all_results = all_results.append_columns(column_add_all_results)
                #
                # aux = RockPyData(column_names=all_results.column_names,
                # data=[np.nan for i in range(len(all_results.column_names))])
                # todo remove workaround
                # column_add_results = list(set(all_results.column_names) -
                # set(results.column_names))  # columns in all_results but not in results
                # results = results.append_columns(column_add_results)
                # for k in aux.column_names:
                # if k in results.column_names:
                # aux[k] = results[k].v
                # store new results in mean_measults
                all_results = all_results.append_rows(results)
        all_results._row_names = rownames
        return all_results

    def calc_all_mean_results(self, filtered=False, **parameter):
        """
        Calculates the mean out of all results

        Parameters
        ----------
           filtered:
           parameter:
        """
        out = None
        for mtype in self.mtypes:
            for stype in self.mtype_stype_dict[mtype]:
                for sval in self.stype_sval_dict[stype]:
                    results = self.all_results(mtype=mtype, stype=stype, sval=sval,
                                               filtered=filtered,
                                               **parameter)

                    results.define_alias('variable', ['stype ' + stype])

                    data = np.mean(results.v, axis=0)
                    err = np.std(results.v, axis=0)
                    if not out:
                        out = RockPyData(column_names=results.column_names, data=data)
                        out.e = err.reshape(1, len(err))
                    else:
                        append = RockPyData(column_names=results.column_names, data=data)
                        append.e = err.reshape(1, len(err))
                        out = out.append_rows(data=append.data)
        self._mean_results = out
        return out

    def get_mean_results(self,
                         mtype=None,
                         stype=None, sval=None, sval_range=None,
                         mlist=None,
                         filtered=False,
                         **parameter):
        """
        calculates all results and returns the mean

        Parameters
        ----------
           mtype: str
           stype: str
           sval: float
           sval_range: list
           mlist: list
              *optional*
           filtered: bool
              is used to specify if the filtered_data_measurement list is used to get all corresponding
              measurements. In the case of a mean measurements it genreally is not wanted to have the
              result of the mean but get the mean of the result.
              if *True* the results(Mean) will be returned
              if *False* the Mean(Results) wil be returned, filtered data will still be calculated.
        """

        if not mlist:
            mlist = self.get_measurements(mtype=mtype,
                                          stype=stype, sval=sval, sval_range=sval_range,
                                          filtered=filtered)

        all_results = self.all_results(mlist=mlist, **parameter)

        if 'stype' in ''.join(all_results.column_names):  # check for stype
            self.logger.warning('series/S found check if measurement list correct'
                                )

        v = np.nanmean(all_results.v, axis=0)
        errors = np.nanstd(all_results.v, axis=0)

        mean_results = RockPyData(column_names=all_results.column_names,
                                  # row_names='mean ' + '_'.join(all_results.row_names),
                                  data=v)

        mean_results.e = errors.reshape((1, len(errors)))
        return mean_results

    def __get_variable_list(self, rpdata_list, var='variable'):
        out = []
        for rp in rpdata_list:
            out.extend(rp[var].v)
        return self.__sort_list_set(out)

    def __sort_list_set(self, values):
        """
        returns a sorted list of non duplicate values
           values:
        :return:
        """
        return sorted(list(set(values)))

    # def _sort_stype_sval(self, mlist):
    ''' FOR PLOTTING FUNCTIONS '''

    @property
    def plottable(self):
        """
        returns a list of all possible Visuals for this sample
        """
        out = {}
        for visual in RockPy.Visualize.base.Generic.inheritors():
            if self.meets_requirements(visual._required):
                out.update({visual.__name__: visual})
        return out

    def meets_requirements(self, require_list):
        """
        checks if the sample meets the requirements for a certain plot

        Parameters
        ----------
           require_list: list
              list of requirements, usually comes from Visualize

        Returns
        -------
           bool
        """
        out = []

        if require_list is None:  # no requirements - standard == False
            return False

        for i in require_list:  # iterate over requirements
            if i in self.mtypes:
                out.append(True)  # true if meets requirements
            else:
                out.append(False)  # false if not

        if all(out):
            return True  # return if all == True
        else:
            return False

    def sort_mlist_in_stype_dict(self, mlist):
        """ sorts a list of measurements according to their stype and svals"""
        mlist = to_list(mlist)
        out = {}
        for m in mlist:
            for t in m.series:
                if not t.stype in out:
                    out[t.stype] = {}
                if not t.value in out:
                    out[t.stype][t.value] = []
                out[t.stype][t.value].append(m)
        return out

    """ INFO """

    def info(self):
        """
        Prints a table of the samples infos
        :return:
        """
        out = []
        header = ['Sample Name', 'Measurements', 'series', 'series values', 'Initial State']
        for m in self.measurements:
            if m.initial_state:
                initial = m.initial_state.mtype
            else:
                initial = 'None'
            out.append([self.name, m.mtype, m.stypes, m.svals, initial])
        out.append(['-----' for i in header])
        out = tabulate.tabulate(out, headers=header, tablefmt="simple")
        return out


def get_common_dtypes_from_list(mlist):
    """
    Takes a list of measurements and returns a list of common dtypes.

    Example
    -------
       mlist = [hys(down_field, up_field), hys(down_field, up_field, virgin)]
       returns ['down_field', 'up_field']

    Parameter
    ---------
       mlist: list
          list of measurements

    Returns
    -------
       dtypes
          sorted list of commen dtypes
    """
    # get intersection of all measurements with certain dtype
    dtypes = None
    for m in mlist:
        if not dtypes:
            dtypes = set(m.data.keys())
        else:
            dtypes = dtypes & set(m.data.keys())
    return sorted(list(dtypes))
