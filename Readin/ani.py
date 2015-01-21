__author__ = 'wack'


__author__ = 'wack'

import base
import numpy as np
from StringIO import StringIO

class ANI(base.Machine):
    """
    ani file format to describe anisotropy measurements
    format:
    first line: header / comment
    second line: reference/measurement directions in pairs of declination and inclinations (mdirs)
    i.e. D1,I1;D2,I2;D3,I3
    remaining lines 1 or 3 components of measurements
    i.e. V or x,y,z
    """

    def __init__(self, dfile, sample_name):
        super(ANI, self).__init__(dfile=dfile, sample_name=sample_name)

        # read the data file line by line
        f = open(self.file_name)
        self.raw_data = f.readlines()
        f.close()

        # store first header line
        self.header = self.raw_data[0]
        dipairs = self.raw_data.strip().split(';')
        self.mdirs = [[float(di[0]), float(di[1])] for di in dipairs.split(',')]
        # read the directional values from remaining lines
        self.data = np.genfromtxt(StringIO(self.raw_data[2:]), delimiter=",")

    def out_anisotropy(self):
        # return mdirs, directional data
        return self.mdirs, self.data

