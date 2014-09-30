__author__ = 'volk'
from Structure.project import Sample
import matplotlib.pyplot as plt

vftb_file = 'test_data/MUCVFTB_test.hys'
vsm_file = 'test_data/MUCVSM_test.hys'

sample = Sample(name='vftb_test_sample')
sample2 = Sample(name='vsm_test_sample')

M = sample.add_measurement(mtype='hys', mfile=vftb_file, machine='vftb')
M.plt_hysteresis()
print M.bc_diff
# M2 = sample2.add_measurement(mtype='hys', mfile=vsm_file, machine='vsm')
