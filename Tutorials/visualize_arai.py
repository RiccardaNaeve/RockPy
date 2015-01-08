__author__ = 'volk'
import RockPy
from Visualize.paleointensity import Arai


def test():
    # thellier output file from cryomag
    cryomag_file = 'test_data/NLCRY_Thellier_test.TT'

    # creating a sample
    sample = RockPy.Sample(name='1a', mass='1.0', mass_unit='mg')

    # adding the measurement to the sample
    M = sample.add_measurement(mtype='thellier', mfile=cryomag_file, machine='cryomag')

    S = Arai(sample)
    print S
    S.show()

if __name__ == '__main__':
    test()
