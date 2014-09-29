__author__ = 'volk'
from Structure.project import Sample
import matplotlib.pyplot as plt

cryomag_file = 'test_data/NLCRY_Thellier_test.TT'

sample = Sample(name='1a')

M = sample.add_measurement(mtype='thellier', mfile=cryomag_file, machine='cryomag')
M.plt_dunlop()