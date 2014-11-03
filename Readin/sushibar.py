__author__ = 'mike'
import datetime

import numpy as np
import matplotlib.dates

import base


class SushiBar(base.Machine):
    def __init__(self, dfile, sample_name):
        print 'test'
        super(SushiBar, self).__init__(dfile, sample_name)
        self.float_data_idx = []
        self.header = {'sample': 0, 'site': 1, 'type': 2, 'run': 3, 'time': 4, 'x': 5, 'y': 6, 'z': 7,
                       'M': 8, 'Dc': 9, 'Ic': 10, 'Dg': 11, 'Ig': 12, 'Ds': 13, 'Is': 14, 'a95': 15,
                       'sM': 16, 'npos': 17, 'Dspin': 18, 'Ispin': 19, 'holder/sample': 20, 'cup/sample': 21,
                       'bl diff/sample': 22, 'steps/rev': 23, 'par1': 24, 'par2': 25, 'par3': 26, 'par4': 27,
                       'par5': 28, 'par6': 29, 'strat_level': 30, 'geoaz': 31, 'hade': 32, 'dipdir': 33,
                       'dip': 34, 'HeaderSkip': 1, 'modes': [], 'mode': 1, 'step': 25, 'type': 24}

        print [i for i in self.reader_object]

    def get_header(self):
        pass

    def out_afdemag(self):
        pass

    def _check_data_exists(self):
        return True

    def old(self):

        floats = ['dspin', 'ispin', 'par1', 'dip', 'dipdir', 'geoaz', 'm', 'strat_level', 'a95', 'par5', 'par4', 'par3',
                  'par2', 'sm', 'par6', 'dg', 'is', 'hade', 'dc', 'npos', 'bl diff/sample', 'y', 'x', 'ic', 'z', 'ds',
                  'ig']

        data_f = open(file)
        data = [i.strip('\n\r').split('\t') for i in data_f.readlines()]

        header = ['sample', 'site', 'type', 'run', 'time', 'x', 'y', 'z', 'M', 'Dc', 'Ic', 'Dg', 'Ig', 'Ds', 'Is',
                  'a95', 'sM', 'npos', 'Dspin', 'Ispin', ' holder/sample', 'cup/sample', 'bl diff/sample', 'steps/rev',
                  'par1', 'par2', 'par3', 'par4', 'par5', 'par6', 'strat_level', 'geoaz', 'hade', 'dipdir', 'dip']

        sample_data = np.array([i for i in data[2:] if i[0] == sample or sample in i[9]])

        if len(sample_data) == 0:
            log.error('UNKNOWN\t sample << %s >> can not be found in measurement file' % sample)
            return None

        out = {header[i].lower(): sample_data[:, i] for i in range(len(header))}

        for i in floats:
            try:
                out[i] = np.array(map(float, out[i]))
            except ValueError:
                for j in range(len(out[i])):
                    if out[i][j] == 'None':
                        out[i][j] = '0'
                    if out[i][j] == '-':
                        out[i][j] = np.nan
                try:
                    out[i] = np.array(map(float, out[i]))
                except ValueError:
                    continue

        out['run'] = map(int, out['run'])

        def time_conv(t):
            if t == '-':
                return None

            return time.strptime(t[:19], "%Y-%m-%d %H:%M:%S")

        out['time'] = map(time_conv, out['time'])
        log.info(
            'RETURNING\t %i data types with %i data points for sample: << %s >>' % (
            len(out), len(out['sample']), sample))
        return out


def test():
    from Structure.project import Sample

    test_file = '../testing/test_data/MUCSUSH_afdemag_trm.af'
    S = Sample(name='3e')
    S.add_measurement(mtype='afdemag', mfile=test_file, machine='sushibar')


if __name__ == '__main__':
    test()