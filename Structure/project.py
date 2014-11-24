# coding=utf-8
__author__ = 'Michael Volk'
# for all project related classes
import logging
import numpy as np
from RockPy.Functions import general
from RockPy.Measurements.base import Measurement
from RockPy.Structure.data import RockPyData

general.create_logger('RockPy.SAMPLE')


class Sample():
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

    def __init__(self, name,
                 mass=1, mass_unit='kg', mass_machine='generic',
                 height=1, diameter=1, length_unit='mm', length_machine='generic',
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
        self.log = logging.getLogger('RockPy.SAMPLE')
        self.log.info('CREATING\t new sample << %s >>' % self.name)

        self.measurements = []
        self.results = None

        if mass is not None:
            self.add_measurement(mtype='mass', mfile=None, machine=mass_machine,
                                 value=float(mass), unit=mass_unit)
        if diameter is not None:
            self.add_measurement(mtype='diameter', mfile=None, machine=length_machine,
                                 value=float(diameter), unit=length_unit)
        if height is not None:
            self.add_measurement(mtype='height', mfile=None, machine=length_machine,
                                 value=float(height), unit=length_unit)

    def __repr__(self):
        return '<< %s - Structure.sample.Sample >>' % self.name

    ''' ADD FUNCTIONS '''

    def add_measurement(self,
                        mtype=None, mfile=None, machine='generic',  # general
                        **options):
        '''
        All measurements have to be added here

        :param mtype: str - the type of measurement
        :param mfile: str -  the measurement file
        :param machine: str - the machine from which the file is output
        :param mag_method: str - only used for af-demag
        :return: RockPyV3.measurement object

        :mtypes:

        - mass
        '''
        mtype = mtype.lower()

        implemented = {i.__name__.lower(): i for i in Measurement.inheritors()}
        if mtype in implemented:
            self.log.info(' ADDING\t << measurement >> %s' % mtype)
            measurement = implemented[mtype](self,
                                             mtype=mtype, mfile=mfile, machine=machine,
                                             **options)
            if measurement.has_data:
                self.measurements.append(measurement)
                return measurement
            else:
                return None
        else:
            self.log.error(' << %s >> not implemented, yet' % mtype)

    def calc_all(self, **options):
        for measurement in self.measurements:
            if not measurement.mtype in ['mass', 'height', 'diameter']:
                s_type = None
                measurement.calc_all(**options)
                if measurement.suffix:
                    s_type, s_value, s_unit = measurement._get_treatment_from_suffix()
                if not self.results:
                    self.results = RockPyData(column_names=measurement.results.column_names,
                                              data=measurement.results.data, row_names=measurement.suffix)
                    # if s_type:
                    # self.results.append_columns(s_type, s_value)
                else:
                    c_names = measurement.results.column_names
                    data = measurement.results.data
                    # if s_type:
                    # c_names = np.append(c_names, s_type)
                    # data = data[0][:, 0]
                    # data = np.append(data, s_value)
                    # print data
                    # print c_names
                    rpdata = RockPyData(column_names=c_names, data=data, row_names=measurement.suffix)
                    self.results = self.results.append_rows(rpdata)

    @property
    def mass_kg(self):
        measurements = self.get_measurements(mtype='mass')
        if len(measurements) > 1:
            self.log.info('FOUND more than 1 << mass >> measurement. Returning first')
        try:
            return measurements[0].data['mass'][0]
        except IndexError:  # todo fix
            return 1

    @property
    def height_m(self):
        measurement = self.get_measurements(mtype='height')
        if len(measurement) > 1:
            self.log.info('FOUND more than 1 << height >> measurement. Returning first')
        return measurement[0].data['height'][0]

    @property
    def diameter_m(self):
        measurement = self.get_measurements(mtype='diameter')
        if len(measurement) > 1:
            self.log.info('FOUND more than 1 << diameter >> measurement. Returning first')
        return measurement[0].data['diameter'][0]

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
    def mtype_dict(self):
        """
        dictionary with all measurement_types {mtype:[list of measurements]}

        example:
        >>> {'thellier': [<RockPy.Measurements.parameters.Mass object at 0x10e196150>, <RockPy.Measurements.parameters.Diameter object at 0x10e1962d0>]}
        """

        out = {mtype: self.get_measurements(mtype=mtype) for mtype in self.mtypes}
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
        for ttype in self.ttypes}
        for mtype in self.mtypes}
        return out

    @property
    def ttype_tval_dict(self):
        out = {ttype: self.__sort_list_set([m.ttype_dict[ttype].value for m in self.ttype_dict[ttype]]) for ttype in self.ttypes}
        return out

    @property
    def mtype_ttype_tval_dict(self):
        out = {mt:
                   {tt: {tv: self.get_measurements(mtype=mt, ttype=tt, tval=tv)
                         for tv in self.ttype_tval_dict[tt]}
                    for tt in self.mtype_ttype_dict[mt]}
               for mt in self.mtypes}
        return out

    ''' FIND FUNCTIONS '''

    def get_measurements(self, mtype=None, ttype=None, tval=None, tval_range=None, **options):
        """
        Returns a list of measurements of type = mtype

        :tval_range: can be used to look up measurements within a certain range. if only one value is given,
                     it is assumed to be an upper limit and the range is set to [0, tval_range]


        :param mtype:
        :return:
        """
        if not tval:
            tvalue = np.nan
        else:
            if isinstance(tval, list):
                tvalue = ''.join(map(str, tval))
            else:
                tvalue = str(tval)

        self.log.debug('SEARCHING\t measurements with  << %s, %s, %s >>' % (mtype, ttype, tvalue))

        out = [m for m in self.measurements]

        if not mtype is None:
            out = [m for m in out if m.mtype == mtype]

        if not ttype is None:
            if isinstance(ttype, list):
                out = [m for m in out for t in ttype if t in m.ttypes]
            else:
                out = [m for m in out if ttype in m.ttypes]

        if not tval is None:
            if isinstance(tval, list):
                out = [m for m in out for val in tval if val in m.tvals]
            else:
                out = [m for m in out if tval in m.tvals]

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
            self.log.error(
                'UNKNOWN\t << %s, %s, %s >> or no measurement found for sample << %s >>' % (
                    mtype, ttype, tvalue, self.name))
            return

        return out

    def get_measurements_with_treatment(self, ttype, **options):
        self.log.debug('SEARCHING\t measurements with treatment type << %s >>' % (ttype.lower()))
        out = [m for m in self.measurements for t in m.treatments if t.ttype == ttype.lower()]

        if len(out) != 0:
            self.log.info('FOUND\t sample << %s >> has %i measurements with treatment << %s >>' % (
                self.name, len(out), ttype.lower()))
        else:
            self.log.error(
                'UNKNOWN\t treatment << %s >> or no measurement found for sample << %s >>' % (ttype.lower(), self.name))
            return []
        return out

    def __sort_list_set(self, values):
        """
        returns a sorted list of non duplicate values
        :param values:
        :return:
        """
        return sorted(list(set(values)))