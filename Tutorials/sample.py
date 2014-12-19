__author__ = 'volk'

import Structure.sample

def make_sample():
    S = Structure.sample.Sample(name='test_sample',
                                 mass=14.2, mass_unit='mg',
                                 diameter=5.4, length_unit='nm',
                                 height=23.8)
    return S

def add_measurements(S):
    mfile1 = '../Tutorials/test_data/MUCVSM_test.hys'
    mfile2 = '../Tutorials/test_data/MUCVFTB_test2.coe'
    S.add_measurement(mtype='hysteresis', mfile=mfile1, machine='vsm')
    S.add_measurement(mtype='backfield', mfile=mfile2, machine='vftb')



def test():
    S = make_sample()
    add_measurements(S)

if __name__ == '__main__':
    test()