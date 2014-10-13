__author__ = 'volk'
from Structure.project import Sample
# thellier output file from cryomag
cryomag_file = 'test_data/NLCRY_Thellier_test.TT'
cryomag_is_file = 'test_data/NLCRY_Thellier_is_test.TT'
# creating a sample
sample = Sample(name='1a')
M = sample.add_measurement(mtype='thellier', mfile=cryomag_file, machine='cryomag')
M.set_initial_state(mtype='trm', mfile=cryomag_is_file, machine='cryomag')
M.add_treatment(ttype='pressure', tvalue=0.0)
M.treatments[0].add_value('max_p', 0.6)
M.treatments[0].add_value('tonnage', 3)
M.treatments[0].add_value('release_time', 30.0)

# M.plt_arai(norm='is')

print M.th
print M.initial_state.data

print M.th / M.initial_state.data