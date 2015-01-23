# coding=utf-8
from RockPy.Functions.general import _to_list

__author__ = 'Michael Volk'
# for all project related classes
import logging
import numpy as np
from RockPy.Measurements.base import Measurement
from RockPy.Structure.data import RockPyData, condense
import RockPy.Visualize.base
from copy import deepcopy

RockPy.Functions.general.create_logger(__name__)


class Sample(object):
    """
    Sample in a way a container for measurements

    HowTo:
    ======
       MTYPES
       ++++++
        want all measurement type (e.g. hysteresis, thellier, backfield...):

        as list: sample.mtypes
           print sample.mtypes
           >>> ['diameter', 'height', 'mass', 'thellier']
        as dictionary with corresponding measurements as value: sample.mdict
           print sample.mdict
           >>> {'diameter': [<RockPy.Measurements.parameters.Diameter object at 0x10d085910>],
                'thellier': [<RockPy.Measurements.thellier.Thellier object at 0x10d0a59d0>],
                'mass': [<RockPy.Measurements.parameters.Mass object at 0x10d085790>],
                'height': [<RockPy.Measurements.parameters.Height object at 0x10d085a90>]}

       TTYPES
       ++++++
        want all treatment type (e.g. pressure, temperature...):

        as list: sample.ttypes
           print sample.ttypes
           >>> ['none', 'pressure']
        as dictionary with corresponding measurements as value: sample.tdict
           print sample.tdict
           >>> {'pressure': [<RockPy.Measurements.thellier.Thellier object at 0x10d0a59d0>,
                             <RockPy.Measurements.thellier.Thellier object at 0x10d0a5910>],
                'none': [<RockPy.Measurements.parameters.Mass object at 0x10d085790>,
                         <RockPy.Measurements.parameters.Diameter object at 0x10d085910>,
                         <RockPy.Measurements.parameters.Height object at 0x10d085a90>]}

            none is always given, if a measurement did not receive any treatment, or a treatment is not explicitely given

        MTYPES & TTYPES
        +++++++++++++++
        want to know what type of measurement has which kinds of treatments:

        dictionary: sample.mtype_ttype_dict
           print sample.mtype_ttype_dict
           >>> {'diameter': ['none'], 'thellier': ['pressure'], 'mass': ['none'], 'height': ['none']}

        TTYPES & TVALUES
        ++++++++++++++++
        want to know what treatment has been done with wich values?

        dictionary: sample.ttype_tval_dict
           print sample.ttype_tval_dict
           >>> {'pressure': [0.0, 0.6, 1.2, 1.8], 'none': [0]}


        MTYPES & TTYPE & TVALUES
        ++++++++++++++++++++++++
        want to know what measurement has which treatments at what values?

        dictionary: sample.mtype_ttype_tval_dict

           print sample.mtype_ttype_tval_dict
           >>> {'diameter': {'none':
                               {0: [<RockPy.Measurements.parameters.Diameter object at 0x10e1bd8d0>]}},
                'thellier': {'pressure':
                               {0.0: [<RockPy.Measurements.thellier.Thellier object at 0x10e1dd990>],
                                0.6: [<RockPy.Measurements.thellier.Thellier object at 0x10e1dd8d0>],
                                1.2: [<RockPy.Measurements.thellier.Thellier object at 0x10e406850>],
                                1.8: [<RockPy.Measurements.thellier.Thellier object at 0x10e40be10>]}},
                'mass': {'none': {0: [<RockPy.Measurements.parameters.Mass object at 0x10e1bd750>]}},
                'height': {'none': {0: [<RockPy.Measurements.parameters.Height object at 0x10e1bda50>]}}}

    """
    logger = logging.getLogger(__name__)

    def __init__(self, name,
                 mass=None, mass_unit='kg', mass_machine='generic',
                 height=None, diameter=None, length_unit='mm', length_machine='generic',
                 **options):
        """

        :param name: str - name of the sample.
        :param mass: float - mass of the sample. If not kg then please specify the mass_unit. It is stored in kg.
        :param mass_unit: str - has to be specified in order to calculate the sample mass properly.
        :param height: float - sample height - stored in 'm'
        :param diameter: float - sample diameter - stored in 'm'
        :param length_unit: str - if not 'm' please specify
        """
        self.name = name
        Sample.logger.info('CREATING\t new sample << %s >>' % self.name)

        self.measurements = []
        self.results = None

        ''' is sample is a mean sample from sample_goup ect... '''
        self.is_mean = False # if a calculated mean_sample
        self.mean_measurements = []
        self.mean_results = None
        self._filtered_data = None

        if mass is not None:
            self.add_measurement(mtype='mass', mfile=None, machine=mass_machine,
                                 value=float(mass), unit=mass_unit)
        if diameter is not None:
            self.add_measurement(mtype='diameter', mfile=None, machine=length_machine,
                                 value=float(diameter), unit=length_unit)
        if height is not None:
            self.add_measurement(mtype='height', mfile=None, machine=length_machine,
                                 value=float(height), unit=length_unit)

    @property
    def filtered_data(self):
        if not self._filtered_data:
            return self.measurements
        else:
            return self._filtered_data


    def __repr__(self):
        return '<< %s - RockPy.Sample >>' % self.name

    ''' ADD FUNCTIONS '''

    def add_measurement(self,
                        mtype=None, mfile=None, machine='generic',  # general
                        idx=None, mdata=None,
                        **options):
        '''
        All measurements have to be added here

        :param mtype: str - the type of measurement
        :param mfile: str -  the measurement file
        :param machine: str - the machine from which the file is output
        :param idx:
        :param mdata: any kind of data that must fit the required structure of the data of the measurement
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
                return measurement
            else:
                return None
        else:
            Sample.logger.error(' << %s >> not implemented, yet' % mtype)

    def add_simulation(self):
        #todo
        raise NotImplementedError

    def calc_all(self, **parameter):
        """
        Calculates all results using specified parameter for all available measurements
        .. Note::

           always recalculates everything

        :param parameter: calculation parameter e.g. t_min, t_max @ Thellier-Thellier
        :return:
        """
        self.results = self.all_results(**parameter)
        return self.results

    @property
    def mtypes(self):
        """
        returns list of all mtypes
        """
        out = [m.mtype for m in self.measurements]
        return self.__sort_list_set(out)

    @property
    def ttypes(self):
        """
        returns a list of all ttypes
        """
        out = [t for m in self.measurements for t in m.ttype_dict]
        return self.__sort_list_set(out)

    @property
    def tvals(self):
        """
        returns a list of all ttypes
        """
        out = []
        for m in self.measurements:
            out.extend(m.tvals)
        return self.__sort_list_set(out)

    @property
    def mtype_tdict(self):
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
        out = {ttype: self.get_measurements(ttype=ttype) for ttype in self.ttypes}
        return out

    @property
    def mtype_ttype_dict(self):
        """
        returns a dictionary of mtypes, with all ttypes in that mtype
        """
        out = {mtype: self.__sort_list_set([ttype for m in self.get_measurements(mtype=mtype) for ttype in m.ttypes])
               for mtype in self.mtypes}
        return out

    @property
    def mtype_ttype_mdict(self):
        """
        returns a dictionary of mtypes, with all ttypes in that mtype
        """
        out = {mtype: {ttype: self.get_measurements(mtype=mtype, ttype=ttype)
                       for ttype in self.mtype_ttype_dict[mtype]}
               for mtype in self.mtypes}
        return out

    @property
    def ttype_tval_dict(self):
        out = {ttype: self.__sort_list_set([m.ttype_dict[ttype].value for m in self.ttype_dict[ttype]]) for ttype in
               self.ttypes}
        return out

    @property
    def mtype_ttype_tval_mdict(self):
        out = {mt:
                   {tt: {tv: self.get_measurements(mtype=mt, ttype=tt, tval=tv)
                         for tv in self.ttype_tval_dict[tt]}
                    for tt in self.mtype_ttype_dict[mt]}
               for mt in self.mtypes}
        return out

    ''' FILTER FUNCTIONS '''
    def filter(self, mtype=None, ttype=None, tval=None, tval_range=None,
                         **kwargs):
        """
        used to filter measurement data.

        :param mtype: mtype to be filtered for, if not specified all mtypes are returned
        :param ttype: ttype to be filtered for, if not specified all ttypes are returned
        :param tval: tval to be filtered for, can only be used in conjuction with ttype
        :param tval_range: tval_range to be filtered for, can only be used in conjuction with ttype
        :param kwargs:
        :return:
        """
        self._filtered_data = self.get_measurements(mtype=mtype,
                                                    ttype=ttype, tval=tval, tval_range=tval_range)

    def reset_filter(self):
        """
        rests filter applied using sample.filter()
        :return:
        """
        self._filtered_data = None



    ''' FIND FUNCTIONS '''

    def get_measurements(self, mtype=None, ttype=None, tval=None, tval_range=None,
                         **options):
        """
        Returns a list of measurements of type = mtype

        :tval_range: can be used to look up measurements within a certain range. if only one value is given,
                     it is assumed to be an upper limit and the range is set to [0, tval_range]


        :param mtype:
        :return:
        """
        if tval is None:
            tvalue = np.nan
        else:
            tvalue = str(tval)

        if self.is_mean:
            Sample.logger.debug('SEARCHING\t measurements(mean_list) with  << %s, %s, %s >>' % (mtype, ttype, tvalue))
            out = self.mean_measurements
        else:
            Sample.logger.debug('SEARCHING\t measurements with  << %s, %s, %s >>' % (mtype, ttype, tvalue))
            out = self.measurements

        if mtype: #filter mtypes, if given
            mtype = _to_list(mtype)
            out = [m for m in out if m.mtype in mtype]
        if ttype:
            ttype = _to_list(ttype)
            out = [m for m in out for t in ttype if t in m.ttypes]

        if tval is not None:
            tval = _to_list(tval)
            out = [m for m in out for val in tval if val in m.tvals]

        print(out)

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

        return out

    def delete_measurements(self, mtype=None, ttype=None, tval=None, tval_range=None, **options):
        measurements_for_del = self.get_measurements(mtype=mtype, ttype=ttype, tval=tval, tval_range=tval_range)
        if measurements_for_del:
            self.measurements = [m for m in self.measurements if not m in measurements_for_del]


    ''' MISC FUNTIONS '''

    def mean_measurement_from_list(self, mlist, interpolate=False, recalc_mag=False):
        """
        takes a list of measurements and creates a mean measurement out of all measurements data

        :param mlist:
        :param interpolate:
        :param recalc_mag:
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

            if len(dtype_list) > 1: #for single measurements
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
                         interpolate=False, recalc_mag=False):
        """
        takes a list of measurements and creates a mean measurement out of all measurements data

        :param mlist:
        :param interpolate:
        :param recalc_mag:
        :return:
        """
        if not mtype:
            raise ValueError('No mtype specified')

        mlist = self.get_measurements(mtype=mtype, ttype=ttype, tval=tval, tval_range=tval_range)
        measurement = deepcopy(mlist[0])

        for dtype in measurement.data:
            dtype_list = [m.data[dtype] for m in mlist]
            if interpolate:
                varlist = self.__get_variable_list(dtype_list)
                if len(varlist) > 1:
                    dtype_list = [m.interpolate(varlist) for m in dtype_list]

            if len(dtype_list) > 1: #for single measurements
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


    def all_results(self, mtype=None, ttype=None, tval=None, tval_range=None, mlist=None, **parameter):
        """
        calculates all results for a list of measurements and stores them in a RockPy data object
        :param mlist:
        :param parameter:
        :return:
        """
        if not mlist:
            mlist = self.get_measurements(mtype=mtype, ttype=ttype, tval=tval, tval_range=tval_range)

        # # initialize
        all_results = None
        rownames = []

        for index, measurement in enumerate(mlist):
            measurement.calc_all()
            rownames.append(measurement.mtype[0:3] + ' %03i' % index)
            results = measurement.results
            if not all_results:
                all_results = results
            else:
                # add new columns to all_results
                column_add_all_results = list(set(results.column_names) -
                                              set(all_results.column_names)) #cols in results but not in all_results

                all_results = all_results.append_columns(column_add_all_results)

                aux = RockPyData(column_names=all_results.column_names, data=[np.nan for i in range(len(all_results.column_names))])
                # todo remove workaround
                # column_add_results = list(set(all_results.column_names) -
                #                           set(results.column_names))  # columns in all_results but not in results
                # results = results.append_columns(column_add_results)
                for k in aux.column_names:
                    if k in results.column_names:
                        aux[k] = results[k].v
                # store new results in mean_measults
                all_results = all_results.append_rows(aux)

        all_results._row_names = rownames
        return all_results

    def get_mean_results(self, mtype=None, ttype=None, tval=None, tval_range=None, mlist=None, **parameter):
        """
        calculates all results and returns the
        :param mlist:
        :return:
        """
        if not mlist:
            mlist = self.get_measurements(mtype=mtype, ttype=ttype, tval=tval, tval_range=tval_range)

        all_results = self.all_results(mlist=mlist, **parameter)

        if 'ttype' in ''.join(all_results.column_names): #check for ttype
            self.logger.warning('TREATMENT/S found check if measurement list correct'
            )
        v = np.nanmean(all_results.v, axis=0)
        errors = np.nanstd(all_results.v, axis=0)

        mean_results = RockPyData(column_names=all_results.column_names,
                                  row_names='mean ' + '_'.join(all_results.row_names),
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
        :param values:
        :return:
        """
        return sorted(list(set(values)))

    # def _sort_ttype_tval(self, mlist):
    #     """
    #     sorts a list of measurements according to their tvals and ttypes
    #     :param mlist:
    #     :return:
    #     """


    ''' FOR PLOTTING FUNCTIONS '''

    @property
    def plottable(self):
        """
        returns a list of all possible Visuals for this sample
        :return:
        """
        out = {}
        for visual in RockPy.Visualize.base.Generic.inheritors():
            if self.meets_requirements(visual._required):
                out.update({visual.__name__: visual})
        return out

    def meets_requirements(self, require_list):
        """
        checks if the sample meets the requirements for a certain plot

        :param require_list: list of requirements, usually comes from Visualize
        :return: bool
        """
        out = []

        if require_list is None: #no requirements - standard == False
            return False

        for i in require_list: #iterate over requirements
            if i in self.mtypes:
                out.append(True) # true if meets requirements
            else:
                out.append(False) # false if not

        if all(out):
            return True # return if all == True
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

