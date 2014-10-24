__author__ = 'wack'

from copy import deepcopy

import numpy as np
from prettytable import PrettyTable

from Structure import ureg

class RockPyData(object):
    # todo units
    # todo append rockpydata object rpd(('a','b','c'), (1,2,3)).append(rpd(('a','b'), (1,2)) -> rpd(('a','b','c'), ((1,2,3), (1,2,np.nan))
    # todo make columns not computable rpd(('a','b','c'), (1,2,3)).not_computable('b') + rpd(('a','b','c'), (4,5,6)) = a=5,b=2,c=9 ??? normalizing a95 for example does not make much sense, right?
    """
    class to manage specific numeric data based on a numpy array
    e.g. d = rockpydata( column_names=( 'F','Mx', 'My', 'Mz'))

    variable naming guidelines:
       key: can be column_name and alias
       column_name: only used for single columns
       alias: only used for alias
    """

    def __init__(self, column_names, row_names=None, units=None, data=None):
        """
            :param column_names: sequence of strings naming individual columns
            :param row_names: optional sequence of strings niming individual rows
            :param units:
            :param data
        """

        if type(column_names) is str:  # if we got a single string, convert it to tuple with one entry
            column_names = (column_names,)

        if type(row_names) is str:  # if we got a single string, convert it to tuple with one entry
            row_names = (row_names,)

        # initialize member variables
        self._column_names = list(column_names)

        #  todo: check for right dimension of units
        if units is None:
            self._units = None
        elif isinstance(units, basestring): # single string
            self._units = [ureg(units),]
        elif all(isinstance(u, basestring) for u in units): # list of strings
            self._units = [ureg(u) for u in units]
        else:
            raise RuntimeError('unknown data type for units: %s' % units.__class__)




        self._data = None

        self._update_column_dictionary()

        # define some default aliases
        self._update_all_alias()
        self._column_dict['variable'] = (0,)
        self._column_dict['data'] = tuple(range(self.column_count)[1:])

        self['all'] = data

        if row_names is None:
            self._row_names = None # don't use row names
        else:
            # make sure that number of row names matches number of lines in data
            if len(row_names) == self.row_count:
                self._row_names = list(row_names)
            else:
                raise RuntimeError('number of entries in row_names (%d) does not match number of lines in data (%d)'%(len(row_names),self.row_count))

    def _update_column_dictionary(self, column_names=None):
        """
        update internal _column_dict to assign single column names and aliases to column indices
        * if column_names == None, populate _column_dict with all columns, aliases will be lost
        * if column_names is list of column names (which must already exist in self._column_names), add or update
        those in _column_dict
        e.g. {'Mx': (0,),'My': (1,), 'Mz': (2,), 'Mx': (0,1,2))
        """

        if type(column_names) is str:  # if we got a single string, convert it to tuple with one entry
            column_names = (column_names,)

        if column_names is None:
            # Python < 2.7
            # self._column_dict = dict((name, (index,)) for (index, name) in enumerate(self._column_names))
            # Python > 2.7
            self._column_dict = {name: (index,) for (index, name) in enumerate(self._column_names)}
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
    def row_names(self):
        return self._row_names


    @property
    def column_count(self):
        return len(self._column_names)

    @property
    def row_count(self):
        if self.data is None:
            return 0
        else:
            return self.data.shape[0]

    @property
    def column_dict(self):
        return self._column_dict

    @property
    def units(self):
        return self._units

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        """
        set data and check if it fits the number of columns
        """
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
        """
        define an alias for a sequence of existing columns
        e.g. d.definealias( 'M', ('Mx', 'My', 'Mz'))
        """
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
        """
        define an alias as a sequence of numeric column indices
        """
        # todo check if column_indices is integer array?
        # check if column indices are in valid range
        if max(column_indices) > self.column_count or min(column_indices) < 0:
            raise IndexError('column indices out of range')
        self._column_dict[alias_name] = tuple(column_indices)

    def append_columns(self, column_names, data=None):
        """
        add data columns to data object
        :param column_names: list(str)
        :param data: 
        """
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

        if data is None:
            # if there is no data, create zeros
            data = np.zeros((self.row_count, len(column_names)))

        # make sure data is 2 dim, even if there is only one column
        # todo BUGFIX!!! if adding a single column with float:     ERROR:: if data.ndim == 1: \\ AttributeError: 'float' object has no attribute 'ndim'
        if data.ndim == 1:
            data = data.reshape(data.shape[0], 1)

        # append new data
        self._data = np.concatenate(( self._data, data), axis=1)

        # update "all" alias to comprise also the new columns
        self._update_all_alias()

    def key_exists(self, key):
        """
        returns true when key is valid

        >>> a = RockPyData(('A','B')); a.key_exists('A'), a.key_exists('B'), a.key_exists('C')
        (True, True, False)
        """
        return key in self._column_dict

    def column_exists(self, column_name):
        """
        returns true if named column exists
        """
        return column_name in self._column_names

    def column_indices_to_names(self, c_indices):
        """
        get column names for given indices

        :param c_indices: list of indices

        :return list of strings
        """
        return [self.column_names[i] for i in c_indices]

    def column_names_from_key(self, key):
        """
        get column names for given key

        :param key: string

        :return list of strings
        """
        return self.column_indices_to_names(self.column_dict[key])

    def __getitem__(self, key):
        """
        allows access to data columns by index (names)
        e.g. data['mass']
        """
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
        """
        allows access to data columns by index (names)
        e.g. data['Mx'] = (1,2,3)
        """

        if data is None:
            return

        # check if key is valid
        if key not in self._column_dict:
            raise KeyError('key %s is not a valid column name or alias' % key)

        if not isinstance(data, np.ndarray):
            data = np.array(data)

        # if we have no data, initialize everything to zero with number of lines matching the new data
        if self._data is None:
            try:
                data.shape[0]
            except IndexError:
                data = data.reshape((1,))

            self._data = np.zeros((data.shape[0], self.column_count))

        # make sure data is 2 dim, even if there is only one column
        if data.ndim == 1:
            data = data.reshape(data.shape[0], 1)

        self._data[:, self._column_dict[key]] = data

    def __sub__(self, other):
        """
        subtract operator
        subtracts other rockpydata object

        .. code-block:: python

           A = B - C

        :param other: rockpydata
        """

        # build and return a new rockpydata object containing the variable columns and matching remaining columns with
        # the calculated data

        result_c_names, results_variable, rd1, rd2 = self._get_arithmetic_data(other)

        results_data = np.append(results_variable, rd1 - rd2, axis=1)  # variable columns + calculated data columns

        return RockPyData(column_names=result_c_names, row_names=self.row_names, units=None, data=results_data)

    def __add__(self, other):
        """
        addition operator
        add other rockpydata object

        .. code-block:: python

           A = B + C

        :param other: rockpydata
        """

        # build and return a new rockpydata object containing the variable columns and matching remaining columns with
        # the calculated data

        result_c_names, results_variable, rd1, rd2 = self._get_arithmetic_data(other)

        results_data = np.append(results_variable, rd1 + rd2, axis=1)  # variable columns + calculated data columns

        return RockPyData(column_names=result_c_names, row_names=self.row_names, data=results_data)

    def __mul__(self, other):
        """
        subtract operator
        subtracts other rockpydata object

        .. code-block:: python

           A = B - C

        :param other: rockpydata
        """

        # build and return a new rockpydata object containing the variable columns and matching remaining columns with
        # the calculated data

        result_c_names, results_variable, rd1, rd2 = self._get_arithmetic_data(other)

        results_data = np.append(results_variable, rd1 * rd2, axis=1)  # variable columns + calculated data columns

        return RockPyData(column_names=result_c_names, row_names=self.row_names, data=results_data)

    def __div__(self, other):
        """
        subtract operator
        subtracts other rockpydata object

        .. code-block:: python

           A = B/C

        :param other: rockpydata
        """

        # build and return a new rockpydata object containing the variable columns and matching remaining columns with
        # the calculated data

        result_c_names, results_variable, rd1, rd2 = self._get_arithmetic_data(other)

        results_data = np.append(results_variable, rd1 / rd2, axis=1)  # variable columns + calculated data columns

        return RockPyData(column_names=result_c_names, row_names=self.row_names, data=results_data)

    def _get_arithmetic_data(self, other):
        """
        looks for matching entries in the 'variable' aliased columns and for matching data columns
        this is needed to prepare an arithmetic operation of two rockpydata objects


        :param other: rockpydata
        :return
        """
        # check if we have a proper rockpydata object for arithmetic operation

        if not isinstance(other, RockPyData):  # todo implement for floats
            raise ArithmeticError('only rockpydata objects can be computed')

        # check if 'variable' columns match in both objects
        if not (self.key_exists('variable') and other.key_exists('variable')):
            raise ArithmeticError("alias 'variable' not known")

        # check if 'variable' columns match
        if not sorted(self.column_names_from_key('variable')) == sorted(other.column_names_from_key('variable')):
            raise ArithmeticError("'variable' columns do not match")

        # check if remaining columns for matching pairs, only those will be subtracted and returned
        cnames1 = self.column_indices_to_names(set(range(self.column_count)) - set(self.column_dict['variable']))
        cnames2 = other.column_indices_to_names(set(range(other.column_count)) - set(other.column_dict['variable']))

        # get intersection of name sets
        matching_cnames = set(cnames1) & set(cnames2)

        # get indices of matching column names
        mcidx = np.array([(self.column_names.index(n), other.column_names.index(n)) for n in matching_cnames])

        # get indices of matching 'variable' values
        d1 = self['variable']
        # make sure d1 is 2 dim, even if there is only one column
        if d1.ndim == 1:
            d1 = d1.reshape(d1.shape[0], 1)

        d2 = other['variable']
        # make sure d1 is 2 dim, even if there is only one column
        if d2.ndim == 1:
            d2 = d2.reshape(d2.shape[0], 1)
        mridx = np.array(np.all((d1[:, None, :] == d2[None, :, :]), axis=-1).nonzero()).T
        # todo: check if matching rows are unique !!!

        result_c_names = self.column_names_from_key('variable') + self.column_indices_to_names(mcidx[:, 0])
        results_variable = d1[mridx[:, 0],
                           :]  # all columns of variable but only those lines which match in both rockpydata objects

        # data for calculation of both objects with reordered columns according to mcidx
        rd1 = self.data[mridx[:, 0], :][:, mcidx[:, 0]]
        rd2 = other.data[mridx[:, 1], :][:, mcidx[:, 1]]

        return result_c_names, results_variable, rd1, rd2

    def __repr__(self):
        """
        get useful representation for debugging
        :return:
        """
        return "rockpydata, %d rows in %d columns (%s)" % (
            self.row_count, self.column_count, ','.join(self.column_names))

    def __str__(self):
        """
        get readable representation of the data
        :return:
        """

        tab = PrettyTable(('row_name',)+tuple(self.column_names))
        for i in range(self.row_count):
            if self.row_names is None:
                l = (i,) + tuple(self.data[i]) # if there are no row labels, put numeric index in first column
            else:
                l = (self.row_names[i],) + tuple(self.data[i]) # otherwise put row label in first column
            tab.add_row(l)

        return tab.get_string()

    """ METHODS returning ARRAYS """

    def magnitude(self, key='data'):
        """
        calculate magnitude of vector columns
        return
        * np.array of data
        """

        return np.sum(np.abs(self[key]) ** 2, axis=-1) ** (1. / 2)

    def normalize(self, column_name, value=1.0):
        """
        return column data normalized to given value
        e.g. d.normalize('X', 100)
        """
        if not self.column_exists(column_name):
            raise IndexError
        d = self[column_name]
        return d / np.max(d) * value

    """ METHODS returning OBJECTS """

    def running_ave(self):
        pass

    def differentiate(self):
        raise NotImplemented

    def filter(self, tf_array):
        """
        Returns a copy of the data filtered according to a True_False array. False entries are not returned.

        tf_array = (d['Mx'] > 10) & (d['Mx'] < 20)
        filtered_d = d.filter(tf_array)

        :param column_name:
        :param tf_array: array_like
                       array with True/False values
        :return: rockpydata
        """
        self_copy = deepcopy(self)

        if not isinstance(tf_array, np.ndarray):
            tf_array = np.array(tf_array).T

        self_copy._data = self_copy._data[tf_array]
        if self_copy._row_names is not None:
            self_copy._row_names = list(np.array(self_copy._row_names, dtype=object)[tf_array]) # filter row names with same true/false array
        return self_copy

    def filter_idx(self, index_list, invert=False):
        """
        Returns a copy of the data filtered according to indices specified in index_list.

        :example:

        .. code-block:: python

           idx_list = [3,5,7,8]
           data = rp.rockpydata(column_names=['testdata'], data=[0,1,2,3,4,5,6,7,8,9,10])
           filtered_data = data.filter_idx(idx_list)
           filtered_data['testdata']
           array([ 3.,  5.,  7.,  8.])

        if invert is True, the specified index will be deleted

        .. code-block:: python

           idx_list = [3,5,7,8]
           data = rp.rockpydata(column_names=['testdata'], data=[0,1,2,3,4,5,6,7,8,9,10])
           filtered_data = data.filter_idx(idx_list)
           filtered_data['testdata']
           array([ 1.,  2.,  3.,  4.,  6.,  9.,  10.])

        :param index_list:
        :return: rockpydata
               filtered data
        """
        if invert:
            tf_array = [False if x in index_list else True for x in range(len(self['data']))]
        else:
            tf_array = [True if x in index_list else False for x in range(len(self['data']))]
        return self.filter(tf_array)

    def check_duplicate(self):
        # todo look for duplicate entries e.g Temp
        raise NotImplemented

    def sort(self, key='variable'):
        """
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
        """
        idx = self.column_dict[key][0]
        self.data = self.data[self.data[:, idx].argsort()]

    def rename_column(self, old_cname, new_cname):
        """
        renames a column according to specified key

        .. code-block:: python

           d = data(column_names=('Temp','M'), data=[[10, 1.3],[30, 2.2],[20, 1.5]])
           d.rename_column('Temp', 't')
           d.column_names
           ['t', 'M']

        :param old_key: str
        :param new_key: str
        """

        if self.column_exists(new_cname):
            raise KeyError('Column %s already exists.' % new_cname)
        if not self.column_exists(old_cname):
            raise KeyError('Column %s does not exist.' % old_cname)

        idx = self._column_names.index(old_cname)
        self._column_names[idx] = new_cname
        self._update_column_dictionary(self._column_names)


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

        """ calculate averages """
        x_mean = np.mean(x)
        y_mean = np.mean(y)

        """ calculate differences """
        x_diff = x - x_mean
        y_diff = y - y_mean

        """ square differences """
        x_diff_sq = x_diff ** 2
        y_diff_sq = y_diff ** 2

        """ sum squared differences """
        x_sum_diff_sq = np.sum(x_diff_sq)
        y_sum_diff_sq = np.sum(y_diff_sq)

        mixed_sum = np.sum(x_diff * y_diff)
        """ calculate slopes """
        n = len(x)

        slope = np.sqrt(y_sum_diff_sq / x_sum_diff_sq) * np.sign(mixed_sum)

        if n <= 2: # stdev not valid for two points
            sigma = np.nan
        else:
            sigma = np.sqrt((2 * y_sum_diff_sq - 2 * slope * mixed_sum) / ((n - 2) * x_sum_diff_sq))

        y_intercept = y_mean + abs(slope * x_mean)
        x_intercept = - y_intercept / slope

        return slope, sigma, y_intercept, x_intercept


#if __name__ == "__main__":
#    import doctest
#    doctest.testmod()