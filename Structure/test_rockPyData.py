from unittest import TestCase

from RockPy.Structure.data import RockPyData

__author__ = 'wack'


class TestRockPyData(TestCase):
    def setUp(self):
        # run before each test
        self.testdata = ((1, 2, 3, 4),
                        (5, 6, 7, 8),
                        (9, 10, 11, 12))

        self.col_names = ('F', 'Mx', 'My', 'Mz')
        self.row_names = ('1.Zeile','2.Zeile','3.Zeile')
        self.units = ('T', 'mT', 'fT', 'pT')

        self.RPD = RockPyData(column_names=self.col_names, row_names=self.row_names, units=self.units, data=self.testdata)

    def test_column_names(self):
        self.assertEqual(self.RPD.column_names, list(self.col_names))

    def test_column_count(self):
        self.assertEqual(self.RPD.column_count, len( self.col_names))