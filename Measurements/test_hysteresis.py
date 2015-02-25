__author__ = 'mike'
from unittest import TestCase
import RockPy as rp
import matplotlib.pyplot as plt
import RockPy
from os.path import join
import numpy as np
from copy import deepcopy


class TestHysteresis(TestCase):
    def setUp(self):
        vsm_file = '../Tutorials/test_data/MUCVSM_test.hys'
        # vsm_file = join(RockPy.test_data_path, 'vsm', 'LTPY_527,1a_HYS_VSM#XX[mg]___#TEMP_300_K#STD000.000')

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
        self.VSM_hys.correct_center()
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


    def test_correct_slope(self):
        res = []
        j = 0.4
        # for j in np.linspace(0.1, 1):
        vsm2 = deepcopy(self.VSM_hys)
        for dtype in vsm2.data:
            idx = [i for i, v in enumerate(vsm2.data[dtype]['field'].v) if
                   abs(v) <= j * max(vsm2.data[dtype]['field'].v)]
            # print len(idx)
            vsm2.data[dtype] = vsm2.data[dtype].filter_idx(idx)
        vsm2.data_gridding()
        popt2 = vsm2.correct_slope()
        popt = self.VSM_hys.correct_slope()
        res.append(popt2[0])
        # plt.plot(np.linspace(0.3, 1), res)
        # print res
        # plot hysteresis & cut hysteresis
        plt.plot(self.VSM_hys.data['down_field']['field'].v,
                 self.VSM_hys.data['down_field']['mag'].v, 'r:')
        plt.plot(self.VSM_hys.data['up_field']['field'].v,
                 self.VSM_hys.data['up_field']['mag'].v, 'r:')
        plt.plot(vsm2.data['down_field']['field'].v,
                 vsm2.data['down_field']['mag'].v, 'k--')
        plt.plot(vsm2.data['up_field']['field'].v,
                 vsm2.data['up_field']['mag'].v, 'k--')

        #plot approach to sat calculation
        x = self.VSM_hys.corrected_data['down_field']['field'].v
        y = popt[0] + popt[1] * x + popt[2] * x ** -1
        plt.plot(x, y, 'r:')
        x = vsm2.corrected_data['down_field']['field'].v
        y = popt2[0] + popt2[1] * x + popt2[2] * x ** -1
        plt.plot(x, y, 'k--')

        # plot assymptote
        x = np.array([0, max(self.VSM_hys.corrected_data['up_field']['field'].v)])
        plt.plot(x, popt[0] + popt[1] * x, 'r:')  # +popt[2]*x**-1)
        x = np.array([0, max(vsm2.corrected_data['up_field']['field'].v)])
        plt.plot(x, popt2[0] + popt2[1] * x, 'k--')  # +popt[2]*x**-1)
        plt.xlim([0, 0.5])
        plt.ylim([0, max(vsm2.corrected_data['up_field']['mag'].v) * 1.5])
        plt.show()


    def test_data_gridding(self):
        self.fail()