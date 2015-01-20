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
        data = RockPyData(column_names=header, data=data)
        data.define_alias('m', ( 'x', 'y', 'z'))
        # data = data.append_columns('mag', data.magnitude('m'))
        self._data = {'data': data.append_columns('mag', data.magnitude('m'))}

    def format_sushibar(self):
        data = RockPyData(column_names=['temp', 'x', 'y', 'z', 'sm'],
                          data=self.machine_data.out_trm(),
                          units=['C', 'mT', 'A m^2', 'A m^2', 'A m^2'])
        data.define_alias('m', ( 'x', 'y', 'z'))
        # data = data.append_columns('mag', data.magnitude('m'))
        self._data = {'data': data.append_columns('mag', data.magnitude('m'))}

    def format_jr6(self):
        data =  self.machine_data.get_data()
        data = RockPyData(column_names=['x', 'y', 'z'],
                                data=data,
                                units=['A m^2', 'A m^2', 'A m^2'])
        data.define_alias('m', ( 'x', 'y', 'z'))
        self._data = {'data': data.append_columns('mag', data.magnitude('m'))}

class Irm(generic_moment):
    def __init__(self, sample_obj,
                 mtype, mfile, machine,
                 **options):

        super(Irm, self).__init__(sample_obj,
                                  mtype, mfile, machine,
                                  **options)

class Arm(generic_moment):
    pass