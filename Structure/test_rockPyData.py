from unittest import TestCase  # Unit testing framework
import numpy as np  # numerical array functions
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
        self.row_names = ('1.Zeile', '2.Zeile_A', '3.Zeile', '4.Zeile_A')
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
        self.RPD = self.RPD.eliminate_duplicate_variable_rows(substfunc='mean')
        self.assertTrue(np.array_equal(self.RPD.v, np.array([[1., 2., 7., 8.], [1., 6., 31., 37.]])))
        self.assertTrue(np.array_equal(self.RPD.e, np.array([[0., 0., 4., 4.], [0., 0., 24., 29.]])))

    def test_mean(self):
        self.RPD = self.RPD.mean()
        self.assertTrue(np.array_equal(self.RPD.v, np.array([[1., 4., 19., 22.5]])))
        np.testing.assert_allclose(self.RPD.e, np.array([[0., 2., 20.976, 25.273]]), atol=0.01)

    def test_max(self):
        self.RPD = self.RPD.max()
        self.assertTrue(np.array_equal(self.RPD.v, np.array([[1., 6., 55., 66.]])))

    def test_filter_row_names(self):
        self.assertEqual(self.RPD.filter_row_names(('1.Zeile', '3.Zeile')).row_names, ['1.Zeile', '3.Zeile'])

    def test_filter_match_row_names(self):
        # get all rows ending with '_A'
        self.assertEqual(self.RPD.filter_match_row_names('.*_A').row_names, ['2.Zeile_A', '4.Zeile_A'])

    def test_append_columns(self):
        cb = self.RPD.column_count
        d = (8,7,6,5)
        self.RPD = self.RPD.append_columns( 'neue Spalte', d)
        self.assertEqual( cb+1, self.RPD.column_count)
        self.assertTrue(np.array_equal( self.RPD[ 'neue Spalte'].v, np.array(d)))