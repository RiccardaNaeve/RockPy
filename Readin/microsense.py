__author__ = 'mike'
import base
from Structure.rockpydata import RockPyData
import numpy as np


class MicroSense(base.Machine):
    def __init__(self, dfile, sample_obj):
        super(MicroSense, self).__init__(dfile, sample_obj)

        self.raw_data = [i for i in self.reader_object]

        self.data_start_idx = [i + 2 for i in range(len(self.raw_data)) if self.raw_data[i].startswith('@@Final')][0]
        self.data_end_idx = [i - 2 for i in range(len(self.raw_data)) if self.raw_data[i].startswith('@@END Data')][-1]
        self.header_idx = [i + 1 for i in range(len(self.raw_data)) if self.raw_data[i].startswith('@@End of Header')][
            0]
        d = np.array([i.split() for i in self.raw_data[self.data_start_idx:self.data_end_idx]])
        # print self.data_start_idx, self.data_end_idx
        self.data = d.astype(float)
        # self.data = rockpydata(column_names=self.header, data=d)

    @property
    def header(self):
        return self.raw_data[self.header_idx].lower().split()

    def out_hys(self):
        return self.data
