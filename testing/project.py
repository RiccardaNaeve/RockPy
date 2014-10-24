__author__ = 'volk'

import Structure.project

def test():
    S = Structure.project.Sample(name='test_sample',
                                 mass=14.2, mass_unit='mg',
                                 diameter=5.4, length_unit='nm',
                                 height=23.8,
    )

if __name__ is '__main__':
    test()