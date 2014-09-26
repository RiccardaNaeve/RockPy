__author__ = 'volk'
from Structure.project import Sample
import matplotlib.pyplot as plt

# define measurement data file
vftb_file = 'test_data/MUCVFTB_test.coe'

# create a sample
sample = Sample(name='vftb_test_sample')

# add measurement
M = sample.add_measurement(mtype='backfield', mfile=vftb_file, machine='vftb')
M.plt_backfield()