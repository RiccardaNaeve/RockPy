__author__ = 'volk'
from Structure.project import Sample
import matplotlib.pyplot as plt

vftb_file = 'test_data/MUCVFTB_test.coe'

sample = Sample(name='vftb_test_sample')

M = sample.add_measurement(mtype='backfield', mfile=vftb_file, machine='vftb')
M.plt_backfield()