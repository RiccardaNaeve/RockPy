from unittest import TestCase
import RockPy as rp
import Visualize.base
__author__ = 'mike'


class TestGeneric(TestCase):
    def setUp(self):
        self.sample = rp.Sample('Plot_Test')
        self.Plot = Visualize.base.Generic(self.sample)

    def test_create_heat_color_map(self):
        list = range(10)
        colors = ['#0000ff', '#1c00e2', '#3800c6', '#5500aa', '#71008d', '#8d0071', '#aa0055', '#c60038', '#e2001c', '#ff0000']
        self.assertEqual(self.Plot.create_heat_color_map(list), colors)