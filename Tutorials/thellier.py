__author__ = 'volk'
import os
from os.path import join
import RockPy
from copy import deepcopy
from pprint import pprint
import time
import RockPy.Visualize.paleointensity

def get_test_sample(recalc=False):

    if os.path.isfile(join(RockPy.test_data_path, 'TTtest.rpy')) or recalc:
        cryomag_file1 = join(RockPy.test_data_path, 'LF4C-HX_1a_TT_CRY#320[mg]_5.17[mm]_5.84[mm]#pressure_0.0_GPa#.000')
        cryomag_file2 = join(RockPy.test_data_path, 'LF4C-HX_1a_TT_CRY#320[mg]_5.17[mm]_5.84[mm]#pressure_0.6_GPa#.000')
        cryomag_file3 = join(RockPy.test_data_path, 'LF4C-HX_1a_TT_CRY#320[mg]_5.17[mm]_5.84[mm]#pressure_1.2_GPa#.000')

        # creating a sample
        sample = RockPy.Sample(name='1a')

        # adding the measurement to the sample
        M = sample.add_measurement(mtype='thellier', mfile=cryomag_file1, machine='cryomag',
                                   treatments='Pressure_0.0_GPa')
        M = sample.add_measurement(mtype='thellier', mfile=cryomag_file2, machine='cryomag',
                                   treatments='Pressure_1.0_GPa')
        M = sample.add_measurement(mtype='thellier', mfile=cryomag_file3, machine='cryomag',
                                   treatments='Pressure_0.0_GPa')

        RockPy.save(sample, 'TTtest.rpy', RockPy.test_data_path)
    else:
        sample = RockPy.load('TTtest.rpy', RockPy.test_data_path)

    return sample

if __name__ == '__main__':

    study = RockPy.Study(name='study')
    sg = RockPy.SampleGroup(name='sg')
    s = get_test_sample()
    s.filter(ttype='pressure', tval=1.0)
    print s.filtered_data
    print s.measurements
    P= RockPy.Visualize.paleointensity.Arai(sg)
    # print P.plotted_primary
    # print P.plotted_secondary
    P.show()