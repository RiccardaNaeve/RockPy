from unittest import TestCase
import RockPy
from os.path import join

__author__ = 'mike'


class TestSample(TestCase):
    def setUp(self):
        self.sample = RockPy.Sample(name='test_sample',
                                    mass=34.5, mass_unit='mg',
                                    diameter=5.4, height=4.3, length_unit='mm',
                                    treatments='pressure_0.0_GPa; temperature_300.0_C')

        self.cryomag_thellier_file = join(RockPy.test_data_path, 'NLCRY_Thellier_test.TT')
        self.cryomag_thellier_is_file = join(RockPy.test_data_path, 'NLCRY_Thellier_is_test.TT')

        # vftb
        self.vftb_coe_file = join(RockPy.test_data_path, 'MUCVFTB_test.coe')
        self.vftb_hys_file = join(RockPy.test_data_path, 'MUCVFTB_test.hys')
        self.vftb_irm_file = join(RockPy.test_data_path, 'MUCVFTB_test.irm')
        self.vftb_rmp_file = join(RockPy.test_data_path, 'MUCVFTB_test.rmp')

        # vsm
        self.vsm_hys_file = ''
        self.vsm_hys_virgin_file = ''
        self.vsm_hys_msi_file = ''
        self.vsm_coe_file = ''
        self.vsm_coe_irm_file = ''
        self.vsm_coe_irm_induced_file = ''
        self.vsm_rmp_file = ''

    def add_hys_measurements_with_conditions(self):
        self.sample.add_measurement(mtype='hysteresis', machine='vftb', mfile=self.vftb_hys_file,
                                    treatments='pressure_0.0_GPa; temperature_100.0_C')

        self.sample.add_measurement(mtype='hysteresis', machine='vftb', mfile=self.vftb_hys_file,
                                    treatments='pressure_1.0_GPa; temperature_200.0_C')

        self.sample.add_measurement(mtype='hysteresis', machine='vftb', mfile=self.vftb_hys_file,
                                    treatments='pressure_2.0_GPa; temperature_300.0_C')

        self.sample.add_measurement(mtype='hysteresis', machine='vftb', mfile=self.vftb_hys_file,
                                    treatments='pressure_3.0_GPa; temperature_400.0_C')

        self.sample.add_measurement(mtype='hysteresis', machine='vftb', mfile=self.vftb_hys_file,
                                    treatments='pressure_4.0_GPa; temperature_500.0_C')


    def test_mass_kg(self):
        self.assertEqual(self.sample.mass_kg.v, 3.45e-5)

    def test_height_m(self):
        self.assertEqual(self.sample.height_m.v, 0.0043)

    def test_diameter_m(self):
        self.assertEqual(self.sample.diameter_m.v, 0.0054)


    def test_add_measurement(self):
        measurement = self.sample.add_measurement(mtype='thellier', mfile=self.cryomag_thellier_file, machine='cryomag')

        check = {
            'nrm': [2.00000000e+01, 2.08720000e-08, -8.95180000e-09, 5.04950000e-09, 2.88920000e-10, 2.32652650e-08],
        }
        for i in check:
            for j in range(len(check[i])):
                self.assertAlmostEqual(measurement.data[i].v[0][j], check[i][j], 5)

    def test_mtype_tdict(self):
        self.assertEqual(self.sample.mtype_tdict.keys(), ['diameter', 'mass', 'height'])

    def test_filter(self):
        self.add_hys_measurements_with_conditions()
        print(self.sample)