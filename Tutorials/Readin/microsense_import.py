__author__ = 'volk'
from Structure.sample import Sample
import matplotlib.pyplot as plt
import numpy as np

dfile = 'test_data/MICROSENSE_HYS-test.VHD'

sample = Sample(name='microsense_test')

M = sample.add_measurement(mtype='hys', mfile=dfile, machine='microsense')

M.plt_hys()