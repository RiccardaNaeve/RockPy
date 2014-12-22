from unittest import TestCase
import RockPy as rp

__author__ = 'mike'


class TestMeasurement(TestCase):
    def setUp(self):
        self.test_sample = rp.Sample(name='test_sample')
        self.generic_M = self.test_sample.add_measurement(mtype='mass', mfile=None,
                                                          treatments='pressure, 0.0, GPa; temperature, 300.0, C')

    def test__get_treatment_from_suffix(self):
        list = [['pressure', 0.0, 'GPa'], ['temperature', 300.0, 'C']]
        self.assertEqual(self.generic_M._get_treatments_from_opt(), list)


    def test__add_treatment_from_opt(self):
        print self.generic_M.treatments