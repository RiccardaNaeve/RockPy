from unittest import TestCase
import RockPy as rp

__author__ = 'mike'


class TestSample(TestCase):
    def setUp(self):
        self.sample = rp.Sample(name='test_sample',
                                mass=34.5, mass_unit='mg',
                                diameter=5.4, height=4.3, length_unit='mm',
                                treatment='pressure, 0.0, GPa; temperature, 300.0, C')

        self.cryomag_thellier_file = '../testing/test_data/NLCRY_Thellier_test.TT'
        self.cryomag_thellier_is_file = '../testing/test_data/NLCRY_Thellier_is_test.TT'

        #vftb
        self.vftb_hys_file = ''
        self.vftb_coe_file = ''
        self.vftb_irm_file = ''
        self.vftb_rmp_file = ''

        #vsm
        self.vsm_hys_file = ''
        self.vsm_hys_virgin_file = ''
        self.vsm_hys_msi_file = ''
        self.vsm_coe_file = ''
        self.vsm_coe_irm_file = ''
        self.vsm_coe_irm_induced_file = ''
        self.vsm_rmp_file = ''



    def test_mass_kg(self):
        self.assertEqual(self.sample.mass_kg.v, 3.45e-5)

    def test_height_m(self):
        self.assertEqual(self.sample.height_m.v, 0.0043)

    def test_diameter_m(self):
        self.assertEqual(self.sample.diameter_m.v, 0.0054)


    def test_add_measurement(self):
        measurement = self.sample.add_measurement(mtype='thellier', mfile=self.cryomag_thellier_file, machine='cryomag')

        check = {'nrm':[2.00000000e+01, 2.08720000e-08, -8.95180000e-09, 5.04950000e-09, 2.88920000e-10, 2.32652650e-08],
                 }
        for i in check:
            for j in range(len(check[i])):
                self.assertAlmostEqual(measurement.data[i].v[0][j], check[i][j], 5)
    #
    # def test_calc_all(self):
    #     self.fail()
    #
    # def test_mass_kg(self):
    #     self.fail()
    #
    # def test_height_m(self):
    #     self.fail()
    #
    # def test_mtypes(self):
    #     self.fail()
    #
    # def test_ttypes(self):
    #     self.fail()
    #
    # def test_tvals(self):
    #     self.fail()
    #
    def test_mtype_tdict(self):
        self.assertEqual(self.sample.mtype_tdict.keys(), ['diameter', 'mass', 'height'])

    def test_mtype_dict(self):
        print self.sample.mtype_dict
        self.assertEqual(self.sample.mtype_tdict.keys(), ['diameter', 'mass', 'height'])
    #
    # def test_ttype_dict(self):
    #     self.fail()
    #
    # def test_mtype_ttype_dict(self):
    #     self.fail()
    #
    # def test_mtype_ttype_mdict(self):
    #     self.fail()
    #
    # def test_ttype_tval_dict(self):
    #     self.fail()
    #
    # def test_mtype_ttype_tval_dict(self):
    #     self.fail()
    #
    # def test_get_measurements(self):
    #     self.fail()
    #
    # def test_get_measurements_with_treatment(self):
    #     self.fail()