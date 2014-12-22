from unittest import TestCase

from RockPy.Structure.data import _to_tuple

__author__ = 'michael'


class Test_Structure_Aux(TestCase):
    def test__to_tuple(self):
        self.assertEqual(_to_tuple( (1,2,3)), (1,2,3))
        self.assertEqual(_to_tuple( '1.Zeile'), ('1.Zeile',))
        self.assertEqual(_to_tuple( ['1.Zeile']), ('1.Zeile',))
        self.assertEqual(_to_tuple( ['1.Zeile', '2.Zeile']), ('1.Zeile', '2.Zeile'))
        self.assertEqual(_to_tuple( None), (None,))