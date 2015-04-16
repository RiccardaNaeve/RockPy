# coding=utf-8
from RockPy.Functions.general import _to_list
from copy import deepcopy
import numpy as np
import logging
import itertools
from RockPy.Measurements.base import Measurement
from RockPy.Structure.data import RockPyData, condense
import RockPy.Visualize.base
import tabulate

# RockPy.Functions.general.create_logger(__name__)

class Sample(object):
    """
    Sample in a way a container for measurements
    """
    logger = logging.getLogger(__name__)
    snum = 0

    def __init__(self, name,
                 mass=None, mass_unit='kg', mass_machine='generic',
                 height=None, diameter=None, length_unit='mm', length_machine='generic', color=None,
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
           color: color
              used in plots if specified
        """
        self.color = color
        self.name = name
        Sample.logger.info('CREATING\t new sample << %s >>' % self.name)

        self.measurements = []
        self.results = None

        ''' is sample is a mean sample from sample_goup ect... '''
        self.is_mean = False  # if a calculated mean_sample
        self.mean_measurements = []
        self._mean_results = None
        self._filtered_data = None
        self._info_dict = self.__create_info_dict()

        if mass is not None:
            self.add_measurement(mtype='mass', mfile=None, machine=mass_machine,
                                 value=float(mass), unit=mass_unit)
        if diameter is not None:
            self.add_measurement(mtype='diameter', mfile=None, machine=length_machine,
                                 value=float(diameter), unit=length_unit)
        if height is not None:
            self.add_measurement(mtype='height', mfile=None, machine=length_machine,
                                 value=float(height), unit=length_unit)
        self.index = Sample.snum
        Sample.snum +=1

    """ INFO DICTIONARY """

    def __create_info_dict(self):
        """
        creates all info dictionaries

        Returns
        -------
           dict
              Dictionary with a permutation of ,type, ttype and tval.
        """
        d = ['mtype', 'ttype', 'tval']
        keys = ['_'.join(i) for n in range(4) for i in itertools.permutations(d, n) if not len(i) == 0]
        out = {i: {} for i in keys}
        return out

    def add_m2_info_dict(self, m):
        keys = self._info_dict.keys()
        for t in m.treatments:
            test = {'mtype': m.mtype, 'ttype': t.ttype, 'tval': t.value}
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
        map(self.add_m2_info_dict, self.measurements)

    """ PICKL """

    def __setstate__(self, d):
        self.__dict__.update(d)

    def __getstate__(self):
        '''
        returned dict will be pickled
        :return:
        '''
        pickle_me = {k: v for k, v in self.__dict__.iteritems() if k in
                     (
                         'name',
                         'measurements',
                         '_filtered_data', '_info_dict',
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


    ''' ADD FUNCTIONS '''

    def add_measurement(self,
                        mtype=None, mfile=None, machine='generic',  # general
                        idx=None, mdata=None,
                        **options):
        '''
        All measurements have to be added here

        Parameters
        ----------
           mtype: str - the type of measurement
           mfile: str -  the measurement file
           machine: str - the machine from which the file is output
           idx:
           mdata: any kind of data that must fit the required structure of the data of the measurement
                    will be used instead of data from file
        :return: RockPy.measurement object

        :mtypes:

        - mass
        '''
        mtype = mtype.lower()

        implemented = {i.__name__.lower(): i for i in Measurement.inheritors()}

        if idx is None:
            idx = len(self.measurements)  # if there is no measurement index
        if mtype in implemented:
            Sample.logger.info(' ADDING\t << measurement >> %s' % mtype)
            measurement = implemented[mtype](self,
                                             mtype=mtype, mfile=mfile, machine=machine,
                                             m_idx=idx, mdata=mdata,
                                             **options)
            if measurement.has_data:
                self.measurements.append(measurement)
                self.add_m2_info_dict(measurement)
                return measurement
            else:
                return None
        else:
            Sample.logger.error(' << %s >> not implemented, yet' % mtype)

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
            Sample.logger.info(' ADDING\t << simulated measurement >> %s' % mtype)
            measurement = implemented[mtype].simulate(self, m_idx=idx, **options)
            if measurement.has_data:
                self.measurements.append(measurement)
                return measurement
            else:
                return None
        else:
            Sample.logger.error(' << %s >> not implemented, yet' % mtype)

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
    def mtypes(self):
        """
        returns list of all mtypes
        """
        return sorted(self._info_dict['mtype'].keys())

    @property
    def ttypes(self):
        """
        returns a list of all ttypes
        """
        return sorted(self._info_dict['ttype'].keys())

    @property
    def tvals(self):
        """
        returns a list of all ttypes
        """

        return sorted(self._info_dict['tval'].keys())

    @property
    def mtype_tdict(self):  # todo: delete?
        """
        dictionary with all measurement_types {mtype:[tretments to corresponding m]}
        """
        out = {}
        for mtype in self.mtypes:
            aux = []
            for m in self.get_measurements(mtype=mtype):
                aux.extend(m.treatments)
            out.update({mtype: aux})
        return out

    @property
    def ttype_dict(self):
        """
        dictionary with all treatment_types {ttype:[list of measurements]}

        example:
        >>> {'pressure': [<RockPy.Measurements.parameters.Mass object at 0x10e196150>, <RockPy.Measurements.parameters.Diameter object at 0x10e1962d0>]}
        """
        return self._info_dict['ttype']

    @property
    def mtype_ttype_dict(self):
        """
        returns a dictionary of mtypes, with all ttypes in that mtype
        """
        # out = {mtype: self.__sort_list_set([ttype for m in self.get_measurements(mtype=mtype) for ttype in m.ttypes])
        # for mtype in self.mtypes}
        return {k: v.keys() for k, v in self._info_dict['mtype_ttype'].iteritems()}

    @property
    def mtype_ttype_mdict(self):
        """
        returns a dictionary of mtypes, with all ttypes in that mtype
        """
        # out = {mtype: {ttype: self.get_measurements(mtype=mtype, ttype=ttype)
        # for ttype in self.mtype_ttype_dict[mtype]}
        #        for mtype in self.mtypes}
        return self._info_dict['mtype_ttype']

    @property
    def ttype_tval_dict(self):
        # out = {ttype: self.__sort_list_set([m.ttype_dict[ttype].value for m in self.ttype_dict[ttype]]) for ttype in
        # self.ttypes}
        return {k: v.keys() for k, v in self._info_dict['ttype_tval'].iteritems()}

    @property
    def mtype_ttype_tval_mdict(self):
        # out = {mt:
        # {tt: {tv: self.get_measurements(mtype=mt, ttype=tt, tval=tv)
        #                  for tv in self.ttype_tval_dict[tt]}
        #             for tt in self.mtype_ttype_dict[mt]}
        #        for mt in self.mtypes}
        return self._info_dict['mtype_ttype_tval']

    ''' FILTER FUNCTIONS '''

    def filter(self, mtype=None, ttype=None, tval=None, tval_range=None,
               **kwargs):
        """
        used to filter measurement data.

        Parameters
        ----------
           mtype: mtype to be filtered for, if not specified all mtypes are returned
           ttype: ttype to be filtered for, if not specified all ttypes are returned
           tval: tval to be filtered for, can only be used in conjuction with ttype
           tval_range: tval_range to be filtered for, can only be used in conjuction with ttype
           kwargs:
        """
        self._filtered_data = self.get_measurements(mtype=mtype,
                                                    ttype=ttype, tval=tval, tval_range=tval_range, filtered=False)
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
                         ttype=None, tval=None, tval_range=None,
                         is_mean=False,
                         filtered=True,
                         reversed=False,
                         **options):
        """
        Returns a list of measurements of type = mtype

        Parameters
        ----------
           ttype: str
              treatment type
           tval: float
              treatment value
           tval_range: list
              treatment range e.g. tval_range = [0,2] will give all from 0 to 2
           is_mean:
           filtered:
           revesed:
              if reversed true it returns only measurements that do not meet criteria
           tval_range:
              can be used to look up measurements within a certain range. if only one value is given,
                     it is assumed to be an upper limit and the range is set to [0, tval_range]

           filtered:
              if true measurements will only be searched in filtered data
           mtype:
        """
        if tval is None:
            tvalue = np.nan
        else:
            tvalue = str(tval)

        if is_mean:
            # Sample.logger.debug('SEARCHING\t measurements(mean_list) with  << %s, %s, %s >>' % (mtype, ttype, tvalue))
            out = self.mean_measurements
        else:
            if filtered:
                # Sample.logger.debug('SEARCHING\t measurements with  << %s, %s, %s >> in filtered data' % (mtype, ttype, tvalue))
                out = self.filtered_data
            else:
                # Sample.logger.debug('SEARCHING\t measurements with  << %s, %s, %s >>' % (mtype, ttype, tvalue))
                out = self.measurements

        if mtype:  # filter mtypes, if given
            mtype = _to_list(mtype)
            out = [m for m in out if m.mtype in mtype]
        if ttype:
            ttype = _to_list(ttype)
            out = [m for m in out for t in ttype if t in m.ttypes]

        if tval is not None:
            tval = _to_list(tval)
            out = [m for m in out for val in tval if val in m.tvals]

        if not tval_range is None:
            if not isinstance(tval_range, list):
                tval_range = [0, tval_range]
            else:
                if len(tval_range) == 1:
                    tval_range = [0] + tval_range
            out = [m for m in out for val in m.tvals
                   if val <= max(tval_range)
                   if val >= min(tval_range)]

        if len(out) == 0:
            Sample.logger.error(
                'UNKNOWN\t << %s, %s, %s >> or no measurement found for sample << %s >>' % (
                    mtype, ttype, tvalue, self.name))
            return []

        if reversed:
            out = [i for i in self.filtered_data if not i in out]
        return out

    def delete_measurements(self, mtype=None, ttype=None, tval=None, tval_range=None, **options):
        measurements_for_del = self.get_measurements(mtype=mtype, ttype=ttype, tval=tval, tval_range=tval_range)
        if measurements_for_del:
            self.measurements = [m for m in self.measurements if not m in measurements_for_del]


    ''' MISC FUNTIONS '''

    def mean_measurement_from_list(self, mlist, interpolate=False, recalc_mag=False):  # todo redundant?
        """
        takes a list of measurements and creates a mean measurement out of all measurements data

        Parameters
        ----------
           mlist:
           interpolate:
           recalc_mag:
        :return:
        """
        mlist = _to_list(mlist)
        measurement = deepcopy(mlist[0])

        for dtype in measurement.data:
            dtype_list = [m.data[dtype] for m in mlist]
            if interpolate:
                varlist = self.__get_variable_list(dtype_list)
                if len(varlist) > 1:
                    dtype_list = [m.interpolate(varlist) for m in dtype_list]

            if len(dtype_list) > 1:  #for single measurements
                measurement.data[dtype] = condense(dtype_list)
                measurement.data[dtype] = measurement.data[dtype].sort('variable')

            if recalc_mag:
                measurement.data[dtype].define_alias('m', ( 'x', 'y', 'z'))
                measurement.data[dtype]['mag'].v = measurement.data[dtype].magnitude('m')

        if measurement.initial_state:
            for dtype in measurement.initial_state.data:
                dtype_list = [m.initial_state.data[dtype] for m in mlist if m.initial_state]
                measurement.initial_state.data[dtype] = condense(dtype_list)
                measurement.initial_state.data[dtype] = measurement.initial_state.data[dtype].sort('variable')
                if recalc_mag:
                    measurement.initial_state.data[dtype].define_alias('m', ( 'x', 'y', 'z'))
                    measurement.initial_state.data[dtype]['mag'].v = measurement.initial_state.data[dtype].magnitude(
                        'm')
        measurement.sample_obj = self
        return measurement

    def mean_measurement(self,
                         mtype=None, ttype=None, tval=None, tval_range=None, mlist=None,
                         interpolate=False, recalc_mag=False,
                         substfunc='mean'):
        """
        takes a list of measurements and creates a mean measurement out of all measurements data

        Parameters
        ----------
           mlist:
           interpolate:
           recalc_mag:
        :return:
        """
        if not mtype:
            raise ValueError('No mtype specified')

        mlist = self.get_measurements(mtype=mtype, ttype=ttype, tval=tval, tval_range=tval_range, filtered=True)

        if not mlist:
            return None

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

            if recalc_mag:
                measurement.data[dtype].define_alias('m', ( 'x', 'y', 'z'))
                measurement.data[dtype]['mag'].v = measurement.data[dtype].magnitude('m')

        if measurement.initial_state:
            for dtype in measurement.initial_state.data:
                dtype_list = [m.initial_state.data[dtype] for m in mlist if m.initial_state]
                measurement.initial_state.data[dtype] = condense(dtype_list, substfunc=substfunc)
                measurement.initial_state.data[dtype] = measurement.initial_state.data[dtype].sort('variable')
                if recalc_mag:
                    measurement.initial_state.data[dtype].define_alias('m', ( 'x', 'y', 'z'))
                    measurement.initial_state.data[dtype]['mag'].v = measurement.initial_state.data[dtype].magnitude(
                        'm')
        measurement.sample_obj = self
        return measurement


    def all_results(self, mtype=None,
                    ttype=None, tval=None, tval_range=None,
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
            mlist = self.get_measurements(mtype=mtype, ttype=ttype, tval=tval, tval_range=tval_range, filtered=filtered)

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
                #                               set(all_results.column_names))  # cols in results but not in all_results
                #
                # all_results = all_results.append_columns(column_add_all_results)
                #
                # aux = RockPyData(column_names=all_results.column_names,
                #                  data=[np.nan for i in range(len(all_results.column_names))])
                # todo remove workaround
                # column_add_results = list(set(all_results.column_names) -
                # set(results.column_names))  # columns in all_results but not in results
                # results = results.append_columns(column_add_results)
                # for k in aux.column_names:
                #     if k in results.column_names:
                #         aux[k] = results[k].v
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
            for ttype in self.mtype_ttype_dict[mtype]:
                for tval in self.ttype_tval_dict[ttype]:
                    results = self.all_results(mtype=mtype, ttype=ttype, tval=tval,
                                               filtered=filtered,
                                               **parameter)

                    results.define_alias('variable', ['ttype ' + ttype])

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
                         ttype=None, tval=None, tval_range=None,
                         mlist=None,
                         filtered=False,
                         **parameter):
        """
        calculates all results and returns the mean

        Parameters
        ----------
           mtype: str
           ttype: str
           tval: float
           tval_range: list
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
                                          ttype=ttype, tval=tval, tval_range=tval_range,
                                          filtered=filtered)

        all_results = self.all_results(mlist=mlist, **parameter)

        if 'ttype' in ''.join(all_results.column_names):  # check for ttype
            self.logger.warning('TREATMENT/S found check if measurement list correct'
            )

        v = np.nanmean(all_results.v, axis=0)
        errors = np.nanstd(all_results.v, axis=0)

        mean_results = RockPyData(column_names=all_results.column_names,
                                  # row_names='mean ' + '_'.join(all_results.row_names),
                                  data=v)

        mean_results.e = errors.reshape((1, len(errors)))
        return mean_results

    def __get_variable_list(self, rpdata_list):
        out = []
        for rp in rpdata_list:
            out.extend(rp['variable'].v)
        return self.__sort_list_set(out)

    def __sort_list_set(self, values):
        """
        returns a sorted list of non duplicate values
           values:
        :return:
        """
        return sorted(list(set(values)))

    # def _sort_ttype_tval(self, mlist):
    # """
    #     sorts a list of measurements according to their tvals and ttypes
    #        mlist:
    #     :return:
    #     """


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

        if require_list is None:  #no requirements - standard == False
            return False

        for i in require_list:  #iterate over requirements
            if i in self.mtypes:
                out.append(True)  # true if meets requirements
            else:
                out.append(False)  # false if not

        if all(out):
            return True  # return if all == True
        else:
            return False

    def sort_mlist_in_ttype_dict(self, mlist):
        """ sorts a list of measurements according to their ttype and tvals"""
        mlist = _to_list(mlist)
        out = {}
        for m in mlist:
            for t in m.treatments:
                if not t.ttype in out:
                    out[t.ttype] = {}
                if not t.value in out:
                    out[t.ttype][t.value] = []
                out[t.ttype][t.value].append(m)
        return out

    """ INFO """

    def info(self):
        """
        Prints a tabel of the samples infos
        :return:
        """
        out = []
        header = ['Sample Name', 'Measurements', 'Treatments', 'Treatment values', 'Initial State']
        for m in self.measurements:
            if m.initial_state:
                initial = m.initial_state.mtype
            else:
                initial = 'None'
            out.append([self.name, m.mtype, m.ttypes, m.tvals, initial])
        out.append(['-----' for i in header])
        out = tabulate.tabulate(out, headers=header, tablefmt="simple")
        return out