__author__ = 'wack'

# script to test data objects

import Structure.rockpydata
import numpy as np
import matplotlib.pyplot as plt


# define some data for testing
testdata = ( (1, 2, 3, 4),
             (5, 6, 7, 8),
             (9, 10, 11, 12))

# create a rockpydata object with named columns and filled with testdata
d = Structure.rockpydata.rockpydata(column_names=( 'F', 'Mx', 'My', 'Mz'), data=testdata)

# define as many aliases as you want
d.definealias('M', ( 'Mx', 'My', 'Mz'))
d.definealias('Mzx', ( 'Mz', 'Mx'))

# show some data
# aliases 'all', 'variable' and 'measurement are predefined
print( 'all:\n%s' % d['all'])
print( 'Mzx:\n%s' % d['Mzx'])

# lets alter some data
d['Mx'] = np.array((13, 24, 35))

# show M with modified Mx component
print( 'M:\n%s' % d['M'])

# we can also alter several columns at once
d['M'] = ((2, 3, 4),
          (18, 88, 98),
          (39, 89, 99))
print( 'M:\n%s' % d['M'])

# some math fun
# calculate magnitude of vector 'M' and save it as new column 'magM'
d.append_columns('magM', d.magnitude('M'))

# we can also add arbitrary data in a new column
d.append_columns(("T",), np.array((1, 2, 3)))

# show all data again, now including magM and T as the last two columns
print( 'all:\n%s' % d['all'])

# do a plot of F vs magM
plt.plot(d['F'], d['magM'])
plt.show()