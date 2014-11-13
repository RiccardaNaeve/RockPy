__author__ = 'mike'
import nrm
from RockPy.Structure.data import RockPyData


class Trm(nrm.Nrm):
    def format_cryomag(self):
        data = self.machine_data.out_trm()
        header = self.machine_data.float_header
        self.data = RockPyData(column_names=header, data=data)
        self.data.rename_column('step', 'temp')
