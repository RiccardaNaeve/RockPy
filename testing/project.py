__author__ = 'volk'

import Structure.sample


def test():
    mfile1 = '../testing/test_data/MUCVSM_test.hys'
    mfile2 = '../testing/test_data/MUCVFTB_test2.coe'

    S = Structure.sample.Sample(name='test_sample',
                                 mass=14.2, mass_unit='mg',
                                 diameter=5.4, length_unit='nm',
                                 height=23.8,
    )

    S.add_measurement(mtype='hysteresis', mfile=mfile1, machine='vsm')
    S.add_measurement(mtype='backfield', mfile=mfile2, machine='vftb')

    # S.results() #todo print all results for a sample

if __name__ == '__main__':
    test()