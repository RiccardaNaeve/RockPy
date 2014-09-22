__author__ = 'volk'

import Structure.project

S = Structure.project.Sample(name='test_sample', mass=14.2, mass_unit='mg',
                             diameter=5.4, length_unit='nm', height=23)

print S.mass_kg
print S.diameter_m
print S.height_m