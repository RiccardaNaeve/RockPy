__author__ = 'mike'
import base
import numpy as np


class CryoMag(base.Machine):
    def __init__(self, dfile, sample_name):
        super(CryoMag, self).__init__(dfile, sample_name)
        self.raw_data = [i.strip('\n\r').split('\t') for i in self.reader_object.readlines()]
        d = np.array(self.raw_data[2:])
        self.float_data_idx = [7, 1, 2, 3, 4, 5, 6, 12, 13, 14, 15, 16, 17, 18, 19, 20]
        self.sample_idx = [i for i, v in enumerate(d[:, 0]) if
                           v == sample_name or sample_name in d[i, 9]]
        self.results_idx = [i for i, v in enumerate(d[:, 11]) if v == 'results' and i in self.sample_idx]
        self.header = self.get_header()

    def get_header(self):
        header = [i.split('[Am^2]')[0] for i in self.raw_data[1]]
        header = map(str.strip, header)
        header = map(str.lower, header)
        header = np.array(header)
        return header

    @property
    def float_header(self):
        return self.header[self.float_data_idx]

    def get_float_data(self):
        data = np.array(self.raw_data[2:])[self.results_idx]
        data = data[:, self.float_data_idx]
        data = data.astype(float)
        return data

    def samples(self):
        samples = np.array(self.raw_data[2:])[:, 0]
        return samples

    def comments(self):
        comments = np.array(self.raw_data[2:])[:, 9]
        return comments

    def out_thellier(self):
        data = self.get_float_data()
        return data

    @property
    def steps(self):
        steps = np.array(self.raw_data[2:])[:, 8]
        steps = np.array(map(str.lower, steps))
        steps = steps[self.results_idx]
        return steps