__author__ = 'volk'
from Structure.project import Sample
import matplotlib.pyplot as plt

vftb_file = 'test_data/MUCVFTB_test.irm'

sample = Sample(name='vftb_test_sample')

M = sample.add_measurement(mtype='irm', mfile=vftb_file, machine='vftb')
M.plt_irm()