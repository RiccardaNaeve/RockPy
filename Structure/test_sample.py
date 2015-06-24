from unittest import TestCase
import RockPy
from os.path import join
import timeit
import time
import sys
from pprint import pprint
from copy import deepcopy

__author__ = 'mike'


class TestSample(TestCase):
    def setUp(self):
        self.sample = RockPy.Sample(name='test_sample',
                                    mass=34.5, mass_unit='mg',
                                    diameter=5.4, height=4.3, length_unit='mm',
                                    series='pressure_0.0_GPa; temperature_300.0_C')

        self.cryomag_thellier_file = join(RockPy.test_data_path, 'cryomag', 'NLCRY_Thellier_test.TT')
        self.cryomag_thellier_is_file = join(RockPy.test_data_path, 'cryomag', 'NLCRY_Thellier_is_test.TT')

        # vftb
        self.vftb_coe_file = join(RockPy.test_data_path, 'VFTB', 'MUCVFTB_test.coe')
        self.vftb_hys_file = join(RockPy.test_data_path, 'VFTB', 'MUCVFTB_test.hys')
        self.vftb_irm_file = join(RockPy.test_data_path, 'VFTB', 'MUCVFTB_test.irm')
        self.vftb_rmp_file = join(RockPy.test_data_path, 'VFTB', 'MUCVFTB_test.rmp')

        # vsm
        self.vsm_hys_file = ''
        self.vsm_hys_virgin_file = ''
        self.vsm_hys_msi_file = ''
        self.vsm_coe_file = ''
        self.vsm_coe_irm_file = ''
        self.vsm_coe_irm_induced_file = ''
        self.vsm_rmp_file = ''

    def add_hys_measurements_with_conditions(self):
        self.hys1 = self.sample.add_measurement(mtype='hys', machine='vftb', mfile=self.vftb_hys_file,
                                                series='pressure_0.0_GPa; temperature_100.0_C')

        self.hys2 = self.sample.add_measurement(mtype='hys', machine='vftb', mfile=self.vftb_hys_file,
                                                series='pressure_1.0_GPa; temperature_200.0_C')

        self.hys3 = self.sample.add_measurement(mtype='hys', machine='vftb', mfile=self.vftb_hys_file,
                                                series='pressure_2.0_GPa; temperature_300.0_C')

        self.hys4 = self.sample.add_measurement(mtype='hys', machine='vftb', mfile=self.vftb_hys_file,
                                                series='pressure_3.0_GPa; temperature_400.0_C')

        self.hys5 = self.sample.add_measurement(mtype='hys', machine='vftb', mfile=self.vftb_hys_file,
                                                series='pressure_4.0_GPa; temperature_500.0_C')

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
            for j in range(len(check[i])):
                self.assertAlmostEqual(measurement.data[i].v[0][j], check[i][j], 5)

        path = join(RockPy.test_data_path, 'LF4C-HX_1a_TT_CRY#320[mg]_5.17[mm]_5.84[mm]#pressure_1.2_GPa#.000')

        print RockPy.get_fname_from_info(sample_group='LF4C-HX', sample_name='1a', mtype='TT', machine='CRY',
                                         mass=320, mass_unit='mg', height=5.17, height_unit='mm', diameter=5.87,
                                         series='pressure', svals=1.2, sunits='GPa')
        m = self.sample.add_measurement(path=path)

    def test_filter(self):
        self.add_hys_measurements_with_conditions()
        print(self.sample)

    def test_recalc_mageasurement_dict(self):
        self.add_hys_measurements_with_conditions()
        self.sample.recalc_info_dict()

    def test_mtypes(self):
        self.add_hys_measurements_with_conditions()
        test = sorted(list(set([m.mtype for m in self.sample.measurements])))
        self.assertEquals(test, self.sample.mtypes)

    def test_stypes(self):
        test = [t.stype for m in self.sample.measurements for t in m.series]
        test = sorted(list(set(test)))
        self.assertEquals(test, self.sample.stypes)

    def test_svals(self):
        test = [t.value for m in self.sample.measurements for t in m.series]
        test = sorted(list(set(test)))
        self.assertEquals(test, self.sample.svals)

    def test_mtype_tdict(self):
        self.assertEqual(self.sample.mtype_tdict.keys(), ['diameter', 'mass', 'height'])

    def test_stype_dict(self):
        self.add_hys_measurements_with_conditions()
        start = time.clock()
        out = {stype: self.sample.get_measurements(stypes=stype) for stype in self.sample.stypes}
        old_time = time.clock() - start
        start = time.clock()
        new = self.sample.stype_dict
        new_time = time.clock() - start
        self.assertEquals(out, new)
        print '%s - %.2f times faster' % (sys._getframe().f_code.co_name, (old_time / new_time))

    def test_mtype_stype_dict(self):
        self.add_hys_measurements_with_conditions()
        start = time.clock()

        old = {mtype: sorted(list(set([stype for m in self.sample.get_measurements(mtypes=mtype)
                                       for stype in m.stypes])))
               for mtype in self.sample.mtypes}
        old_time = time.clock() - start
        start = time.clock()
        new = self.sample.mtype_stype_dict
        new_time = time.clock() - start
        self.assertEquals(old, new)
        print '%s - %.2f times faster' % (sys._getframe().f_code.co_name, (old_time / new_time))

    def test_mtype_stype_mdict(self):
        self.add_hys_measurements_with_conditions()
        start = time.clock()
        old = {mtype: {stype: self.sample.get_measurements(mtypes=mtype, stypes=stype)
                       for stype in self.sample.mtype_stype_dict[mtype]}
               for mtype in self.sample.mtypes}
        old_time = time.clock() - start
        start = time.clock()
        new = self.sample.mtype_stype_mdict
        new_time = time.clock() - start
        self.assertEquals(old, new)
        print '%s - %.2f times faster' % (sys._getframe().f_code.co_name, (old_time / new_time))

    def test_stype_sval_dict(self):
        self.add_hys_measurements_with_conditions()
        start = time.clock()
        old = {stype: sorted(list(set([m.stype_dict[stype].value for m in self.sample.stype_dict[stype]])))
               for stype in self.sample.stypes}
        old_time = time.clock() - start
        start = time.clock()
        new = self.sample.stype_sval_dict
        new_time = time.clock() - start
        self.assertEqual(old.keys(), new.keys())
        # self.assertEqual(old.items(), new.items())
        print '%s - %.2f times faster' % (sys._getframe().f_code.co_name, (old_time / new_time))

    def test_mtype_stype_sval_mdict(self):
        self.add_hys_measurements_with_conditions()

        start = time.clock()
        old = {mt:
                   {tt: {tv: self.sample.get_measurements(mtypes=mt, stypes=tt, svals=tv)
                         for tv in self.sample.stype_sval_dict[tt]}
                    for tt in self.sample.mtype_stype_dict[mt]}
               for mt in self.sample.mtypes}
        old_time = time.clock() - start

        start = time.clock()
        new = self.sample.mtype_stype_sval_mdict
        new_time = time.clock() - start
        print '%s - %.2f times faster' % (sys._getframe().f_code.co_name, (old_time / new_time))
        self.assertEquals(old, new)

    def test_all_results(self):
        self.add_vftb_measurements()
        self.sample.all_results()
        print self.sample.results

        # def test_calc_all_mean_results(self):
        # print self.sample
        #     self.add_hys_measurements_with_conditions()
        #     self.add_vftb_measurements()
        #     print self.sample.info()
        #     # print self.sample.calc_all_mean_results()
        #     print self.sample.all_results()

    def test_remove_m_from_info_dict(self):
        compare = deepcopy(self.sample._create_info_dict())
        # self.add_hys_measurements_with_conditions()
        # pprint(self.sample.info_dict)
        for m in self.sample.measurements:
            print m
            self.sample.remove_m_from_info_dict(m=m)
        pprint(self.sample.info_dict)
        self.assertDictEqual(compare, self.sample.info_dict)

    def test_add_m2_info_dict(self):
        sample = RockPy.Sample(name='test')
        m = RockPy.Measurement(sample_obj=sample, mfile=None, machine='generic', mtype='mass', mdata=[1])
        sample.add_measurement(mobj=m)
        pprint(sample.info_dict)
        sample2 = RockPy.Sample(name='test')
        sample2.add_m2_info_dict(m)
        sample2.add_m2_info_dict(m)
        pprint(sample2.info_dict)

    def test_get_measurements(self):
        self.add_hys_measurements_with_conditions()
        self.assertEqual([], self.sample.get_measurements(mtypes='thellier', stypes='pressure', svals=0))
        self.assertEqual([self.hys1], self.sample.get_measurements(mtypes='hys', stypes='pressure', svals=0))
        self.assertEqual([self.hys1], self.sample.get_measurements(mtypes='hys', stypes='temperature', svals=100))
        self.assertEqual([self.hys1], self.sample.get_measurements(mtypes='hys', stypes='pressure', svals=0.0))
        self.assertEqual([self.hys1, self.hys2, self.hys3, self.hys4, self.hys5],
                         self.sample.get_measurements(mtypes='hys', stypes='pressure'))

        # multiple mtypes
        self.assertEqual([self.hys1],
                         self.sample.get_measurements(mtypes='hys', stypes=['pressure', 'temperature'], svals=0))
        self.assertEqual([self.hys1, self.hys2],
                         self.sample.get_measurements(mtypes='hys', stypes=['pressure', 'temperature'], svals=[0, 200]))
        # multiple stypes
        self.assertEqual([self.hys1, self.hys2],
                         self.sample.get_measurements(mtypes='hys', stypes='pressure', svals=[0, 1]))
        self.assertEqual([self.hys1, self.hys2, self.hys3],
                         self.sample.get_measurements(mtypes='hys', stypes=['pressure', 'temperature'],
                                                      svals=[0, 1, 300]))
        # sval_range
        self.assertEqual([self.hys1, self.hys2],
                         self.sample.get_measurements(mtypes='hys', stypes='pressure', sval_range=[0, 1]))
        self.assertEqual([self.hys1],
                         self.sample.get_measurements(mtypes='hys', stypes='pressure', sval_range='<1'))
        self.assertEqual([self.hys1, self.hys2],
                         self.sample.get_measurements(mtypes='hys', stypes='pressure', sval_range='<=1'))

    def test_add_m2_mdict(self):
        sample = RockPy.Sample(name='test')
        compare = deepcopy(sample.mdict)
        m1 = RockPy.Measurement(sample_obj=sample, mfile=None, machine='generic', mtype='mass', mdata=[1])
        m1.add_sval(stype='m1a', sval=1)
        m1.add_sval(stype='m1b', sval=2)
        sample.add_m2_mdict(mobj=m1)
        self.assertTrue(m1 in sample.mdict['stype']['m1a'])
        self.assertTrue(m1 in sample.mdict['stype']['m1b'])

        m2 = RockPy.Measurement(sample_obj=sample, mfile=None, machine='generic', mtype='height', mdata=[1])
        m2.add_sval(stype='m2a', sval=3)
        m2.add_sval(stype='m2b', sval=4)
        self.assertTrue(m2 in sample.mdict['stype']['m2a'])
        self.assertTrue(m2 in sample.mdict['stype']['m2b'])
        m2.add_sval(stype='m2c-added_later', sval=100)
        self.assertTrue(m2 in sample.mdict['stype']['m2c-added_later'])
        sample.remove_m_from_mdict(mobj=m1)
        self.assertFalse('m1a' in sample.mdict['stype'])
        self.assertFalse('m1b' in sample.mdict['stype'])
        sample.remove_m_from_mdict(mobj=m2)
        self.assertDictEqual(compare, sample.mdict)
