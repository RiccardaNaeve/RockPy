__author__ = 'mike'
from unittest import TestCase
import RockPy as rp
import matplotlib.pyplot as plt
import RockPy
from os.path import join


class TestHysteresis(TestCase):
    def setUp(self):
        # vsm_file = '../Tutorials/test_data/MUCVSM_test.hys'
        vsm_file = join(RockPy.test_data_path, 'vsm', 'LTPY_527,1a_HYS_VSM#XX[mg]___#TEMP_300_K#STD000.000')

        self.VSM_test = rp.Sample('test')
        self.VSM_hys = self.VSM_test.add_measurement(mtype='hysteresis', mfile=vsm_file, machine='vsm')


    def test_calculate_ms(self):
        print self.VSM_hys.calculate_ms()


    def test_calculate_mrs(self):
        self.VSM_hys.calculate_mrs()
        print self.VSM_hys.results['mrs']


    def test_grid_data(self):
        # plt.plot(self.VSM_hys.get_grid())
        self.VSM_hys.data_gridding(order='first')
        self.VSM_hys.data_gridding(order='second')
        plt.plot(self.VSM_hys.data['down_field']['field'].v, self.VSM_hys.data['down_field']['mag'].v, 'g.-')
        plt.plot(self.VSM_hys.data['up_field']['field'].v, self.VSM_hys.data['up_field']['mag'].v, 'g.-')
        plt.plot(self.VSM_hys.grid_data['down_field']['field'].v, self.VSM_hys.grid_data['down_field']['mag'].v, 'r.-')
        plt.plot(self.VSM_hys.grid_data['up_field']['field'].v, self.VSM_hys.grid_data['up_field']['mag'].v, 'r.-')
        # print self.VSM_hys.grid_data['down_field']
        # print self.VSM_hys.data['down_field']
        plt.show()


    def test_correct_center(self):
        auxx = self.VSM_hys.correct_center()
        plt.plot(self.VSM_hys.data['down_field']['field'].v, self.VSM_hys.data['down_field']['mag'].v, 'g.-')
        plt.plot(self.VSM_hys.data['up_field']['field'].v, self.VSM_hys.data['up_field']['mag'].v, 'g.-')

        plt.plot(self.VSM_hys._corrected_data['down_field']['field'].v,
                 self.VSM_hys._corrected_data['down_field']['mag'].v, 'r-')
        plt.plot(self.VSM_hys._corrected_data['up_field']['field'].v,
                 self.VSM_hys._corrected_data['up_field']['mag'].v, 'r-')

        plt.plot([-1, 1], [0, 0], 'k-')
        plt.plot([0, 0], [-max(self.VSM_hys._corrected_data['down_field']['mag'].v),
                          max(self.VSM_hys._corrected_data['down_field']['mag'].v)], 'k-')
        plt.show()