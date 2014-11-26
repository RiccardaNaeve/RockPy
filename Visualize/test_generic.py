from unittest import TestCase
import RockPy as rp
import Visualize.base

__author__ = 'mike'


class TestGeneric(TestCase):
    def setUp(self):
        self.sample = rp.Sample('test_sample')
        self.Plot = Visualize.base.Generic(self.sample)

    def test_create_heat_color_map(self):
        list = range(10)
        colors = ['#0000ff', '#1c00e2', '#3800c6', '#5500aa', '#71008d', '#8d0071', '#aa0055', '#c60038', '#e2001c',
                  '#ff0000']
        self.assertEqual(self.Plot.create_heat_color_map(list), colors)


    def test___treatment_variable_transformation(self):
        from pprint import pprint
        self.add_measurements_treatments()
        ddict = self.Plot._treatment_variable_transformation(self.Plot.sample_group.sample_list[0], mtype='thellier', ttype='pressure')
        self.assertIsInstance(ddict, dict)

    def add_measurements_treatments(self):
        from os import listdir
        from os.path import join
        folder = '../testing/test_data/treatments'
        pressures = ['0.0, GPa', '0.6, GPa', '1.2, GPa', '1.8, GPa']

        for i, v in enumerate(['P0', 'P1', 'P2', 'P3']):
            tt_data = [join(folder+'/', f) for f in listdir(folder) if 'tt' in f if v in f]
            trm_data = [join(folder+'/', f) for f in listdir(folder) if 'trm' in f if v in f]
            M = self.sample.add_measurement(mtype='thellier', mfile=tt_data[0], machine='cryomag',
                                   treatments='Pressure, ' + pressures[i])
            M.set_initial_state(mtype='trm', mfile=trm_data[0], machine='cryomag')