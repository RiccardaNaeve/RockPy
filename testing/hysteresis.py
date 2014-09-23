__author__ = 'volk'
from Structure.project import Sample
import matplotlib.pyplot as plt

vftb_file = 'test_data/MUCVFTB_test.hys'

sample = Sample(name='vftb_test_sample')

M = sample.add_measurement(mtype='hys', mfile=vftb_file, machine='vftb')

data = M.down_field.interpolate()
plt.plot(data.variable, data.measurement)
# plt.plot(M.up_field.variable, M.up_field.measurement)
# plt.plot(M.down_field.variable, M.down_field.measurement)
plt.show()