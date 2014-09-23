__author__ = 'volk'
import base
from Structure.data import data
from Functions.convert import convert2
import numpy as np


class mass(base.measurement):
    '''
    simple 1d measurement for mass
    '''

    def __init__(self, sample_obj,
                 mtype='mass', mfile=None, machine='generic',
                 value=1.0, unit='kg',
                 log=None,
                 std=None, time=None,
                 **options):
        log = None  # 'RockPy.MEASUREMENT.mass'

        super(mass, self).__init__(sample_obj=sample_obj,
                                   mtype=mtype, mfile=mfile, machine=machine,
                                   log=log,
                                   **options)

        mass_conversion = convert2(unit, 'kg', 'mass')

        self.data = data(variable=np.array(0.0), measurement=np.array(value * mass_conversion),
                         var_unit='idx', measure_unit='kg',
                         time=time, std_dev=std)


class length(base.measurement):
    '''
    simple 1d measurement for mass
    '''

    def __init__(self, sample_obj,
                 mtype, mfile=None, machine=None,
                 value=1.0, unit='m',
                 log=None,
                 std=None, time=None,
                 **options):
        log = 'RockPy.MEASUREMENT.length'
        super(length, self).__init__(sample_obj=sample_obj,
                                     mtype=mtype, mfile=mfile, machine=machine,
                                     log=log,
                                     **options)
        self.mtype = mtype
        self.machine = machine
        mass_conversion = convert2(unit, 'm', 'length')

        self.data = data(variable=np.array(0.0), measurement=np.array(value * mass_conversion),
                         var_unit='idx', measure_unit='m',
                         time=time, std_dev=std)

