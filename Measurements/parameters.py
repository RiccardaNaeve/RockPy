from ..Structure.data import RockPyData

__author__ = 'volk'
from base import Measurement
from RockPy.Functions.convert import convert2


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

        self._raw_data = {'data': RockPyData(column_names=['mass', 'time', 'std_dev'])}
        self._raw_data ['data']['mass'] = value * mass_conversion
        self._raw_data ['data']['time'] = time
        self._raw_data ['data']['std_dev'] = std


    def format_generic(self):
        pass


class Length(Measurement):
    """
    simple 1d measurement for Length
    """

    def __init__(self, sample_obj,
                 mtype, mfile=None, machine='generic',
                 value=1.0, unit='m',
                 std=None, time=None,
                 **options):
        super(Length, self).__init__(sample_obj=sample_obj,
                                     mtype=mtype, mfile=mfile, machine=machine,
                                     **options)
        self.mtype = mtype
        self.machine = machine
        length_conversion = convert2(unit, 'm', 'length')

        self._raw_data  = {'data':RockPyData(column_names=[mtype, 'time', 'std_dev'])}
        self._raw_data ['data'][mtype] = value * length_conversion
        self._raw_data ['data']['time'] = time
        self._raw_data ['data']['std_dev'] = std

    def format_generic(self):
        pass


class Diameter(Length):
    """
    simple 1d measurement for Length
    """
    pass


class Height(Length):
    """
    simple 1d measurement for Length
    """
    pass