__author__ = 'volk'
from Structure.project import Sample

def test():
    vftb_file = 'test_data/MUCVFTB_test.hys'
    vsm_file = 'test_data/MUCVSM_test.hys'

    sample = Sample(name='vftb_test_sample')
    sample2 = Sample(name='vsm_test_sample')

    M = sample.add_measurement(mtype='hysteresis', mfile=vftb_file, machine='vftb')
    M.calc_all()
    print M.results

if __name__ is '__main__':
    test()