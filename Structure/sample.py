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
from collections import Counter
from functools import partial

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
        self._info_dict = self._create_info_dict()
        self._mdict = self._create_mdict()
        self._mean_mdict = self._create_mdict()

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
        m = self.get_measurements(mtypes='mass')[-1]
        return m.data['data']['mass'].v[0]

    @property
    def volume(self):
        """
        Searches for last volume measurement and returns value in m^3
        :return:
        """
        m = self.get_measurements(mtypes='volume')[-1]
        return m.data['data']['volume'].v[0]


    @property
    def mdict(self):
        if not self._mdict:
            self._mdict = self._create_mdict()
        else:
            return self._mdict
    #todo maybe create a rdict for results, in the same way the mdict works

    @property
    def mean_mdict(self):
        if not self._mean_mdict:
            self._mean_mdict = self._create_mdict()
        else:
            return self._mean_mdict

    def _create_mdict(self):
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
        out.update({'measurements': list()})
        out.update({'series': list()})
        return out

    def mdict_cleanup(self, mdict_type='mdict'):
        """
        recursively removes all empty lists from dictionary
        :param empties_list:
        :return:
        """

        mdict = getattr(self, mdict_type)

        for k0, v0 in sorted(mdict.iteritems()):
            if isinstance(v0, dict):
                for k1, v1 in sorted(v0.iteritems()):
                    if isinstance(v1, dict):
                        for k2, v2 in sorted(v1.iteritems()):
                            if isinstance(v2, dict):
                                for k3, v3 in sorted(v2.iteritems()):
                                    if not v3:
                                        v2.pop(k3)
                                    if not v2:
                                        v1.pop(k2)
                                    if not v1:
                                        v0.pop(k1)
                            else:
                                if not v2:
                                    v1.pop(k2)
                                if not v1:
                                    v0.pop(k1)
                    else:
                        if not v1:
                            v0.pop(k1)

    def add_m2_mdict(self, mobj, mdict_type='mdict'):
        """
        adds or removes a measurement from the mdict

        Parameters
        ----------
           mobj: measurement object
              object to be added
        :param operation:
        :return:
        """
        # cylcle through all the series
        for s in mobj.series:
            self.add_series2_mdict(mobj=mobj, series=s, mdict_type=mdict_type)

    def remove_m_from_mdict(self, mobj, mdict_type='mdict'):
        """
        adds or removes a measurement from the mdict

        Parameters
        ----------
           mobj: measurement object
              object to be added
        :param operation:
        :return:
        """
        # cylcle through all the series
        for series in mobj.series:
            self.remove_series_from_mdict(mobj=mobj, series=series, mdict_type=mdict_type)

    def add_series2_mdict(self, mobj, series, mdict_type='mdict'):
        self.change_series_in_mdict(mobj=mobj, series=series, operation='append', mdict_type=mdict_type)

    def remove_series_from_mdict(self, mobj, series, mdict_type='mdict'):
        self.change_series_in_mdict(mobj=mobj, series=series, operation='remove', mdict_type=mdict_type)

    def change_series_in_mdict(self, mobj, series, operation, mdict_type='mdict'):
        # dict for getting the info of the series
        sinfo = {'mtype': mobj.mtype, 'stype': series.stype, 'sval': series.value}

        mdict = getattr(self, mdict_type)

        if series in mdict['series'] and operation == 'append':
            self.logger.info('SERIES << %s >> already in mdict' %series)
            return

        # cycle through all the elements of the self.mdict
        for level in mdict:
            # get sublevels of the level
            sublevels = level.split('_')
            if level == 'measurements':
                append_if_not_exists(mdict['measurements'], mobj, operation=operation)
                # getattr(self.mdict['measurements'], operation)(mobj)
            elif level == 'series':
                append_if_not_exists(mdict['series'], series, operation=operation)

                # getattr(self.mdict['series'], operation)(series)
            elif len(sublevels) == 1:
                d = mdict[level].setdefault(sinfo[level], list())
                append_if_not_exists(d, mobj, operation=operation)
                # getattr(d, operation)(mobj)
            else:
                for slevel_idx, sublevel in enumerate(sublevels):
                    if slevel_idx == 0:
                        info0 = sinfo[sublevel]
                        d = mdict[level].setdefault(info0, dict())
                    elif slevel_idx != len(sublevels) - 1:
                        info0 = sinfo[sublevel]
                        d = d.setdefault(info0, dict())
                    else:
                        info0 = sinfo[sublevel]
                        d = d.setdefault(info0, list())
                        append_if_not_exists(d, mobj, operation=operation)

                        # getattr(d, operation)(mobj)

        if operation == 'remove':
            self.mdict_cleanup(mdict_type=mdict_type)

    def populate_mdict(self, mdict_type='mdict'):
        """
        Populates the mdict with all measurements
        :return:
        """
        if mdict_type == 'mdict':
            map(self.add_m2_mdict, self.measurements)
        if mdict_type == 'mean_mdict':
            add_m2_mean_mdict = partial(self.add_m2_mdict, mdict_type='mean_mdict')
            map(add_m2_mean_mdict, self.measurements)


    """ OLD INFO DICTIONARY """
    def _create_info_dict(self):
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
        out.update({'measurements': []})
        return out

    # todo remove
    def add_m2_info_dict(self, m):
        keys = self._info_dict.keys()
        for t in m.series:
            test = {'mtype': m.mtype, 'stype': t.stype, 'sval': t.value}
            for key in keys:
                levels = key.split('_')
                for i, level in enumerate(levels):
                    if level == 'measurements':
                        self._info_dict['measurements'].append(m)
                        continue
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

    # todo remove
    def remove_m_from_info_dict(self, m):
        """
        removes a measurement from the info_dict
        :param m:
        :return:
        """
        empty_cells = []
        if m in self.info_dict['measurements']:
            for key, value in sorted(self.info_dict.iteritems()):
                # remove from self.measurements
                if isinstance(value, list):
                    if m in value:
                        self.info_dict[key].remove(m)
                else:
                    # cycle through first level: e.g. sval, stype, mtype...
                    for k0, v0 in sorted(value.iteritems()):
                        if isinstance(v0, list):
                            if m in v0:
                                v0.remove(m)
                                if not v0:
                                    empty_cells.append([key, k0])
                        else:
                            for k1, v1 in sorted(v0.iteritems()):
                                if isinstance(v1, list):
                                    if m in v1:
                                        v1.remove(m)
                                else:
                                    for k2, v2 in sorted(v1.iteritems()):
                                        if isinstance(v2, list):
                                            if m in v2:
                                                v2.remove(m)
            self.remove_empty_val_from_info_dict()
        else:
            self.logger.warning('MEASUREMENT << %s >> not found' % m)


    # todo remove
    def remove_empty_val_from_info_dict(self):
        """
        recursively removes all empty lists from dictionary
        :param empties_list:
        :return:
        """
        for k0, v0 in sorted(self.info_dict.iteritems()):
            if isinstance(v0, dict):
                for k1, v1 in sorted(v0.iteritems()):
                    if isinstance(v1, dict):
                        for k2, v2 in sorted(v1.iteritems()):
                            if isinstance(v2, dict):
                                for k3, v3 in sorted(v2.iteritems()):
                                    if not v3:
                                        v2.pop(k3)
                                    if not v2:
                                        v1.pop(k2)
                                    if not v1:
                                        v0.pop(k1)
                            else:
                                if not v2:
                                    v1.pop(k2)
                                if not v1:
                                    v0.pop(k1)
                    else:
                        if not v1:
                            v0.pop(k1)

    # todo remove
    def recalc_info_dict(self):
        """
        calculates a dictionary with information and the corresponding measurement

        :return:

        """
        self._info_dict = self._create_info_dict()
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
                         'name', 'index', 'color',
                         'measurements',
                         '_filtered_data', 'sgroups',
                         '_info_dict', #todo remove
                         '_mdict',
                         'is_mean', 'mean_measurements', '_mean_results',
                         'results',
                     )}
        return pickle_me

    def mean_results(self, **parameter):
        if not self._mean_results:
            self.calc_all_mean_results(**parameter)
        return self._mean_results

    def __repr__(self):
        return '<< RockPy.Sample[%s] >>' % self.name

    def __add__(self, other):
        """
        adding two samples results in the adding of the sample.measurements lists
        :param other:
        :return:
        """
        # todo decide on how to handle mdict
        first = deepcopy(self)

        for m in other.measurements:
            m.sample_obj = first

        first.measurements.extend(other.measurements)
        first.recalc_info_dict()
        return first

    def __getattr__(self, name):
        if name in self.mdict:
            return self.mdict[name]
        else:
            # Default behaviour
            raise AttributeError

    ''' ADD FUNCTIONS '''

    def add_measurement(self,
                        mtype=None, mfile=None, machine='generic',  # general
                        fname=None, folder=None, path=None,  # added for automatic import of pathnames
                        idx=None,
                        mdata=None, mobj=None,
                        # create_parameter = False,
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
           create_parameter: bool NOT IMPLEMENTED YET
              default: False
                  if true it will create the parameter (lenght, mass) measurements from path
                  before creating the actual measurement
              Note: NEEDS PATH with RockPy complient fname structure.
            mobj: RockPy.Measurement object
              if provided, the object is added to self.measurements


        Returns
        -------
            RockPy.measurement object

        :mtypes:

        - mass
        '''

        #todo change series to list(tuples)
        ### FILE IMPORT
        file_info = None  # file_info includes all info needed for creation of measurement instance

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

        # create the file_info dictionary for classic import
        elif mtype:
            mtype = mtype.lower()
            file_info = dict(sample_obj=self,
                             mtype=mtype, mfile=mfile, machine=machine,
                             m_idx=idx, mdata=mdata)
        if options:
            file_info.update(options)

        if file_info or mobj:
            mtype = file_info['mtype']
            if mtype in Sample.implemented_measurements() or mobj:
                self.logger.info(' ADDING\t << measurement >> %s' % mtype)
                if mobj:
                    measurement = mobj
                else:
                    measurement = Sample.implemented_measurements()[mtype](**file_info)
                if measurement.has_data:
                    self.measurements.append(measurement)
                    self.raw_measurements.append(deepcopy(measurement))
                    self.add_m2_info_dict(measurement) # todo remove when infodict cleanup
                    self.add_m2_mdict(measurement)
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

    @property #todo remove?
    def info_dict(self): #todo remove
        # self._info_dict.update(dict(measurements=self.measurements))
        # if not hasattr(self, '_info_dict'):
        # self.recalc_info_dict()
        return self._info_dict

    @property #todo remove?
    def mtypes(self): #todo remove
        """
        returns list of all mtypes
        """
        return sorted(self._info_dict['mtype'].keys())

    @property #todo remove?
    def stypes(self): #todo remove
        """
        returns a list of all stypes
        """
        return sorted(self._info_dict['stype'].keys())

    @property #todo remove?
    def svals(self): #todo remove
        """
        returns a list of all stypes
        """

        return sorted(self._info_dict['sval'].keys())

    @property #todo remove?
    def mtype_tdict(self):  # todo: delete?
        """
        dictionary with all measurement_types {mtype:[tretments to corresponding m]}
        """
        out = {}
        for mtype in self.mtypes:
            aux = []
            for m in self.get_measurements(mtypes=mtype):
                aux.extend(m.series)
            out.update({mtype: aux})
        return out

    @property #todo remove?
    def stype_dict(self): #todo remove
        """
        dictionary with all series_types {stype:[list of measurements]}

        example:
        >>> {'pressure': [<RockPy.Measurements.parameters.Mass object at 0x10e196150>, <RockPy.Measurements.parameters.Diameter object at 0x10e1962d0>]}
        """
        return self._info_dict['stype']

    @property #todo remove?
    def mtype_stype_dict(self): #todo remove
        """
        returns a dictionary of mtypes, with all stypes in that mtype
        """
        # out = {mtype: self.__sort_list_set([stype for m in self.get_measurements(mtype=mtype) for stype in m.stypes])
        # for mtype in self.mtypes}
        return {k: v.keys() for k, v in self._info_dict['mtype_stype'].iteritems()}

    @property #todo remove?
    def mtype_stype_mdict(self): #todo remove
        """
        returns a dictionary of mtypes, with all stypes in that mtype
        """
        # out = {mtype: {stype: self.get_measurements(mtype=mtype, stype=stype)
        # for stype in self.mtype_stype_dict[mtype]}
        # for mtype in self.mtypes}
        return self._info_dict['mtype_stype']

    @property #todo remove?
    def stype_sval_dict(self): #todo remove
        # out = {stype: self.__sort_list_set([m.stype_dict[stype].value for m in self.stype_dict[stype]]) for stype in
        # self.stypes}
        return {k: v.keys() for k, v in self._info_dict['stype_sval'].iteritems()}

    @property #todo remove?
    def mtype_stype_sval_mdict(self): #todo remove
        # out = {mt:
        # {tt: {tv: self.get_measurements(mtype=mt, stype=tt, sval=tv)
        # for tv in self.stype_sval_dict[tt]}
        # for tt in self.mtype_stype_dict[mt]}
        # for mt in self.mtypes}
        return self._info_dict['mtype_stype_sval']

    ''' FILTER FUNCTIONS '''

    def filter(self, mtype=None, stype=None, sval=None, sval_range=None,
               **kwargs):
        #todo should now remove measurements that are non complient to criteria from sample.measurements
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
        self._filtered_data = self.get_measurements(mtypes=mtype,
                                                    stypes=stype, svals=sval, sval_range=sval_range, filtered=False)
        return self._filtered_data

    def reset_filter(self):
        """
        rests filter applied using sample.filter()
        :return:
        """
        # todo should now add MISSING (not all because of possible calculations) from _raw_measurements back to measurements
        self._filtered_data = None

    ''' FIND FUNCTIONS '''

    def get_measurements(self,
                         mtypes=None,
                         series=None,
                         stypes=None, svals=None, sval_range=None,
                         mean=False,
                         invert = False,
                         **options):
        """
        Returns a list of measurements of type = mtypes

        Parameters
        ----------
           mtypes: list, str
              mtypes to be returned
           series: list(tuple)
              list of tuples, to search for several sepcific series. e.g. [('mtime',4),('gc',2)] will only return
              mesurements that fulfill both criteria.
              Supercedes stype, sval and sval_range. Returnes only measurements that meet series exactly!
           stypes: list, str
              series type
           sval_range: list, str
              series range e.g. sval_range = [0,2] will give all from 0 to 2 including 0,2
              also '<2', '<=2', '>2', and '>=2' are allowed.
           svals: float
              series value to be searched for.
              caution:
                 will be overwritten when sval_range is given
           invert:
              if invert true it returns only measurements that do not meet criteria
           sval_range:
              can be used to look up measurements within a certain range. if only one value is given,
                     it is assumed to be an upper limit and the range is set to [0, sval_range]
           mean: bool
              not implemented, yet^

        Returns
        -------
           list
              list of RockPy.Measurements that meet search criteria or if invert is True, do not meet criteria.

        Note
        ----
            there is no connection between stype and sval. This may cause problems. I you have measurements with
               M1: [pressure, 0.0, GPa], [temperature, 100.0, C]
               M2: [pressure, 1.0, GPa], [temperature, 100.0, C]
            and you search for stypes=['pressure','temperature'], svals=[0,100]. It will return both M1 and M2 because
            both M1 and M2 have [temperature, 100.0, C].

        """
        mtypes = to_list(mtypes)
        stypes = to_list(stypes)
        svals = to_list(svals)

        if mean:
            mdict = self.mean_mdict
            mdict_type = 'mean_mdict'
        else:
            mdict = self.mdict
            mdict_type = 'mdict'

        if sval_range:
            if isinstance(sval_range, list):
                svals = [i for i in mdict['sval'] if sval_range[0] <= i <= sval_range[1]]
            if isinstance(sval_range, str):
                sval_range = sval_range.strip() #remove whitespaces in case '> 4' is provided
                if '<' in sval_range:
                    if '=' in sval_range:
                        svals = [i for i in mdict['sval'] if i <= float(sval_range.replace('<=',''))]
                    else:
                        svals = [i for i in mdict['sval'] if i < float(sval_range.replace('<',''))]
                if '>' in sval_range:
                    if '=' in sval_range:
                        svals = [i for i in mdict['sval'] if i >= float(sval_range.replace('>=',''))]
                    else:
                        svals = [i for i in mdict['sval'] if i > float(sval_range.replace('>',''))]
            self.logger.info('SEARCHING %s for sval_range << %s >>' %(mdict_type, ', '.join(map(str, svals))))

        out = []

        if not series:
            for mtype in mtypes:
                for stype in stypes:
                    for sval in svals:
                        measurements = self.get_mtype_stype_sval(mtype=mtype, stype=stype, sval=sval,
                                                                 mdict_type=mdict_type)
                        for m in measurements:
                            if not m in out:
                                out.append(m)
        else:
            # searching for specific series, all mtypes specified that fit the series description will be returned
            series = to_list(series)
            for mtype in mtypes: #cycle through mtypes
                aux = []
                for s in series:
                    aux.extend(self.get_mtype_stype_sval(mtype=mtype, stype=s[0], sval=float(s[1])))
                out.extend(list(set([i for i in aux if aux.count(i) == len(series)])))

        # invert list to contain only measurements that do not meet criteria
        if invert:
            out = [i for i in mdict['measurements'] if not i in out]
        return out

    def get_mtype_stype_sval(self, mtype, stype, sval, mdict_type='mdict'):
        """
        Searches for a single set of mtype, stype, sval

        Parameters
        ----------
           mtype: str
              mtype to be looked up
           stype: str
              stype to be looked up
           sval: float
              sval to be looked up
           mdict_type:
              chose which mdict to use:
                 e.g. 'mdict' -> lookup in measurement_dictionary
                 or.  'mean_mdict' -> lookup in mean_measurement_dictionary
        """
        self.logger.info('SEARCHING\t measurements with  << %s, %s, %s >>' % (mtype, stype, sval))

        # searching for no value returns all measurements
        if not mtype and not stype and not sval:
            if mdict_type == 'mdict':
                return self.measurements
            if mdict_type == 'mean_mdict':
                return self.mean_measurements

        # get right mdict for lookup:
        mdict = getattr(self, mdict_type)
        # create dictionary with mtypes, stypes, svals search parameters
        lookup_dict = {mtype:'mtype', stype:'stype', sval:'sval'}
        # create string for mdict lookup e.g. if mtypes and stypes is given then svals == None -> lookup = mtype_stype
        # and we can search in Sample.mdict[mtype_stype] for the measurements
        lookup = '_'.join([lookup_dict[i] for i in sorted(lookup_dict) if i is not None])
        # create reverse dict for lookup of value
        rev_lookup_dict = {v:k for k,v in lookup_dict.iteritems()}

        # copy of mdict[lookup] for dynamic lookup of arbitrary level depth
        out = mdict[lookup]
        for i in lookup.split('_'): #cycle through levels
            # catch Keyerror exception for question without answer
            try:
                # store next level
                out = out[rev_lookup_dict[i]]
            # if key not exists return empty list
            except KeyError:
                self.logger.error('CANT find measurement with << %s: %s >> in %s'%(i, rev_lookup_dict[i], mdict_type))
                return []
        return out

    def remove_measurements(self, mtypes=None, stypes=None, svals=None, sval_range=None, **options):
        measurements_for_del = self.get_measurements(mtypes=mtypes,
                                                     stypes=stypes, svals=svals, sval_range=sval_range,
                                                     **options)
        if measurements_for_del:
            self.measurements = [m for m in self.measurements if not m in measurements_for_del]

    ''' MISC FUNTIONS '''

    def mean_measurement(self,
                         mtype=None, stype=None, sval=None, sval_range=None, mlist=None,
                         interpolate=True, recalc_mag=False,
                         substfunc='mean',
                         reference=None, ref_dtype='mag', norm_dtypes='all', vval=None, norm_method='max',
                         normalize_variable=False, dont_normalize=None,
                         add2list=True):

        """
        takes a list of measurements and creates a mean measurement out of all measurements data

        Parameters
        ----------
           mlist:
           interpolate:
           recalc_mag:
           add2list: bool
              will add measurement to the mean_measurements list

        Returns
        -------
           RockPy.Measurement
              The mean measurement that fits to the specified lookup


        """
        if not mtype:
            # raise ValueError('No mtype specified')

            self.logger.error('NO mtype specified. Please specify mtype')
            return

        mlist = self.get_measurements(mtypes=mtype, stypes=stype, svals=sval, sval_range=sval_range, mean=False)

        if reference:
            mlist = [m.normalize(reference=reference, ref_dtype=ref_dtype, norm_dtypes=norm_dtypes, vval=vval,
                                 norm_method=norm_method, normalize_variable=normalize_variable,
                                 dont_normalize=dont_normalize) for m in mlist]
        # get common series
        series = list(set(['%s_%.3f_%s' %(s.stype, s.value, s.unit) for m in mlist for s in m.series]))
        series = [i.split('_') for i in series]

        if not mlist:
            self.logger.warning('NO measurement found >> %s, %s, %f >>' %(mtype, stype, sval))
            return None

        if len(mlist) == 1:
            self.logger.warning('Only one measurement found returning measurement')
            return mlist[0]

        # use first measurement as base
        dtypes = get_common_dtypes_from_list(mlist=mlist)

        # create a base measurement
        base_measurement = RockPy.Functions.general.create_dummy_measurement(mtype=mlist[0].mtype,
                                                                             machine=mlist[0].machine,
                                                                             mdata=deepcopy(mlist[0].data), sample=self)
        # delete uncommon dtype from base_measurement
        for key in base_measurement.data:
            if key not in dtypes:
                base_measurement.data.pop(key)

        for dtype in dtypes:  # cycle through all dtypes e.g. 'down_field', 'up_field' for hysteresis
            dtype_list = [m.data[dtype] for m in mlist] # get all data for dtype in one list

            if interpolate:
                varlist = self.__get_variable_list(dtype_list, var='temp') #todo check why var=temp
                if len(varlist) > 1:
                    dtype_list = [m.interpolate(varlist) for m in dtype_list]

            if len(dtype_list) > 1:  # for single measurements
                base_measurement.data[dtype] = condense(dtype_list, substfunc=substfunc)
                base_measurement.data[dtype] = base_measurement.data[dtype].sort('variable')

            if recalc_mag:
                base_measurement.data[dtype].define_alias('m', ('x', 'y', 'z'))
                base_measurement.data[dtype]['mag'].v = base_measurement.data[dtype].magnitude('m')

        # check if there is an initial state measurement and mean them, too.
        if base_measurement.initial_state:
            for dtype in base_measurement.initial_state.data:
                dtype_list = [m.initial_state.data[dtype] for m in mlist if m.initial_state]
                base_measurement.initial_state.data[dtype] = condense(dtype_list, substfunc=substfunc)
                base_measurement.initial_state.data[dtype] = base_measurement.initial_state.data[dtype].sort('variable')
                if recalc_mag:
                    base_measurement.initial_state.data[dtype].define_alias('m', ('x', 'y', 'z'))
                    base_measurement.initial_state.data[dtype]['mag'].v = base_measurement.initial_state.data[
                        dtype].magnitude(
                        'm')

        base_measurement.sample_obj = self

        # add all comon series to mean_m_object
        for s in series:
            base_measurement.add_sval(stype=s[0], sval=float(s[1]), unit=s[2])

        # add to self.mean_measurements if specified
        if add2list:
            self.mean_measurements.append(base_measurement)
            self.add_m2_mdict(mobj=base_measurement, mdict_type='mean_mdict')
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
            mlist = self.get_measurements(mtypes=mtype, stypes=stype, svals=sval, sval_range=sval_range, filtered=filtered)

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
            mlist = self.get_measurements(mtypes=mtype,
                                          stypes=stype, svals=sval, sval_range=sval_range,
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

    def sort_mlist_in_stype_dict(self, mlist): #todo needed?
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

def append_if_not_exists(elist, element, operation):
    if operation == 'append':
        if not element in elist:
            elist.append(element)
    if operation == 'remove':
        if element in elist:
            elist.remove(element)
    return elist