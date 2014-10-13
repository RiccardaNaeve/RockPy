import base
from Structure.rockpydata import RockPyData


class Nrm(base.Measurement):
    def format_cryomag(self):
        data = self.machine_data.out_trm()
        header = self.machine_data.float_header
        self.data = RockPyData(column_names=header, data=data)
        __author__ = 'mike'
