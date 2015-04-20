__author__ = 'mike'
import numpy as np

from RockPy.Structure.data import RockPyData
import base
import vsm
from time import clock
from pprint import pprint
from collections import defaultdict
from profilehooks import profile
from functools import partial
from multiprocessing import Pool


class VsmNew(base.Machine):
    # @profile()
    def __init__(self, dfile, sample=None):
        super(VsmNew, self).__init__(dfile=dfile, sample_name=sample)

        with open(dfile) as f:
            self.raw_data = map(str.rstrip, f.readlines())

        # self.data_idx = min(i for i, v in enumerate(self.raw_data) if v.startswith('+') or v.startswith('-'))
        self.data_idx = self.get_data_idx()

        self.fformat_header = self.get_file_header()
        self.segment_header = self.get_segment_header()

        self.data = self.get_data()

    def get_data_idx(self):
        for i,v in enumerate(self.raw_data):
            if v.startswith('+') or v.startswith('-'):
                return i

    def get_file_header(self):
        out = {}
        linecount = 0
        header_lines = [i.split('  ') for i in self.raw_data[3:self.data_idx]]
        header_lines = (filter(None, i) for i in header_lines)

        key = 'machine'
        for idx, line in enumerate(header_lines):
            if len(line) == 1:
                if len(line[0].split(',')) == 1:
                    key = line[0]
            out.setdefault(key, dict())
            if len(line) == 2 and not all(i.strip() == 'Adjusted' for i in line):
                out[key].setdefault(line[0], line[1])
                linecount = idx + 4
        self.segment_index = linecount
        return out

    def get_segment_header(self):
        if 'NForc' in self.fformat_header['SCRIPT']:
            return

        # get number of segments
        segments = int(self.fformat_header['SCRIPT']['Number of segments'])
        # get end index, the last '\r\n' entry
        segment_end_idx = max(i for i, v in enumerate(self.raw_data[self.segment_index:self.data_idx]) if not v)
        segment_info = [i.rstrip() for i in
                        self.raw_data[self.segment_index + 1:self.segment_index + segment_end_idx - segments]]
        # get length of each entry from data lengths
        segment_length = [len(i)+1 for i in self.raw_data[self.segment_index + segment_end_idx - segments].split(',')]

        #cut entries to represent length
        for i, v in enumerate(segment_info):
            idx = 0
            aux = []
            for j, length in enumerate(segment_length):
                aux.append(v[idx:idx + segment_length[j]].strip())
                idx += segment_length[j]
            segment_info[i] = aux

        # filter empty lists and create generator
        # join segment names ( segment\nnumber -> segment_number
        segment_info = [' '.join(filter(len,i)) for i in zip(*segment_info)]

        segments = [map(float, i.rstrip().split(',')) for i in
                    self.raw_data[self.segment_index + segment_end_idx - segments:self.segment_index + segment_end_idx]]

        # initialize dictionary
        out = {v: [j[i] for j in segments] for i, v in enumerate(segment_info)}
        return out

    def get_data(self):
        data = self.raw_data[self.data_idx:-2]
        # different readin procedure for Forc Data, because no segment information
        if 'NForc' in self.fformat_header['SCRIPT']:
            indices = [-1] + [i for i,v in enumerate(data) if not v]+[len(data)]
            # out = [map(self.split_comma_float, [line for line in data[indices[i]+1:indices[i+1]]]) for i in xrange(len(indices)-1)]
            out = [np.asarray([line.split(',') for line in data[indices[i]+1:indices[i+1]]], dtype=float) for i in xrange(len(indices)-1)]
        else:
            indices = [0] + map(int, self.segment_header['Final Index'])
            data = filter(len, data) # remove empty lines
            out = [np.asarray([line.split(',') for line in data[indices[i]:indices[i+1]]], dtype=float) for i in xrange(len(indices)-1)]
        return out


if __name__ == '__main__':
    # dfile = '/Users/mike/Dropbox/experimental_data/FeNiX/FeNi20G/FeNi20_FeNi20-Ga36-G01_HYS_VSM#7,9[mg]_[]_[]###.001'
    dfile = '/Users/mike/Dropbox/experimental_data/FeNiX/FeNi20H/FeNi_FeNi20-Ha36e02-G01_FORC_VSM#[]_[]_[]#-.002'
    # #
    # start = clock()
    # old = vsm.Vsm(dfile=dfile)
    # old.forc()
    # print 'old readin', clock() - start

    start = clock()
    new = VsmNew(dfile=dfile)
    print new.data[5]
    print 'new', clock() - start