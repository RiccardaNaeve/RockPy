__author__ = 'mike'

import base
from RockPy.Structure.data import RockPyData


class generic_moment(base.Measurement):
    def __init__(self, sample_obj,
                 mtype, mfile, machine,
                 **options):

        super(generic_moment, self).__init__(sample_obj,
                                             mtype, mfile, machine,
                                             **options)

    def format_cryomag(self):
        data = self.machine_data.float_data
        header = self.machine_data.float_header
        self._data = RockPyData(column_names=header, data=data)
        self._data.define_alias('m', ( 'x', 'y', 'z'))
        self._data = self._data.append_columns('mag', self._data.magnitude('m'))

    def format_sushibar(self):
        self._data = RockPyData(column_names=['field', 'x', 'y', 'z'],
                               data=self.machine_data.out_trm())  # , units=['mT', 'Am^2', 'Am^2', 'Am^2'])
        self._data.define_alias('m', ( 'x', 'y', 'z'))
        self._data = self._data.append_columns('mag', self._data.magnitude('m'))

    def format_jr6(self):
        data =  self.machine_data.get_data()
        self._data = RockPyData(column_names=['x', 'y', 'z'],
                                data=data,
                                units=['A m^2', 'A m^2', 'A m^2'])
        self._data.define_alias('m', ( 'x', 'y', 'z'))
        self._data = self._data.append_columns('mag', self._data.magnitude('m'))

class Irm(generic_moment):
    def __init__(self, sample_obj,
                 mtype, mfile, machine,
                 **options):

        super(Irm, self).__init__(sample_obj,
                                  mtype, mfile, machine,
                                  **options)