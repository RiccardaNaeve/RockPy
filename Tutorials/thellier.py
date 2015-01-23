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
        cryomag_file = join(RockPy.test_data_path, 'NLCRY_Thellier_test.TT')
        # creating a sample
        sample = RockPy.Sample(name='1a')

        # adding the measurement to the sample
        M = sample.add_measurement(mtype='thellier', mfile=cryomag_file, machine='cryomag',
                                   treatments='Pressure_0.0_GPa')
        M = sample.add_measurement(mtype='thellier', mfile=cryomag_file, machine='cryomag',
                                   treatments='Pressure_0.0_GPa')
        M.set_initial_state(mtype='trm', mfile=cryomag_file, machine='cryomag',
                                   treatments='Pressure_0.0_GPa')

        M = sample.add_measurement(mtype='thellier', mfile=cryomag_file, machine='cryomag',
                                   treatments='Pressure_1.0_GPa')
        M = sample.add_measurement(mtype='thellier', mfile=cryomag_file, machine='cryomag',
                                   treatments='Pressure_1.0_GPa')
        M.set_initial_state(mtype='trm', mfile=cryomag_file, machine='cryomag',
                                   treatments='Pressure_1.0_GPa')
        RockPy.save(sample, 'TTtest.rpy', RockPy.test_data_path)
    else:
        sample = RockPy.load('TTtest.rpy', RockPy.test_data_path)

    return sample

if __name__ == '__main__':

    study = RockPy.Study(name='study')
    sg = RockPy.SampleGroup(name='sg')
    s = get_test_sample()

    RockPy.Visualize.paleointensity.Arai(s).show()