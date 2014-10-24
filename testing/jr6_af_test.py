__author__ = 'mike'
from Structure.project import Sample

data = 'test_data/High_T_AF-demag_neu.jr6'

S = Sample(name='VB')

M = S.add_measurement(mtype='afdemag', machine='jr6', mfile=data)
# M.plt_afdemag(norm=True)
M.calc_all()
print M.results