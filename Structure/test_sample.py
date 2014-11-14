from unittest import TestCase
import RockPy as rp

__author__ = 'mike'


class TestSample(TestCase):
    def setUp(self):
        self.sample = rp.Sample(name='test_sample',
                                mass=34.5, mass_unit='mg',
                                diameter=5.4, height=4.3, length_unit='mm',
                                treatment='pressure, 0.0, GPa; temperature, 300.0, C')

    def test_mass_kg(self):
        self.assertEqual(self.sample.mass_kg.v, 3.45e-5)

    def test_height_m(self):
        self.assertEqual(self.sample.height_m.v, 0.0043)

    def test_diameter_m(self):
        self.assertEqual(self.sample.diameter_m.v, 0.0054)
