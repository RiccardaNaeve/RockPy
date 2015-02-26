from unittest import TestCase
import RockPy
from os.path import join
import timeit
import time
import sys

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

    def add_vftb_measurements(self):
        self.sample.add_measurement(mtype='backfiled', mfile=self.vftb_coe_file, machine='vftb')
        self.sample.add_measurement(mtype='hysteresis', mfile=self.vftb_hys_file, machine='vftb')
        self.sample.add_measurement(mtype='irm_acquisition', mfile=self.vftb_irm_file, machine='vftb')
        self.sample.add_measurement(mtype='thermocurve', mfile=self.vftb_rmp_file, machine='vftb')

    def test_add_measurement(self):
        measurement = self.sample.add_measurement(mtype='thellier', mfile=self.cryomag_thellier_file, machine='cryomag')
        check = {
            'nrm': [2.00000000e+01, 2.08720000e-08, -8.95180000e-09, 5.04950000e-09, 2.88920000e-10, 735277.720278,
                    2.32652650e-08],
        }
        for i in check:
            for j,v in enumerate(check[i]):
                self.assertAlmostEqual(measurement.data[i].v[0][j], v, 5)


    def test_filter(self):
        self.add_hys_measurements_with_conditions()
        print(self.sample)

    def test_recalc_measurement_dict(self):
        self.add_hys_measurements_with_conditions()
        self.sample.recalc_info_dict()

    def test_mtypes(self):
        self.add_hys_measurements_with_conditions()
        test = sorted(list(set([m.mtype for m in self.sample.measurements])))
        self.assertEquals(test, self.sample.mtypes)


    def test_ttypes(self):
        test = [t.ttype for m in self.sample.measurements for t in m.treatments]
        test = sorted(list(set(test)))
        self.assertEquals(test, self.sample.ttypes)

    def test_tvals(self):
        test = [t.value for m in self.sample.measurements for t in m.treatments]
        test = sorted(list(set(test)))
        self.assertEquals(test, self.sample.tvals)

    def test_mtype_tdict(self):
        self.assertEqual(self.sample.mtype_tdict.keys(), ['diameter', 'mass', 'height'])

    def test_ttype_dict(self):
        self.add_hys_measurements_with_conditions()
        start = time.clock()
        out = {ttype: self.sample.get_measurements(ttype=ttype) for ttype in self.sample.ttypes}
        old_time = time.clock() - start
        start = time.clock()
        new = self.sample.ttype_dict
        new_time = time.clock() - start
        self.assertEquals(out, new)
        print '%s - %.2f times faster' % (sys._getframe().f_code.co_name, (old_time / new_time))


    def test_mtype_ttype_dict(self):
        self.add_hys_measurements_with_conditions()
        start = time.clock()

        old = {mtype: sorted(list(set([ttype for m in self.sample.get_measurements(mtype=mtype)
                                       for ttype in m.ttypes])))
               for mtype in self.sample.mtypes}
        old_time = time.clock() - start
        start = time.clock()
        new = self.sample.mtype_ttype_dict
        new_time = time.clock() - start
        self.assertEquals(old, new)
        print '%s - %.2f times faster' % (sys._getframe().f_code.co_name, (old_time / new_time))


    def test_mtype_ttype_mdict(self):
        self.add_hys_measurements_with_conditions()
        start = time.clock()
        old = {mtype: {ttype: self.sample.get_measurements(mtype=mtype, ttype=ttype)
                       for ttype in self.sample.mtype_ttype_dict[mtype]}
               for mtype in self.sample.mtypes}
        old_time = time.clock() - start
        start = time.clock()
        new = self.sample.mtype_ttype_mdict
        new_time = time.clock() - start
        self.assertEquals(old, new)
        print '%s - %.2f times faster' % (sys._getframe().f_code.co_name, (old_time / new_time))


    def test_ttype_tval_dict(self):
        self.add_hys_measurements_with_conditions()
        start = time.clock()
        old = {ttype: sorted(list(set([m.ttype_dict[ttype].value for m in self.sample.ttype_dict[ttype]])))
               for ttype in self.sample.ttypes}
        old_time = time.clock() - start
        start = time.clock()
        new = self.sample.ttype_tval_dict
        new_time = time.clock() - start
        self.assertEqual(old.keys(), new.keys())
        # self.assertEqual(old.items(), new.items())
        print '%s - %.2f times faster' % (sys._getframe().f_code.co_name, (old_time / new_time))


    def test_mtype_ttype_tval_mdict(self):
        self.add_hys_measurements_with_conditions()

        start = time.clock()
        old = {mt:
                   {tt: {tv: self.sample.get_measurements(mtype=mt, ttype=tt, tval=tv)
                         for tv in self.sample.ttype_tval_dict[tt]}
                    for tt in self.sample.mtype_ttype_dict[mt]}
               for mt in self.sample.mtypes}
        old_time = time.clock() - start

        start = time.clock()
        new = self.sample.mtype_ttype_tval_mdict
        new_time = time.clock() - start
        print '%s - %.2f times faster' % (sys._getframe().f_code.co_name, (old_time / new_time))
        self.assertEquals(old, new)

    def test_all_results(self):
        self.add_vftb_measurements()
        self.sample.all_results()
        print self.sample.results

    # def test_calc_all_mean_results(self):
    #     print self.sample
    #     self.add_hys_measurements_with_conditions()
    #     self.add_vftb_measurements()
    #     print self.sample.info()
    #     # print self.sample.calc_all_mean_results()
    #     print self.sample.all_results()