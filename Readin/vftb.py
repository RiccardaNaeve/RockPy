__author__ = 'mike'
import numpy as np

import base


class Vftb(base.Machine):
    def __init__(self, dfile, sample_name):
        super(Vftb, self).__init__(dfile, sample_name)
        self.raw_data = [i.strip('\r\n').split('\t') for i in open(self.file_name).readlines() if not '#' in i]
        self.mass = float(self.raw_data[0][1].split()[1])
        # finding set indices
        idx = [j for j, v2 in enumerate(self.raw_data) for i, v in enumerate(v2) if v.startswith('Set')]
        # appending length of measurement (-1 because of empty last line
        idx.append(len(self.raw_data))
        self.set_idx = [(idx[i], idx[i + 1]) for i in range(len(idx) - 1)]
        self.units = self.get_units()
        self.header = self.get_header()
        self.data = self.get_data()

    def get_header(self):
        header = self.raw_data[self.set_idx[0][0] + 1]
        header = ['_'.join(i.split(' / ')[0].split()) for i in header]  # only getting the column name without the unit
        return header

    def get_units(self):
        units = self.raw_data[self.set_idx[0][0] + 1]
        units = ['/'.join(i.split(' / ')[1:]) for i in units]  # only getting the column name without the unit
        return units

    def get_data(self):
        data = np.array([np.array(self.raw_data[i[0] + 2:i[1] - 1]) for i in self.set_idx])
        data = [self.replace_na(i) for i in data]
        data = np.array([i.astype(float) for i in data])
        data = self.convert_to_T(data)
        return data

    def out_hysteresis(self):
        data = self.get_data()
        return data

    def out_backfield(self):
        data = self.get_data()
        return data

    def out_irm_acquisition(self):
        data = self.get_data()
        return data

    def out_thermocurve(self):
        data = self.get_data()
        return data

    def replace_na(self, data):
        out = [['0.' if j == 'n/a' else j for j in i] for i in data]
        out = np.array(out)
        return out

    def convert_to_T(self, data):
        for i in data:
            i[:, 0] /= 10000
        self.units[0] = 'T'
        return data

    def _check_data_exists(self):
        if self.data is not None:
            return True
        else:
            return False