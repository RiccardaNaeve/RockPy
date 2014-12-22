__author__ = 'volk'
from Structure.sample import Sample
from VisualizeOLD.arai import Arai


def test():
    # thellier output file from cryomag
    cryomag_file = 'test_data/NLCRY_Thellier_test.TT'

    # creating a sample
    sample = Sample(name='1a', mass='1.0', mass_unit='mg')
    sample2 = Sample(name='1b')

    # adding the measurement to the sample
    M = sample.add_measurement(mtype='thellier', mfile=cryomag_file, machine='cryomag')
    M.delete_temp(450)
    M = sample2.add_measurement(mtype='thellier', mfile=cryomag_file, machine='cryomag')
    M.delete_temp(450)

    S = Arai([sample, sample2], style='publication')


if __name__ == '__main__':
    test()
