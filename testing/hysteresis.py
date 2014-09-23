__author__ = 'volk'
from Structure.project import Sample
import matplotlib.pyplot as plt

vftb_file = 'test_data/MUCVFTB_test.hys'

sample = Sample(name='vftb_test_sample')

M = sample.add_measurement(mtype='hys', mfile=vftb_file, machine='vftb')
M.plt_hys()