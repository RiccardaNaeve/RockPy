__author__ = 'volk'

import Structure.project

S = Structure.project.Sample(name='test_sample', mass=22.4, mass_unit='mg')

print S.mass_kg