__author__ = 'wack'

from Structure.rockpydata import RockPyData

# script to test data objects

import numpy as np

from copy import deepcopy

def test():
    # define some data for testing
    testdata = ( (1, 2, 3, 4),
                 (5, 6, 7, 8),
                 (9, 10, 11, 12))

    # create a rockpydata object with named columns and filled with testdata
    d = RockPyData(column_names=('F', 'Mx', 'My', 'Mz'), row_names=('1.Zeile','2.Zeile','3.Zeile'), units=('T', 'mT', 'fT', 'pT'), data=testdata)

    print d.units
    # define as many aliases as you want
    d.define_alias('M', ('Mx', 'My', 'Mz'))
    d.define_alias('Mzx', ('Mz', 'Mx'))

    # show some data
    # aliases 'all', 'variable' and 'measurement are predefined
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
    d.append_columns('magM', d.magnitude('M'))

    # calculate values of 'magM' normalized to 100
    d.append_columns('normM', d.normalize('magM', 100))

    # we can also add arbitrary data in a new column
    d.append_columns(("T",), np.array((1, 2, 3)))

    # renaming a column
    d.rename_column('T', 'temp')

    # show all data again, now including magM and T as the last two columns
    print d

    # do a plot of F vs magM
    # plt.plot(d['F'], d['magM'])
    # plt.show()

    # fancy filtering of data
    tf_array = (d['Mx'] > 10) & (d['Mx'] < 20)
    print 'filtering:'
    filtered_d = d.filter(tf_array)
    print filtered_d['Mx']



    # arithmetic operations
    e = deepcopy(d)
    # mutlipy one column with value
    e['Mx'] *= 2
    # calculate difference of two rockpydata objects
    c = e - d
    print c

    c = e + d
    print c

    c = e / d
    print c

    c = e * d
    print c

    print repr(c)

if __name__ is '__main__':
    test()