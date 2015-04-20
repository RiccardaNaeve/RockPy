__author__ = 'wack'

from RockPy.Structure.data import RockPyData, condense


# script to test data objects

import numpy as np
import numpyson

from copy import deepcopy


def test():
    # define some data for tutorials.rst
    testdata = ((1, 2, 3, 4),
                (2, 6, 7, 8),
                (9, 10, 11, 12))

    testdata2 = ((1, 1),
                 (2, 2),
                 (19, 3))

    # create a rockpydata object with named columns and filled with testdata
    d = RockPyData(column_names=('F', 'Mx', 'My', 'Mz'), row_names=('1.Zeile', '2.Zeile', '3.Zeile'),
                   units=('T', 'mT', 'fT', 'pT'), data=testdata)

    d_json = numpyson.dumps(d)
    print d_json
    dd = numpyson.loads(d_json)
    print repr(dd)

    print "dd:", dd

    #d = d.eliminate_duplicate_variable_rows(substfunc='last')
    #print d._find_unique_variable_rows()
    print('d:\n%s' % d)

    e = RockPyData(column_names=('F', 'Mx'), row_names=('1.Zeile', '2.Zeile', '3.Zeile'),
                   units=('T', 'mT', 'fT', 'pT'), data=testdata2)

    print('e:\n%s' % e)

    print('e+d:\n%s' % (e+d))
    print('e-d:\n%s' % (e-d))
    print('e/d:\n%s' % (e/d))
    print('e*d:\n%s' % (e*d))

    print('d/e:\n%s' % (d/e))
    print('d*e:\n%s' % (d*e))
    print('d+e:\n%s' % (d+e))
    print('d-e:\n%s' % (d-e))

    print d.units
    # define as many aliases as you want
    d.define_alias('M', ('Mx', 'My', 'Mz'))
    d.define_alias('Mzx', ('Mz', 'Mx'))

    # show some data
    # aliases 'all', 'variable' and 'dep_var' are predefined
    print('all:\n%s' % d['all'])
    print('Mzx:\n%s' % d['Mzx'])

    # lets alter some data
    d['Mx'] = np.array((13, 24, 35))

    # show M with modified Mx component
    print('M:\n%s' % d['M'])
    # show Mx
    print('Mx:\n%s' % d['Mx'])
    # we can also alter several columns at once
    d['M'] = ((2, 3, 4),
              (18, 88, 98),
              (39, 89, 99))
    print('M:\n%s' % d['M'])

    # some math fun
    # calculate magnitude of vector 'M' and save it as new column 'magM'
    d = d.append_columns('magM', d.magnitude('M'))

    # calculate values of 'magM' normalized to 100
    #d.append_columns('normM', d.normalize('magM', 100))

    # we can also add arbitrary data in a new column
    d = d.append_columns(("T",), np.array((1, 2, 3)))

    # we can also add an empty column
    d = d.append_columns(("empty",))

    # renaming a column
    d.rename_column('T', 'temp')

    # show all data again, now including magM and T as the last two columns
    print d

    # do a plot of F vs magM
    # plt.plot(d['F'], d['magM'])
    # plt.show()

    # fancy filtering of data
    tf_array = (d['Mx'].v > 10) & (d['Mx'].v < 20)
    print 'filtering:'
    filtered_d = d.filter(tf_array)
    print filtered_d['Mx']

    # arithmetic operations
    e = deepcopy(d)
    # mutlipy one column with value
    e['Mx'].v *= 2
    # calculate difference of two rockpydata objects
    #c = e - d
    #print c

    #c = e + d
    #print c

    #c = e / d
    #print c

    #c = e * d
    #print c

    #print repr(c)

    # test single line object
    l = RockPyData(column_names=('A', 'B', 'C', 'D'), row_names=('1.Zeile',),
                   units=('T', 'mT', 'fT', 'pT'), data=((1, 2, 3, 4),))
    l = l.append_columns('X', (5,))
    print l

    print l['X']

    #print d.mean()
    print d
    print d + (1, 2, 3, 4, 5, 6)

    print d.interpolate(np.arange(2, 10, .5), includesourcedata=True)
    #d.define_alias('variable', 'Mx')
    #print d.interpolate(np.arange(0, 10, .5))

    print "condense:"
    print condense([d, d*2, d*3], substfunc='median')

if __name__ == '__main__':
    test()