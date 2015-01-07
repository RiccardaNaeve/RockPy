from unittest import TestCase
import numpy as np
from Structure.sample import Sample

__author__ = 'mike'


class TestThellier(TestCase):
    def setUp(self):
        cryomag_file = '../Tutorials/test_data/NLCRY_Thellier_test.TT'
        self.test_sample_cryomag = Sample(name='1a')
        self.thellier_cryomag = self.test_sample_cryomag.add_measurement(mtype='thellier', mfile=cryomag_file,
                                                                         machine='cryomag')
        self.parameter = {'t_min': 450, 't_max': 540}

    # def test_format_cryomag(self):
    # self.fail()
    #
    # def test_format_sushibar(self):
    # self.fail()
    #
    # def test_remove_duplicate_measurements(self):
    # self.fail()
    #
    # def test_delete_temp(self):
    #     self.fail()

    def test_result_n(self):
        self.assertEqual([14], self.thellier_cryomag.result_n().v)
        self.assertEqual([10], self.thellier_cryomag.result_n(**self.parameter).v)


    def test_result_slope(self):
        self.assertAlmostEqual([-1.01], self.thellier_cryomag.result_slope().v, 2)
        self.assertAlmostEqual([-1.00], self.thellier_cryomag.result_slope(**self.parameter).v, 2)


    def test_result_sigma(self):
        self.assertAlmostEqual([0.04], self.thellier_cryomag.result_sigma().v, 2)
        self.assertAlmostEqual([0.05], self.thellier_cryomag.result_sigma(**self.parameter).v, 2)

    def test_result_f(self):
        # self.thellier_cryomag.result_f()
        # self.thellier_cryomag.plt_arai()
        self.assertAlmostEqual([0.98], self.thellier_cryomag.result_f().v, 2)
        self.assertAlmostEqual([0.88], self.thellier_cryomag.result_f(**self.parameter).v, 2)

    # def test_result_f_vds(self):
    #     self.fail()

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
    #
    # def test__get_ck_data(self):
    #     self.fail()
    #
    #
    # def test_result_n_ptrm(self):
    #     self.assertEqual([4], self.thellier_cryomag.result_n_ptrm().v)
    #
    #
    # def test_result_ck_check_percent(self):
    #     self.thellier_cryomag.result_ck_check_percent()
    #     # print(self.thellier_cryomag.results)
    #     self.fail()
    #
    #
    # def test_calculate_delta_ck(self):
    #     self.thellier_cryomag.result_delta_ck()
    #     # print(self.thellier_cryomag.results)
    #     self.fail()
    #
    #
    # def test_calculate_drat(self):
    #     self.thellier_cryomag.result_drat()
    #     # print(self.thellier_cryomag.results)
    #     self.fail()
    #
    #
    # def test_result_ck_max_dev(self):
    #     self.thellier_cryomag.result_ck_max_dev()
    #     # print(self.thellier_cryomag.results)
    #     self.fail()
    #
    #
    # def test_calculate_cdrat(self):
    #     self.thellier_cryomag.result_cdrat()
    #     # print(self.thellier_cryomag.results)
    #     self.fail()
    #
    #
    # def test_result_drats(self):
    #     self.thellier_cryomag.result_drats()
    #     # print(self.thellier_cryomag.results)
    #     self.fail()
    #
    #
    # def test_result_mean_drat(self):
    #     self.thellier_cryomag.result_mean_drat()
    #     # print(self.thellier_cryomag.results)
    #     self.fail()
    #
    #
    # def test_result_mean_dev(self):
    #     self.thellier_cryomag.result_mean_dev()
    #     self.fail()
    #
    #
    # def test_get_d_tail(self):
    #     self.thellier_cryomag.get_d_tail()
    #     self.fail()
    #
    #
    # def test_result_n_tail(self):
    #     self.assertEqual([3], self.thellier_cryomag.result_n_tail().v)
    #
    # def test_result_drat_tail(self):
    #     self.thellier_cryomag.result_drat_tail()
    #     # print(self.thellier_cryomag.results)
    #     self.fail()
    #
    #
    # def test_result_delta_tr(self):
    #     self.thellier_cryomag.result_delta_tr()
    #     # print(self.thellier_cryomag.results)
    #     self.fail()
    #
    #
    # def test_result_md_vds(self):
    #     self.thellier_cryomag.result_md_vds()
    #     self.fail()
    #
    # def test_get_d_ac(self):
    #     self.thellier_cryomag.get_d_ac()
    #     self.fail()
    #
    #
    # def test_result_n_ac(self):
    #     self.assertEqual([4], self.thellier_cryomag.result_n_ac().v)


    def test_result_delta_ac(self):
        self.thellier_cryomag.result_delta_ac()
        # print self.thellier_cryomag.results
        # for i in ['th', 'pt', 'ac','ck', 'tr']:
        #     with open('/Users/mike/Desktop/' +i + '.txt', 'a') as f:
        #         a = self.thellier_cryomag.data[i]
        #         f.write('\t'.join(a.column_names))
        #         f.write('\n')
        #         for i, line in enumerate(a.v):
        #             text = '\t'.join(list(map(str, line)))
        #             f.write(text)
        #             f.write('\n')
        # self.fail()


    def test__get_idx_equal_val(self):
        print(self.thellier_cryomag._get_idx_equal_val('pt', 'th'))