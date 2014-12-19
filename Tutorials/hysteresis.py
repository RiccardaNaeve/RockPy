__author__ = 'volk'
from RockPy.Structure.sample import Sample

def test():
    vftb_file = 'test_data/MUCVFTB_test.hys'
    vsm_file = 'test_data/MUCVSM_test.hys'

    sample = Sample(name='vftb_test_sample')
    sample2 = Sample(name='vsm_test_sample')

    M = sample.add_measurement(mtype='hysteresis', mfile=vftb_file, machine='vftb')
    # print M.result_ms()
    # M.plt_hys()

    M = sample.add_measurement(mtype='hysteresis', mfile=vsm_file, machine='vsm')
    print M.result_ms(from_field=80)
    # M.calc_all()
    # print M.results
    M.plt_hys()

if __name__ == '__main__':
    test()