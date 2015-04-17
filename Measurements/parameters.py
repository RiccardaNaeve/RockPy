__author__ = 'volk'
from base import Measurement
from RockPy.Functions.convert import convert2
import RockPy
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

        self._raw_data = {'data': RockPy.RockPyData(column_names=['mass', 'time', 'std_dev'])}
        self._raw_data['data']['mass'] = value * mass_conversion
        self._raw_data['data']['time'] = time
        self._raw_data['data']['std_dev'] = std


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
                                     direction=None,
                                     **options)
        self.mtype = mtype
        self.machine = machine
        self.direction = direction

        length_conversion = convert2(unit, 'm', 'length')

        self._raw_data = {'data': RockPy.RockPyData(column_names=[mtype, 'time', 'std_dev'])}
        self._raw_data['data'][mtype] = value * length_conversion
        self._raw_data['data']['time'] = time
        self._raw_data['data']['std_dev'] = std

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


class Volume(Measurement):
    """
    Combined measurement. It needs a height and a diameter measurement.
    """

    def __init__(self, sample_obj,
                 mtype, mfile=None, machine='combined',
                 height=None, diameter=None, sample_shape='cylinder',
                 std=None, time=None,
                 **options):
        super(Volume, self).__init__(sample_obj=sample_obj,
                                     mtype=mtype, mfile=mfile, machine='combined',
                                     **options)
        self.sample_shape = sample_shape

        if sample_shape == 'cylinder':
            self.height_data = height.data['data']['height'].v[0]
            self.diameter_data = diameter.data['data']['diameter'].v[0]

        # store in RockPy Data object
        self._raw_data = {'data': RockPy.RockPyData(column_names=['diameter', 'time', 'std_dev'])}
        self._raw_data['data'][mtype] = volume
        self._raw_data['data']['time'] = time
        self._raw_data['data']['std_dev'] = std

    def cylinder(self):
        return np.pi * (self.diameter_data/2) * self.height_data


def test():
    Sample = RockPy.Sample(name='parameter_test',
                           mass=10., mass_unit='kg',
                           height=4.5, diameter=6., length_unit='mm')
    print Sample.volume

if __name__ == '__main__':
    test()