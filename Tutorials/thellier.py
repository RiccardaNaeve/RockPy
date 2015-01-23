__author__ = 'volk'
from os.path import join
import RockPy
# thellier output file from cryomag

def test():
    cryomag_file = join(RockPy.test_data_path, 'NLCRY_Thellier_test.TT')

    # creating a sample
    sample = RockPy.Sample(name='1a')

    # adding the measurement to the sample
    M = sample.add_measurement(mtype='thellier', mfile=cryomag_file, machine='cryomag',
                               treatments='Pressure_0.0_GPa')

    print M.th
if __name__ == '__main__':
    test()