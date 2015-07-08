__author__ = 'volk'
import RockPy

from RockPy.Structure.sample import Sample
from os.path import join

def test():
    vftb_file = join(RockPy.test_data_path, 'MUCVFTB_test.hys')
    # vsm_file = join(RockPy.test_data_path, 'vsm', 'MUCVSM_test.hys')
    vsm_file = join(RockPy.test_data_path, 'vsm', 'LTPY_527,1a_HYS_VSM#XX[mg]___#TEMP_300_K#STD000.000')
    # sample = Sample(name='vftb_test_sample')
    sample2 = Sample(name='vsm_test_sample')

    # M = sample.add_measurement(mtype='hysteresis', mfile=vftb_file, machine='vftb')
    # print M.result_ms()
    # M.plt_hys()

    M = sample2.add_measurement(mtype='hysteresis', mfile=vsm_file, machine='vsm')

    M.calc_all()

    print M.results
    M.plt_hys()
if __name__ == '__main__':
    test()