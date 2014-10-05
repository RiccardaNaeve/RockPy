__author__ = 'wack'

import numpy as np
from copy import deepcopy


class rockpydata(object):
    # todo units
    '''
    class to manage specific numeric data based on a numpy array
    e.g. d = rockpydata( column_names=( 'F','Mx', 'My', 'Mz'))

    variable naming guidelines:
       key: can be column_name and alias
       column_name: only used for single columns
       alias: only used for alias
    '''

    def __init__(self, column_names, units=None, data=None):
        '''
            * columns: sequence of strings naming individual columns
        '''

        if type(column_names) is str:  # if we got a single string, convert it to tuple with one entry
            column_names = (column_names,)

        # initialize member variables
        self._column_names = list(column_names)
        self._data = None

        self._update_column_dictionary()

        # define some default aliases
        self._update_all_alias()
        self._column_dict['variable'] = (0,)
        self._column_dict['measurement'] = tuple(range(self.column_count)[1:])

        self['all'] = data

    def _update_column_dictionary(self, column_names=None):
        '''
        update internal _column_dict to assign single column names and aliases to column indices
        * if column_names == None, populate _column_dict with all columns, aliases will be lost
        * if column_names is list of column names (which must already exist in self._column_names), add or update
        those in _column_dict
        e.g. {'Mx': (0,),'My': (1,), 'Mz': (2,), 'Mx': (0,1,2))
        '''

        if type(column_names) is str:  # if we got a single string, convert it to tuple with one entry
            column_names = (column_names,)

        if column_names is None:
            # Python < 2.7
            #self._column_dict = dict((name, (index,)) for (index, name) in enumerate(self._column_names))
            # Python > 2.7
            self._column_dict = { name: (index,) for (index, name) in enumerate(self._column_names)}
        else:
            for n in column_names:  # check if all column_names are valid, i.e. exist in self._column_names
                if not self.column_exists(n):
                    raise IndexError('column %s does not exist' % n)
            for n in column_names:  # add or update each column to _column_dict
                self._column_dict[n] = (self._column_names.index(n),)


    def _update_all_alias(self):  #
        self._column_dict['all'] = tuple(range(self.column_count))

    @property
    def column_names(self):
        return self._column_names


    @property
    def column_count(self):
        return len(self._column_names)

    @property
    def rowcount(self):
        if self.data == None:
            return 0
        else:
            return self.data.shape[0]

    @property
    def column_dict(self):
        return self._column_dict

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        '''
        set data and check if it fits the number of columns
        '''
        if data is None:
            self._data = None  # clear existing data
            return

        d = np.array(data)
        if d.ndim != 2:
            raise TypeError('wrong data dimension')

        if d.shape[1] != self.column_count:
            raise TypeError('wrong number of columns in data')

        self._data = np.array(data)

    def define_alias(self, alias_name, column_names):
        '''
        define an alias for a sequence of existing columns
        e.g. d.definealias( 'M', ('Mx', 'My', 'Mz'))
        '''
        if type(column_names) is str:  # if we got a single string, convert it to tuple with one entry
            column_names = (column_names,)

        if len(column_names) < 1:
            raise TypeError('at least one column name needed')

        for n in column_names:  # check if all column_names are valid, i.e. exist in self._column_names
            if not self.column_exists(n):
                raise IndexError('column %s does not exist' % n)

        # add alias to _column_dict
        self._define_alias_indices(alias_name, tuple(self._column_dict[cn][0] for cn in column_names))

    def _define_alias_indices(self, alias_name, column_indices):
        '''
        define an alias as a sequence of numeric column indices
        '''
        # todo check if column_indices is integer array?
        # check if column indices are in valid range
        if max(column_indices) > self.column_count or min(column_indices) < 0:
            raise IndexError('column indices out of range')
        self._column_dict[alias_name] = tuple(column_indices)

    def append_columns(self, column_names, data=None):
        '''
        add data columns to data object
        column_names: list of strings
        '''
        if type(column_names) is str:  # if we got a single string, convert it to tuple with one entry
            column_names = (column_names,)

        # check if column names are already used as keys (= column names and aliases)
        for n in column_names:
            if self.key_exists(n):
                raise IndexError('column %s already exists' % n)

        # append new column names to the list
        self._column_names.extend(column_names)

        # update internal column dictionary
        self._update_column_dictionary(column_names)

        if data == None:
            # if there is no data, create zeros
            data = np.zeros((self.rowcount, len(column_names)))

        # make sure data is 2 dim, even if there is only one column
        if data.ndim == 1:
            data = data.reshape(data.shape[0], 1)

        # append new data
        self._data = np.concatenate(( self._data, data), axis=1)

        # update "all" alias to comprise also the new columns
        self._update_all_alias()

    def key_exists(self, key):
        '''
        returns true when key is valid
        '''
        return key in self._column_dict

    def column_exists(self, column_name):
        '''
        returns true if named column exists
        '''
        return column_name in self._column_names

    def __getitem__(self, key):
        '''
        allows access to data columns by index (names)
        e.g. data['mass']
        '''
        # check if key is valid
        if not self.key_exists(key):
            raise KeyError('key %s is not a valid column name or alias' % key)

        if self._data is None:
            return None
            # todo: return multiple Nones corresponding to alias length

        # return appropriate columns from self.data numpy array
        d = self._data[:, self._column_dict[key]]
        if d.shape[1] == 1:
            d = d.T[0]
        return d

    def __setitem__(self, key, data):
        '''
        allows access to data columns by index (names)
        e.g. data['Mx'] = (1,2,3)
        '''

        if data is None:
            return

        # check if key is valid
        if key not in self._column_dict:
            raise KeyError('key %s is not a valid column name or alias' % key)

        if not isinstance(data, np.ndarray):
            data = np.array(data)

        # if we have no data, initialize everything to zero with number of lines matching the new data
        if self._data == None:
            try:
                data.shape[0]
            except IndexError:
                data = data.reshape((1,))

            self._data = np.zeros((data.shape[0], self.column_count))

        # make sure data is 2 dim, even if there is only one column
        if data.ndim == 1:
            data = data.reshape(data.shape[0], 1)

        self._data[:, self._column_dict[key]] = data


    def magnitude(self, key='measurement'):
        '''
        calculate magnitude of vector columns
        return
        * np.array of data
        '''

        return np.sum(np.abs(self[key]) ** 2, axis=-1) ** (1. / 2)

    def normalize(self, column_name, value=1.0):
        '''
        return column data normalized to given value
        e.g. d.normalize('X', 100)
        '''
        if not self.column_exists(column_name):
            raise IndexError
        d = self[column_name]
        return d / np.max(d) * value


    def differentiate(self):
        raise NotImplemented

    def filter(self, tf_array):
        '''
        Returns a copy of the data filtered according to a True_False array. False entries are not returned.

        tf_array = (d['Mx'] > 10) & (d['Mx'] < 20)
        filtered_d = d.filter(tf_array)

        :param column_name:
        :param tf_array: array_like
                       array with True/False values
        :return: rockpydata
        '''
        self_copy = deepcopy(self)

        if not isinstance(tf_array, np.ndarray):
            tf_array = np.array(tf_array).T

        self_copy._data = self_copy._data[tf_array]
        return self_copy

    def filter_idx(self, index_list):
        '''
        Returns a copy of the data filtered according to indices specified in index_list

        :example:

        .. code-block:: python

           idx_list = [3,5,7,8]
           data = rp.rockpydata(column_names=['testdata'], data=[0,1,2,3,4,5,6,7,8,9,10])
           filtered_data = data.filter_idx(idx_list)
           filtered_data['testdata']
           array([ 3.,  5.,  7.,  8.])

        :param index_list:
        :return: rockpydata
               filtered data
        '''

        tf_array = [True if x in index_list else False for x in range(len(self['measurement']))]
        return self.filter(tf_array)

    def check_duplicate(self):
        #todo look for duplicate entries e.g Temp
        raise NotImplemented

    def sort(self, key='variable'):
        '''
        sorting all data according to one column_name or alias
        e.g.

        .. code-block:: python

           d = data(column_names=('Temp','M'), data=[[10, 1.3],[30, 2.2],[20, 1.5]])
           d.sort('Temp')
           d.data
           array([[ 10. ,   1.3],
           [ 20. ,   1.5],
           [ 30. ,   2.2]])

        :param key: str
                  column_name to be sorted for
        '''
        idx = self.column_dict[key][0]
        self.data = self.data[self.data[:, idx].argsort()]

    def rename_column(self, old_key, new_key):
        '''
        renames a column according to specified key

        .. code-block:: python

           d = data(column_names=('Temp','M'), data=[[10, 1.3],[30, 2.2],[20, 1.5]])
           d.rename_column('Temp', 't')
           d.column_names
           ['t', 'M']

        :param old_key: str
        :param new_key: str
        '''
        try:
            idx = self._column_names.index(old_key)
            self._column_names[idx] = new_key
            self._update_column_dictionary(self._column_names)
        except ValueError:
            print 'Key << %s >> does not exist' %(old_key)



    def lin_regress(self, column_name_x, column_name_y):
        """
        calculates a least squares linear regression for given x/y data
        :param column_name_x:
        :param column_name_y:
        """

        x = self[column_name_x]
        y = self[column_name_y]

        if len(x) < 2 or len(y) < 2:
            return None

        ''' calculate averages '''
        x_mean = np.mean(x)
        y_mean = np.mean(y)

        ''' calculate differences '''
        x_diff = x - x_mean
        y_diff = y - y_mean

        ''' square differences '''
        x_diff_sq = x_diff ** 2
        y_diff_sq = y_diff ** 2

        ''' sum squared differences '''
        x_sum_diff_sq = np.sum(x_diff_sq)
        y_sum_diff_sq = np.sum(y_diff_sq)

        mixed_sum = np.sum(x_diff * y_diff)
        ''' calculate slopes '''
        N = len(x)

        slope = np.sqrt(y_sum_diff_sq / x_sum_diff_sq) * np.sign(mixed_sum)

        sigma = np.sqrt((2 * y_sum_diff_sq - 2 * slope * mixed_sum) / ((N - 2) * x_sum_diff_sq))

        y_intercept = y_mean + abs(slope * x_mean)
        x_intercept = - y_intercept / slope

        return slope, sigma, y_intercept, x_intercept

    def minus_equal_var(self, other, variable):
        self_copy = deepcopy(self)
