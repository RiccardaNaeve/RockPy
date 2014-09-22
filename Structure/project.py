# coding=utf-8
__author__ = 'Michael Volk'
# for all project related classes
from Functions import convert, general
import logging
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import csv

class Sample():
    general.create_logger('RockPy.SAMPLE')

    def __init__(self, name, mass=1.0, mass_unit=None, height=None, diameter=None, length_unit=None):
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

        if mass_unit:
            mass_factor = convert.convert2(mass_unit, 'kg', 'mass')
        else:
            self.log.info(' MISSING\t length_unit: assuming << mm >>')
            mass_factor = convert.convert2('mg', 'kg', 'mass')

        if mass:
            self.mass_kg = mass * mass_factor
            self.log.debug(' ADDING\t << mass >> input: %.1f [%s] stored: %1f [kg]' % (mass, mass_unit, self.mass_kg))
        else:
            self.log.debug('MISSING\t << mass >>')
            self.mass_kg = None

        # get length _unit for conversion
        if length_unit:
            length_factor = convert.convert2(length_unit, 'm', 'length')
        else:
            self.log.info(' MISSING\t mass_unit: assuming << mg >>')
            length_factor = convert.convert2('mm', 'm', 'length')

        if height:
            self.height_m = float(height) * length_factor
            self.log.debug(
                ' ADDING\t << height >> input: %.1f [%s] stored: %1f [m]' % (height, length_unit, self.height_m))

        else:
            self.log.debug('MISSING\t << height >>')
            self.height_m = None

        if diameter:
            self.diameter_m = float(diameter) * length_factor
            self.log.debug(
                ' ADDING\t << diameter >> input: %.1f [%s] stored: %1f [m]' % (diameter, length_unit, self.diameter_m))

        else:
            self.log.debug('MISSING\t << diameter >>')
            self.diameter_m = None

    def __repr__(self):
        return '<< %s - Structure.sample.Sample >>' %self.name
    ''' ADD FUNCTIONS '''

    def add_mass(self, mass, mass_unit='mg'):
        '''
        Adds mass to the sample object

        :param mass: float
        :param mass_unit: str

        changes sample.mass_kg from its initial value to a new value.
        mass unit should be given, if other than 'mg'. See convert2 helper function
        #todo point to helper
        '''
        self.mass_kg = float(mass) * convert.convert2(mass_unit, 'kg', 'mass')
        self.log.debug(' ADDING\t << mass >> input: %.1f [%s] stored: %1f [kg]' % (mass, mass_unit, self.mass_kg))

    def add_height(self, height, length_unit='mm'):
        '''
        Adds height in m to sample

        :param height: float
        :param length_unit: str

        changes sample.height_m from its initial value to a new value.
        Length unit should be given, if other than 'mm'. See convert2 helper function
        #todo point to helper
        '''
        self.height_m = float(height) * convert.convert2(length_unit, 'm', 'length')
        self.log.debug(' ADDING\t << height >> input: %.1f [%s] stored: %1f [m]' % (height, length_unit, self.height_m))

    def add_diameter(self, diameter, length_unit='mm'):
        '''
        Adds diameter in m to sample

        :param diameter: float
        :param length_unit: str

        changes sample.diameter_m from its initial value to a new value.
        Length unit should be given, if other than 'mm'. See convert2 helper function
        #todo point to helper
        '''
        self.diameter_m = float(diameter) * convert.convert2(length_unit, 'm', 'length')
        self.log.debug(
            ' ADDING\t << diameter >> input: %.1f [%s] stored: %1f [m]' % (diameter, length_unit, self.diameter_m))

    def add_measurement(self,
                        mtype=None, mfile=None, machine=None,  # general
                        mag_method='',  # IRM
                        af_obj=None, parm_obj=None,  # pseudo-thellier
                        **options):
        '''

        :param mtype: str - the type of measurement
        :param mfile: str -  the measurement file
        :param machine: str - the machine from which the file is output
        :param mag_method: str - only used for af-demag
        :return: RockPyV3.measurement object

        :mtypes:

        - af-demagnetization - 'af-demag'
        - hysteresis - 'hys'
        - Thellier-Thellier - 'thellier'
        - Zero Field Cooling-  'zfc'
        - IRM acquisition - 'irm'
        - Backfield - 'coe'
        - Viscosity - 'visc'

        '''

        # options = {'af_obj':af_obj, 'parm_obj':parm_obj}


        implemented = {
            'af-demag': measurements.Af_Demag,
            'af': measurements.Af_Demag,
            'hys': measurements.Hysteresis,
            'palint': measurements.Thellier,
            'thellier': measurements.Thellier,
            'zfc': measurements.Zfc_Fc,
            'irm': measurements.Irm,
            'coe': measurements.Coe,
            'visc': measurements.Viscosity,
            'parm-spectra': measurements.pARM_spectra,
            'pseudo-thellier': measurements.Pseudo_Thellier,
            'rmp': measurements.Thermo_Curve,
            'forc': measurements.Forc,
        }

        if mtype.lower() in implemented:
            self.log.info(' ADDING\t << measurement >> %s' % mtype)
            measurement = implemented[mtype.lower()](self,
                                                     mtype=mtype, mfile=mfile, machine=machine,
                                                     mag_method=mag_method,
                                                     af_obj=af_obj, parm_obj=parm_obj,
                                                     **options
            )
            self.measurements.append(measurement)
            return measurement
        else:
            self.log.error(' << %s >> not implemented, yet' % mtype)


    ''' RETURN FUNCTIONS '''

    def mass(self, mass_unit='mg'):
        '''
        Returns mass in specified mass unit
        :param mass_unit: str - unit to be output
        :return: float - mass in mass_unit
        '''
        OUT = self.mass_kg * convert.convert2('kg', mass_unit, 'mass')
        return OUT

    def height(self, length_unit='mm'):
        OUT = self.height_m * convert.convert2('m', length_unit, 'length')
        return OUT

    def diameter(self, length_unit='mm'):
        OUT = self.diameter_m * convert.convert2('m', length_unit, 'length')
        return OUT

    def volume(self, length_unit='mm'):
        out = np.pi * (self.diameter(length_unit=length_unit) / 2) ** 2 * self.height(length_unit=length_unit)
        return out

    def infos(self, mass_unit='mg', length_unit='mm', header=True):
        text = '%s\t ' % self.name
        hdr = 'Sample\t '
        if self.mass_kg:
            text += '%.2f\t ' % (self.mass(mass_unit=mass_unit))
            hdr += 'mass [%s]\t ' % mass_unit
        if self.height_m:
            text += '%.2f\t ' % self.height(length_unit=length_unit)
            hdr += 'length [%s]\t ' % length_unit
        if self.diameter_m:
            text += '%.2f\t ' % self.height(length_unit=length_unit)
            hdr += 'diameter [%s]\t ' % length_unit
        if header:
            print hdr
        print text


    ''' FIND FUNCTIONS '''

    def find_measurement(self, mtype):
        self.log.info('SEARCHING\t measurements with mtype << %s >>' % (mtype.lower()))
        out = [m for m in self.measurements if m.mtype == mtype.lower()]
        if len(out) != 0:
            self.log.info('FOUND\t sample << %s >> has %i measurements with mtype << %s >>' % (
                self.name, len(out), mtype.lower()))
        else:
            self.log.error('UNKNOWN\t mtype << %s >> or no measurement found' % mtype.lower())
        return out


    ''' ADDITIONAL '''

    def Experiment(self):
        experiment_matrix = {
            'af-demag': {},
        }

    def plot(self):
        # def plot(self, norm='mass', out='show', virgin=False, folder=None, name='output.pdf', figure=None):

        fig = plt.figure()

        mtypes = list(set([i.mtype for i in self.measurements]))

        print mtypes


