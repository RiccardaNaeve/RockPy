from unittest import TestCase
import numpy as np
from RockPy.Structure.data import RockPyData


__author__ = 'wack'


class TestRockPyData(TestCase):
    def setUp(self):
        # run before each test
        self.testdata = ((1, 2, 3, 4),
                         (1, 6, 7, 8),
                         (1, 2, 11, 12),
                         (1, 6, 55, 66))

        self.col_names = ('F', 'Mx', 'My', 'Mz')
        self.row_names = ('1.Zeile', '2.Zeile', '3.Zeile', '4.Zeile')
        self.units = ('T', 'mT', 'fT', 'pT')

        self.RPD = RockPyData(column_names=self.col_names, row_names=self.row_names, units=self.units,
                              data=self.testdata)

    def test_column_names(self):
        self.assertEqual(self.RPD.column_names, list(self.col_names))

    def test_column_count(self):
        self.assertEqual(self.RPD.column_count, len(self.col_names))

    def test__find_duplicate_variable_rows(self):
        # self.assertTrue((self.RPD._find_duplicate_variables()[0] == np.array([0, 1, 2])).all())
        self.assertEqual(self.RPD._find_duplicate_variable_rows(), [(0, 1, 2, 3)])

        # redefine variabe alias to the first two columns
        self.RPD.define_alias('variable', ('F', 'Mx'))
        self.assertEqual(self.RPD._find_duplicate_variable_rows(), [(0, 2), (1, 3)])

    def test_rename_column(self):
        self.RPD.rename_column('Mx', 'M_x')
        self.assertEqual(self.RPD.column_names, ['F', 'M_x', 'My', 'Mz'])

    def test_append_rows(self):
        self.RPD.append_rows([5,6,7,8], '5.Zeile')