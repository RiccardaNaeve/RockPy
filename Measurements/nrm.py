import base
from RockPy.Structure.data import RockPyData


class Nrm(base.Measurement):
    def format_cryomag(self):
        data = self.machine_data.out_trm()
        header = self.machine_data.float_header
        self.data = RockPyData(column_names=header, values=data)
        __author__ = 'mike'