def sample_import(sample_file, mass_unit='mg', length_unit='mm'):
    '''
    imports a csv list with mass, diameter and height data.
    has to be tab separated e.g.:

        Sample	Mass	Height	Diameter
        1a	320.0	5.17	5.84

    example
    -------

    samples = RockPyV3.sample_import(sample_file = the_data_file.txt, mass_unit = 'mg', length_unit='mm')

    :param sample_file: str
    :param mass_unit: str
    :param length_unit: str
    '''
    log = logging.getLogger('RockPy.READIN.get_data')
    reader_object = csv.reader(open(sample_file), delimiter='\t')
    r_list = [i for i in reader_object]
    header = r_list[0]
    d_dict = {}

    for i in r_list[1:]:
        for j in range(1, len(i)):
            d_dict.update({i[0]: {header[j].lower(): float(i[j])}})
    # d_dict = {i[0]: {header[j].lower(): float(i[j]) for j in range(1, len(i))} for i in r_list[1:]}

    out = {}
    for sample in d_dict:
        mass = d_dict[sample].get('mass', None)
        height = d_dict[sample].get('height', None)
        diameter = d_dict[sample].get('diameter', None)
        aux = {sample: Sample(sample, mass=mass, height=height, diameter=diameter, mass_unit=mass_unit,
                              length_unit=length_unit)}
        out.update(aux)

    return out


