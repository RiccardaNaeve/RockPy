from unittest import TestCase
import RockPy as rp
import time
import sys

__author__ = 'mike'


class TestMeasurement(TestCase):
    def setUp(self):
        self.sample = rp.Sample(name='test_sample')
        self.generic_M = self.sample.add_measurement(mtype='mass', mfile=None,
                                                     series='pressure_0.0_GPa; temperature_300.0_C')

    def test__get_series_from_suffix(self):
        list = [['pressure', 0.0, 'GPa'], ['temperature', 300.0, 'C']]
        self.assertEqual(self.generic_M._get_series_from_opt(), list)


    def test__add_series_from_opt(self):
        measurement = self.sample.add_measurement(mtype='mass', mfile=None,
                                                  series='pressure_0.0_GPa; temperature_300.0_C')
        out = [i.stype for i in measurement.series]
        self.assertEquals(out, ['pressure', 'temperature'])

    def test___create_info_dict(self):
        self.generic_M.recalc_info_dict()
        self.assertEquals(self.generic_M._info_dict['stype'].keys(), ['pressure', 'temperature'])


    def test_stypes(self):
        self.generic_M.recalc_info_dict()
        start = time.clock()
        old = sorted(list(set([t.stype for t in self.generic_M.series])))
        old_time = time.clock() - start
        start = time.clock()
        new = self.generic_M.stypes
        new_time = time.clock() - start
        self.assertEquals(old, new)
        print '%s - %.2f times faster' % (sys._getframe().f_code.co_name, (old_time / new_time))


    def test_svals(self):
        self.generic_M.recalc_info_dict()
        start = time.clock()
        old = sorted(list(set([t.value for t in self.generic_M.series])))
        old_time = time.clock() - start
        start = time.clock()
        new = self.generic_M.svals
        new_time = time.clock() - start
        self.assertEquals(old, new)
        print '%s - %.2f times faster' % (sys._getframe().f_code.co_name, (old_time / new_time))


    def test_stype_dict(self):
        self.generic_M.recalc_info_dict()
        start = time.clock()
        old = {t.stype: t for t in self.generic_M.series}
        old_time = time.clock() - start
        start = time.clock()
        new = self.generic_M.stype_dict
        new_time = time.clock() - start
        self.assertEquals(old.keys() , new.keys())
        print '%s - %.2f times faster' % (sys._getframe().f_code.co_name, (old_time / new_time))