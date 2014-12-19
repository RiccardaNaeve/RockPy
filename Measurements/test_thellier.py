from unittest import TestCase
import numpy as np
from Structure.sample import Sample
__author__ = 'mike'


class TestThellier(TestCase):
    def setUp(self):
        cryomag_file = '../Tutorials/test_data/NLCRY_Thellier_test.TT'
        self.test_sample_cryomag = Sample(name='1a')
        self.thellier_cryomag = self.test_sample_cryomag.add_measurement(mtype='thellier', mfile=cryomag_file, machine='cryomag')
    #
    # def test_format_cryomag(self):
    #     self.fail()
    #
    # def test_format_sushibar(self):
    #     self.fail()
    #
    # def test_remove_duplicate_measurements(self):
    #     self.fail()
    #
    # def test_delete_temp(self):
    #     self.fail()
    #
    # def test_result_slope(self):
    #     self.fail()
    #
    # def test_result_n(self):
    #     self.fail()
    #
    # def test_result_sigma(self):
    #     self.fail()
    #
    # def test_result_x_int(self):
    #     self.fail()
    #
    # def test_result_y_int(self):
    #     self.fail()
    #
    # def test_result_b_anc(self):
    #     self.fail()
    #
    # def test_result_sigma_b_anc(self):
    #     self.fail()
    #
    # def test_result_vds(self):
    #     self.fail()
    #
    # def test_result_f(self):
    #     self.fail()
    #
    # def test_result_f_vds(self):
    #     self.fail()
    #
    # def test_result_frac(self):
    #     self.fail()
    #
    # def test_result_beta(self):
    #     self.fail()
    #
    # def test_result_g(self):
    #     self.fail()
    #
    # def test_result_gap_max(self):
    #     self.fail()
    #
    # def test_result_q(self):
    #     self.fail()
    #
    # def test_result_w(self):
    #     self.fail()
    #
    # def test_calculate_slope(self):
    #     self.fail()
    #
    # def test_calculate_b_anc(self):
    #     self.fail()
    #
    # def test_calculate_sigma_b_anc(self):
    #     self.fail()
    #
    # def test_calculate_vds(self):
    #     self.fail()
    #
    # def test_calculate_vd(self):
    #     self.fail()
    #
    # def test_calculate_x_dash(self):
    #     self.fail()
    #
    # def test_calculate_y_dash(self):
    #     self.fail()
    #
    # def test_calculate_delta_x_dash(self):
    #     self.fail()
    #
    # def test_calculate_delta_y_dash(self):
    #     self.fail()
    #
    # def test_calculate_f(self):
    #     self.fail()
    #
    # def test_calculate_f_vds(self):
    #     self.fail()
    #
    # def test_calculate_frac(self):
    #     self.fail()
    #
    # def test_calculate_beta(self):
    #     self.fail()
    #
    # def test_calculate_g(self):
    #     self.fail()
    #
    # def test_calculate_gap_max(self):
    #     self.fail()
    #
    # def test_calculate_q(self):
    #     self.fail()
    #
    # def test_calculate_w(self):
    #     self.fail()

    def test_correct_last_step(self):
        self.thellier_cryomag.correct_last_step()
        self.assertEqual(list(self.thellier_cryomag.th['m'].v[-1]), [0.0,0.0,0.0])