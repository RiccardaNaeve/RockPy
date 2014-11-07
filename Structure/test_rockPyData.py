from unittest import TestCase
import numpy as np
from RockPy.Structure.data import RockPyData, _to_tuple


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
        d1 = [[5, 6, 7, 8], [9, 10, 11, 12]]
        self.RPD = self.RPD.append_rows(d1, ('5.Zeile', '6.Zeile'))
        self.assertTrue(np.array_equal(self.RPD.v[-2:, :], np.array(d1)))
        d2 = [5, 6, 7, 8]
        self.RPD = self.RPD.append_rows(d2, '5.Zeile')
        self.assertTrue(np.array_equal(self.RPD.v[-1, :], np.array(d2)))
        # lets try with other RockPyData object
        # self.RPD.append_rows( self.RPD)
        # print self.RPD

    def test_delete_rows(self):
        self.RPD = self.RPD.delete_rows((0, 2))
        self.assertTrue(np.array_equal(self.RPD.v, np.array(self.testdata)[(1, 3), :]))

    def test_eliminate_duplicate_variable_rows(self):
        # check for one variable column
        self.RPD = self.RPD.eliminate_duplicate_variable_rows()
        self.assertTrue(np.array_equal(self.RPD.v, np.array([]).reshape(0, 4)))

    def test_eliminate_duplicate_variable_rows2(self):
        # check for two variable columns
        self.RPD.define_alias('variable', ('F', 'Mx'))
        self.RPD  = self.RPD.eliminate_duplicate_variable_rows(subst='mean')
        self.assertTrue(np.array_equal(self.RPD.v, np.array([[1., 2., 7., 8.], [1., 6., 31., 37.]])))
        self.assertTrue(np.array_equal(self.RPD.e, np.array([[0., 0., 4., 4.], [0., 0., 24., 29.]])))

    def test_mean(self):
        self.RPD = self.RPD.mean()
        self.assertTrue(np.array_equal(self.RPD.v, np.array([[1., 4., 19., 22.5]])))
        np.testing.assert_allclose(self.RPD.e, np.array([[0., 2., 20.976, 25.273]]), atol=0.01)