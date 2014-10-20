__author__ = 'mike'
import numpy as np

import base


class Jr6(base.Machine):
    def __init__(self, dfile, sample_name):

        super(Jr6, self).__init__(dfile=dfile, sample_name=sample_name)
        names = np.genfromtxt(dfile, usecols=(0), dtype=str)
        self.sample_index = np.where(names == self.sample_name)[0]
        self.type = np.genfromtxt(dfile, usecols=(1), dtype=str)
        self.xyz = np.genfromtxt(dfile, usecols=(2, 3, 4))
        self.exponent = np.genfromtxt(dfile, usecols=(5))


    def get_header(self):
        return ['x', 'y', 'z']

    def get_exponent(self):
        return self.exponent[self.sample_index]

    def get_data(self):
        data = self.xyz[self.sample_index]
        exponent = self.get_exponent()
        out = np.power(np.ones(len(exponent)) * 10, exponent) * data
        out *= 1e-5
        return out

    def get_type(self):
        return self.type[self.sample_index]

    def _check_data_exists(self):
        if self.sample_index:
            return True
        else:
            return False
