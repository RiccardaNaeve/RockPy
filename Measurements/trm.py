__author__ = 'mike'
import base
from RockPy.Structure.data import RockPyData


class Trm(base.Measurement):
    def format_cryomag(self):
        data = self.machine_data.out_trm()
        header = self.machine_data.float_header
        self.data = RockPyData(column_names=header, data=data)
        self.data.rename_column('step', 'temp')
    def format_sushibar(self):
        self.data = RockPyData(column_names=['field', 'x', 'y', 'z'],
                               data=self.machine_data.out_afdemag())  # , units=['mT', 'Am^2', 'Am^2', 'Am^2'])
        self.data.define_alias('m', ( 'x', 'y', 'z'))
        self.data.append_columns('mag', self.data.magnitude('m'))