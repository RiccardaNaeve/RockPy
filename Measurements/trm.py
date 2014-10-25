__author__ = 'mike'
import base
from Structure.data import RockPyData


class Trm(base.Measurement):
    def format_cryomag(self):
        data = self.machine_data.out_trm()
        header = self.machine_data.float_header
        self.data = RockPyData(column_names=header, values=data)
        self.data.rename_column('step', 'temp')
