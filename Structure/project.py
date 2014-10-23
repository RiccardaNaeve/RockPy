# coding=utf-8
__author__ = 'Michael Volk'
# for all project related classes
import logging

from Functions import general
import Measurements.base


class Sample():
    general.create_logger('RockPy.SAMPLE')

    def __init__(self, name,
                 mass=None, mass_unit='kg', mass_machine='generic',
                 height=None, diameter=None, length_unit=None, length_machine='generic',
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

        implemented = {i.__name__.lower(): i for i in Measurements.base.Measurement.inheritors()}
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

    @property
    def mass_kg(self):
        measurement = self.get_measurements(mtype='mass')
        if len(measurement) > 1:
            self.log.info('FOUND more than 1 << mass >> measurement. Returning first')
        try:
            return measurement[0].data['mass'][0]
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

    def get_measurements(self, mtype):
        """
        Returns a list of measurements of type = mtype
        :param mtype:
        :return:
        """
        self.log.debug('SEARCHING\t measurements with mtype << %s >>' % (mtype.lower()))
        out = [m for m in self.measurements if m.mtype == mtype.lower()]
        if len(out) != 0:
            self.log.info('FOUND\t sample << %s >> has %i measurements with mtype << %s >>' % (
                self.name, len(out), mtype.lower()))
        else:
            self.log.error('UNKNOWN\t mtype << %s >> or no measurement found' % mtype.lower())
        return out
