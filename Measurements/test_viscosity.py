from unittest import TestCase
import RockPy
import os.path
from profilehooks import profile

__author__ = 'mike'


class TestViscosity(TestCase):
    def setUp(self):
        self.sample = RockPy.Sample(name='test_sample')
        # files
        vsm_file = os.path.join(RockPy.test_data_path, 'vsm', 'FeNi20_FeNi20-Ga72-G01_VISC_VSM#6,0[mg]_[]_[]###.001')

        # add measurements
        self.vsm_measurement = self.sample.add_measurement(mtype='viscosity', mfile=vsm_file, machine='vsm')

    def test_fit_viscous_relaxation(self):
        #just a wrapper for scipy.stats.linregress should always work
        pass

    def test_format_vsm(self):
        """
        tests consistency of data import
        :return:
        """
        copy_from_file_line1 = [+1.500078E+00, +17.15022E-06,
                                +158.4568E-06]  # directly copied from line one in datafile (counting from 0)
        self.assertEqual(self.vsm_measurement.data['data']['time'].v[1], copy_from_file_line1[0])
        self.assertEqual(self.vsm_measurement.data['data']['mag'].v[1], copy_from_file_line1[1])
        self.assertEqual(self.vsm_measurement.data['data']['field'].v[1], copy_from_file_line1[2])

    def test_correct_ommit_first_n(self):
        copy_from_file_line1 = [+1.500078E+00, +17.15022E-06,
                                +158.4568E-06]  # directly copied from line one in datafile (counting from 0)

        self.vsm_measurement.correct_ommit_first_n(n=1)  # ommit first data point -> line 1 -> line 0
        self.assertEqual(self.vsm_measurement.data['data']['time'].v[0], copy_from_file_line1[0])
        self.assertEqual(self.vsm_measurement.data['data']['mag'].v[0], copy_from_file_line1[1])
        self.assertEqual(self.vsm_measurement.data['data']['field'].v[0], copy_from_file_line1[2])

    def test_result_visc_decay(self):
        self.assertAlmostEquals(self.vsm_measurement.result_visc_decay(ommit_first_n=1).v,
                                -6.651733071E-8)  # calculated with excel
        self.assertAlmostEquals(self.vsm_measurement.result_visc_decay(ommit_first_n=0).v,
                                -6.641746193E-8)  # calculated with excel

    def test_result_visc_decay_norm(self):
        self.assertAlmostEquals(self.vsm_measurement.result_visc_decay_norm(ommit_first_n=0).v,
                                -3.8655466E-3)  # calculated with excel
        self.assertAlmostEquals(self.vsm_measurement.result_visc_decay_norm(ommit_first_n=1).v,
                                -3.8785118E-03)  # calculated with excel

    def test_calculate_visc_decay(self):
        res = self.vsm_measurement.calculate_visc_decay()  # returns slope, std_err, norm_slope, norm_std_err
        self.assertAlmostEquals(res[0], -6.641746193E-8)  # check if slope correct
        self.assertAlmostEquals(res[2], -3.8655466E-03)  # check if norm_slope correct