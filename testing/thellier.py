__author__ = 'volk'
from Structure.project import Sample
import matplotlib.pyplot as plt
import numpy as np
# thellier output file from cryomag
cryomag_file = 'test_data/NLCRY_Thellier_test.TT'

# creating a sample
sample = Sample(name='1a')

# adding the measurement to the sample
M = sample.add_measurement(mtype='thellier', mfile=cryomag_file, machine='cryomag')

# print np.c_[M.th['temp'], M.th['mag']]
# print np.c_[M.ptrm['temp'], M.ptrm['mag']]
# print np.c_[M.sum['temp'], M.sum['mag']]
print M.result_slope(t_min=20)
# calculation of slope
# print 'just returning the standard values'
# print M.result_slope()
# print 'recalculating with different parameters'
# print M.result_slope(t_min=300)
# print 'calculating slope 1: t_min=400'
# M.calculate_slope(t_min=400, component='z')  #calculation with non standard parameters
# print 'returning calculation'
# print M.result_slope(), M.result_sigma()

# getting results -> simple calculation with standard parameters
# print M.slope, M.sigma, M.y_intercept, M.x_intercept

# print M.result_b_anc(t_min=300)
# print M.result_sigma_b_anc(t_min=300)

# print M.result_vds(t_min=100)
# M.calculate_x_dash()
# plotting dunlop plot
# M.plt_dunlop()

# plotting arai diagram
# M.plt_arai()