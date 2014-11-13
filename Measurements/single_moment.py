__author__ = 'mike'

import base
from Structure.data import RockPyData


class generic_moment(base.Measurement):
    def __init__(self, sample_obj,
                 mtype, mfile, machine,
                 **options):

        super(generic_moment, self).__init__(sample_obj,
                                             mtype, mfile, machine,
                                             **options)

    def format_cryomag(self):
        data = self.machine_data.out_trm()
        header = self.machine_data.float_header
        self.data = RockPyData(column_names=header, data=data)
        self.data.define_alias('m', ( 'x', 'y', 'z'))
        self.data = self.data.append_columns('mag', self.data.magnitude('m'))

    def format_sushibar(self):
        self.data = RockPyData(column_names=['field', 'x', 'y', 'z'],
                               data=self.machine_data.out_trm())  # , units=['mT', 'Am^2', 'Am^2', 'Am^2'])
        self.data.define_alias('m', ( 'x', 'y', 'z'))
        self.data = self.data.append_columns('mag', self.data.magnitude('m'))



class Irm(generic_moment):
    def __init__(self, sample_obj,
                 mtype, mfile, machine,
                 **options):

        super(Irm, self).__init__(sample_obj,
                                  mtype, mfile, machine,
                                  **options)