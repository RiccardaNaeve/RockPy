__author__ = 'mike'
from unittest import TestCase
import RockPy as rp


class TestHysteresis(TestCase):
    def setUp(self):
        vsm_file = '../testing/test_data/MUCVSM_test.hys'
        self.VSM_test = rp.Sample('test')
        self.VSM_hys = self.VSM_test.add_measurement(mtype='hysteresis', mfile=vsm_file, machine='vsm')


    def test_calculate_ms(self):
        print self.VSM_hys.calculate_ms()


    def test_calculate_mrs(self):
        self.VSM_hys.calculate_mrs()
        print self.VSM_hys.results['mrs']