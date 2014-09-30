__author__ = 'volk'
from Structure.project import Sample
import matplotlib.pyplot as plt
import numpy as np
dfile = 'test_data/MICROSENSE_HYS-test.VHD'

sample = Sample(name='microsense_test')

M = sample.add_measurement(mtype='hys', mfile=dfile, machine='microsense')

field = (M.down_field['field'][2:] - M.up_field['field'][:-4]) /2
diff = (M.down_field['moment'][2:] - M.up_field['moment'][:-4])
rev = (M.down_field['moment'][2:] + M.up_field['moment'][:-4]) /2

# plt.plot(field, diff/max(diff))
# plt.plot(field, rev/max(rev))
# plt.show()
# print M.up_field['field']
M.plt_hys()