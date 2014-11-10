# coding=utf-8
__author__ = 'Michael Volk'
# for all project related classes
import logging
import numpy as np
from RockPy.Functions import general
from RockPy.Measurements.base import Measurement
from RockPy.Structure.data import RockPyData


class Sample():
    general.create_logger('RockPy.SAMPLE')

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

    def calc_all(self):
        for measurement in self.measurements:
            if not measurement.mtype in ['mass', 'height', 'diameter']:
                s_type = None
                measurement.calc_all()
                if measurement.suffix:
                    s_type, s_value, s_unit = measurement._get_treatment_from_suffix()
                if not self.results:
                    self.results = RockPyData(column_names=measurement.results.column_names,
                                              data=measurement.results.data, row_names=measurement.suffix)
                    # if s_type:
                    #     self.results.append_columns(s_type, s_value)
                else:
                    c_names = measurement.results.column_names
                    data = measurement.results.data
                    # if s_type:
                    #     c_names = np.append(c_names, s_type)
                    #     data = data[0][:, 0]
                    #     data = np.append(data, s_value)
                    # print data
                    # print c_names
                    rpdata = RockPyData(column_names=c_names, data=data, row_names=measurement.suffix)
                    self.results.append_rows(rpdata)


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


    ''' FIND FUNCTIONS '''

    def get_measurements(self, mtype, **options):
        """
        Returns a list of measurements of type = mtype
        :param mtype:
        :return:
        """
        self.log.debug('SEARCHING\t measurements with mtype << %s >>' % (mtype.lower()))
        out = [m for m in self.measurements if m.mtype == mtype.lower()]
        if options:
            out = [m for m in out for key in options if hasattr(m, key) if getattr(m, key) == options[key]]
        if len(out) != 0:
            self.log.info('FOUND\t sample << %s >> has %i measurements with mtype << %s >>' % (
                self.name, len(out), mtype.lower()))
        else:
            self.log.error('UNKNOWN\t mtype << %s >> or no measurement found' % mtype.lower())
            return None
        return out

