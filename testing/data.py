__author__ = 'wack'

# script to test data objects

import Structure.rockpydata
import numpy as np
import matplotlib.pyplot as plt

testdata = ( (1, 2, 3, 4),
             (5, 6, 7, 8),
             (9, 10, 11, 12))

d = Structure.rockpydata.rockpydata( column_names=( 'F','Mx', 'My', 'Mz'), data = testdata)
d.definealias( 'M', ( 'Mx', 'My', 'Mz'))

d['Mx'] = np.array((11,55,99))

print( d['M'])

d['M'] = np.array((( 77,87,97),(78,88,98),(79,89,99)))

print( d['M'])

print d.magnitude( 'M')

#d.magnitude( column_name = 'M', result_column = 'magM')

d.append_columns( ('magM',), d.magnitude( 'M'))

print( d['magM'])

d.append_columns( ("T",), np.array((1,2,3)))
print d["all"]

# do a plot of magnitude M vs F
plt.plot( d['F'], d.magnitude('M'))
plt.show()