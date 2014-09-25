__author__ = 'volk'
from base import Measurement
from Structure.data import data
from Functions.convert import convert2
import numpy as np


class Mass(Measurement):
    """
    simple 1d measurement for mass
    """

    def __init__(self, sample_obj,
                 mtype='mass', mfile=None, machine='generic',
                 value=1.0, unit='kg',
                 std=None, time=None,
                 **options):
        super(Mass, self).__init__(sample_obj=sample_obj,
                                   mtype=mtype, mfile=mfile, machine=machine,
                                   **options)

        mass_conversion = convert2(unit, 'kg', 'mass')

        self.data = data(variable=np.array(0.0), measurement=np.array(value * mass_conversion),
                         var_unit='idx', measure_unit='kg',
                         time=time, std_dev=std)


class Length(Measurement):
    """
    simple 1d measurement for mass
    """

    def __init__(self, sample_obj,
                 mtype, mfile=None, machine=None,
                 value=1.0, unit='m',
                 std=None, time=None,
                 **options):
        super(Length, self).__init__(sample_obj=sample_obj,
                                     mtype=mtype, mfile=mfile, machine=machine,
                                     **options)
        self.mtype = mtype
        self.machine = machine
        mass_conversion = convert2(unit, 'm', 'length')

        self.data = data(variable=np.array(0.0), measurement=np.array(value * mass_conversion),
                         var_unit='idx', measure_unit='m',
                         time=time, std_dev=std)
