from unittest import TestCase

__author__ = 'mike'
from Structure.sample import Sample
import numpy as np


class TestAfDemag(TestCase):
    def setUp(self):
        # sample data files
        self.jr6_file = '../Tutorials/test_data/MUCSPN_afdemag.jr6'
        self.cryomag_file = '../Tutorials/test_data/NLCRYO_test.af'
        self.sushibar_file = '../Tutorials/test_data/MUCSUSH_af_test.af'

        # creating samples
        self.jr6_sample = Sample(name='VA')
        self.sushibar_sample = Sample(name='WURM')
        self.cryomag_sample = Sample(name='DA6B')

        # adding measurements
        self.jr6_af = self.jr6_sample.add_measurement(mtype='afdemag', mfile=self.jr6_file, machine='jr6')
        self.cryomag_af = self.cryomag_sample.add_measurement(mtype='afdemag', mfile=self.cryomag_file,
                                                              machine='cryomag',
                                                              demag_type='x')
        self.sushibar_af = self.sushibar_sample.add_measurement(mtype='afdemag', mfile=self.sushibar_file,
                                                                machine='sushibar')

    def test_calculate_mdf(self):
        self.cryomag_af.calculate_mdf()
        self.assertAlmostEqual(self.cryomag_af.result_mdf().v, 24.40, places=1)


    def test_format_jr6(self):
        m = self.jr6_sample.add_measurement(mtype='afdemag', mfile=self.jr6_file, machine='jr6')  #
        self.assertEqual(m.data['data']['field'].v[0], 0)

    def test_format_sushibar(self):
        m = self.sushibar_sample.add_measurement(mtype='afdemag', mfile=self.sushibar_file, machine='sushibar')  #
        self.assertEqual(m.data['data']['field'].v[0], 0)

    def test_format_cryomag(self):
        m = self.cryomag_sample.add_measurement(mtype='afdemag', mfile=self.cryomag_file, machine='cryomag')  #
        self.assertEqual(m.data['data']['field'].v[0], 0)

    def test_result_mdf(self):
        self.assertAlmostEqual(self.cryomag_af.result_mdf().v, 24.40, places=1)
    #
    # def test_interpolate_smoothing_spline(self):
    #     self.fail()
    #
    # def test_interpolation_spline(self):
    #     self.fail()
    #
    # def test_plt_afdemag(self):
    #     self.fail()