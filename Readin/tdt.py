__author__ = 'mike'
import base
import numpy as np
import os.path
import RockPy
from RockPy.Functions.general import DIL2XYZ


class Tdt(base.Machine):
    @staticmethod
    def recalc_line(line):
        """
        Takes a line and splits off the name, truncates the dtype information from the temperature and converts the DIL
        data to XYZ

        Parameters
        ----------
           line: list
              line to be converted to float, xyz
        """
        t = float(line[1].split('.')[0])
        L, D, I = map(float, line[2:])
        x, y, z = DIL2XYZ((D, I, L*1E-3)) # convert mA/m to A/m
        return t, x, y, z, L

    def __init__(self, dfile, sample_name=None):
        super(Tdt, self).__init__(dfile=dfile, sample_name=sample_name)

        self.raw_data = self.simple_import()[1:]
        # setting data
        self.data = self.get_data()
        self.header = ['temp', 'x', 'y', 'z', 'mag']
        self.units = ['C', 'A / m', 'A / m', 'A / m', 'A / m']

    @property
    def header_data(self):
        """
        Looks in the file for a line that starts with a number -> there is a header, which then gets transformed to
        a dictionary with the relavent data
        :return:
        """
        for line in self.raw_data:
            if line[0].isdigit():
                l = line.split('\t')
                out = {'lab_field': float(l[0]),
                       'bearing': float(l[1]),
                       'plunge': float(l[2]),
                       'dip_direction': float(l[3]),
                       'dip': float(l[4]),
                       }
                return out
        else:
            return None

    def get_data(self):
        """
        formats the raw input from file into floats and xyz data
        :return:
        """
        look_up = {'00': 'TH', '0': 'TH',
                   '11': 'PT', '1': 'PT',
                   '12': 'CK', '2': 'CK',
                   '13': 'TR', '3': 'TR',
                   '14': 'AC', '4': 'AC'}
        out = dict()
        for line in self.raw_data:
            if line != 'Thellier-tdt':
                try:
                    int(line[0])
                except:
                    l = line.split('\t')
                    dtype = look_up[l[1].split('.')[1]]
                    out.setdefault(dtype, [])
                    out[dtype].append(self.recalc_line(l))
        return out


def test():
    test_file = os.path.join(RockPy.test_data_path, 'tdt', 'example2.tdt')

    test_tdt = Tdt(dfile=test_file, sample_name='MGH1')
    # sample = RockPy.Sample(name='test_sample')


if __name__ == '__main__':
    test()