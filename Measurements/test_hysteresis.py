__author__ = 'mike'
from unittest import TestCase
import matplotlib.pyplot as plt
import numpy as np
from copy import deepcopy
import RockPy
from os.path import join


class TestHysteresis(TestCase):
    def setUp(self):
        vsm_file = '../Tutorials/test_data/MUCVSM_test.hys'
        # vsm_file = join(RockPy.test_data_path, 'vsm', 'LTPY_527,1a_HYS_VSM#XX[mg]___#TEMP_300_K#STD000.000')
        self.sample = RockPy.Sample('test')
        self.VSM_test = RockPy.Sample('test')
        self.VSM_hys = self.VSM_test.add_measurement(mtype='hysteresis', mfile=vsm_file, machine='vsm')
        self.simulation = self.sample.add_simulation(mtype='hysteresis', mrs_ms=0.5, ms=5., b_sat=0.8, hf_sus=1)

    def test_simulate(self):
        hys = self.sample.add_simulation(mtype='hysteresis', mrs_ms=0.2, ms=5., b_sat=0.5, hf_sus=0.)
        self.assertAlmostEqual(5, max(hys.data['down_field']['mag'].v), delta=5. * 0.001)

    def test_calculate_ms(self):
        self.simulation.calculate_ms()
        res = self.simulation.results['ms'].v[0]
        self.assertAlmostEquals(res, 5., delta=5. * 0.01)


    def test_calculate_ms_simple(self):
        self.simulation.calculate_ms_simple()
        res = self.simulation.results['ms'].v[0]
        self.assertAlmostEquals(res, 5., delta=5. * 0.01)

    def test_calculate_mrs(self):
        self.simulation.calculate_mrs()
        res = self.simulation.results['mrs'].v[0]
        self.assertAlmostEquals(res, 2.5, delta=2.5 * 0.01)

    def test_calculate_bc(self):
        self.simulation.calculate_bc()
        res = self.simulation.results['bc'].v[0]
        self.simulation.plt_hys()
        self.assertAlmostEquals(res, 0.20, delta=0.20 * 0.01)
