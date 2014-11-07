__author__ = 'wack'

from copy import deepcopy

import numpy as np
import itertools
from prettytable import PrettyTable

from RockPy.Structure import ureg


def _to_tuple( oneormoreitems):
    '''
    convert argument to tuple of elements
    :param oneormoreitems: single number or string or list of numbers or strings
    :return: tuple of elements
    '''
    return tuple(oneormoreitems) if hasattr(oneormoreitems, '__iter__') else (oneormoreitems, )

class RockPyData(object):
    # todo units
    # todo append rockpydata object rpd(('a','b','c'), (1,2,3)).append(rpd(('a','b'), (1,2)) -> rpd(('a','b','c'), ((1,2,3), (1,2,np.nan))
    """
    class to manage specific numeric data based on a numpy array
    e.g. d = rockpydata( column_names=( 'F','Mx', 'My', 'Mz'))

    internally numeric data is organized as a numpy array with dimensions row x col x 2
    the last dimension holds pairs of value and error estimate

    every column has a unique name and a unit can be assigned

    rows can be labeled as well


    variable naming scheme:
       key: can be column_name and alias
       column_name: only used for single columns
       alias: only used for alias
    """

    def __init__(self, column_names, row_names=None, units=None, data=None):
        """
            :param column_names: sequence of strings naming individual columns
            :param row_names: optional sequence of strings niming individual rows
            :param units:
            :param values: numpy array with values
            :param errors: numpy array with error estimates
        """
        # todo: check dimension of data and the treat as values or values+errors

        if type(column_names) is str:  # if we got a single string, convert it to tuple with one entry
            column_names = (column_names,)

        if type(row_names) is str:  # if we got a single string, convert it to tuple with one entry
            row_names = (row_names,)

        # initialize member variables
        self._column_names = list(column_names)
        # todo: check for right dimension of units
        if units is None:
            self._units = None
        elif isinstance(units, basestring):  # single string
            self._units = [ureg(units), ]
        elif all(isinstance(u, basestring) for u in units):  # list of strings
            self._units = [ureg(u) for u in units]
        else:
            raise RuntimeError('unknown values type for units: %s' % units.__class__)

        self._data = None

        self._update_column_dictionary()

        # define some default aliases
        self._update_all_alias()
        self._define_alias_indices('variable', (0,))
        self._define_alias_indices('values', tuple(range(self.column_count)[1:]))

        data = np.array(data)
        if data.ndim == 2:  # two dimension -> only values
            self.values = data
        elif data.ndim == 3:  # three dimensions -> values + errors
            self.data = data

        if row_names is None:
            self._row_names = None  # don't use row names
        else:
            # make sure that number of row names matches number of lines in values
            if len(row_names) == self.row_count:
                self._row_names = list(row_names)
            else:
                raise RuntimeError(
                    'number of entries in row_names (%d) does not match number of lines in values (%d)' % (
                        len(row_names), self.row_count))

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

    def _update_all_alias(self):
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

    @property  # alias for units
    def u(self):
        return self.units

    @property
    def unitstrs(self):
        if self.units == None:
            return None
        return [str(u.units) for u in self.units]

    @property
    def data(self):
        return self._data

    @property  # alias for data
    def d(self):
        return self.data

    @data.setter
    def data(self, data):
        """
        set values and errors and check if it fits the number of columns
        """
        if data is None:
            self._data = None  # clear existing data
            return

        d = np.array(data, dtype=float)
        if d.ndim != 3:
            raise TypeError('wrong data dimension')

        if d.shape[1] != self.column_count:
            raise TypeError('found %d columns in data but needed %d' % (d.shape[1], self.column_count))

        self._data = d

    @d.setter
    def d(self, data):  # alias for data
        self.data = data

    @property
    def values(self):
        """
        :return: values
        """
        return self.data[:, :, 0].T[0] if self.data.shape[1] == 1 else self.data[:, :, 0]

    @property  # alias for values
    def v(self):
        return self.values

    @values.setter
    def values(self, values):
        """
        set values of data, set errors to nan
        checks whether number of data columns fits array shape

        :param values:
        :return:
        """

        if values is None:
            self._data = None  # clear existing data
            return

        d = np.array(values, dtype=float)
        if d.ndim != 2:
            raise TypeError('wrong data dimension')

        if d.shape[1] != self.column_count:
            raise TypeError('%d columns instead of %d in values' % (d.shape[1], self.column_count))

        d = d[:, :, np.newaxis]
        self._data = np.append(d, np.zeros_like(d), axis=2)
        self.errors = None

    @v.setter
    def v(self, values):  # alias for values
        self.values = values

    @property
    def errors(self):
        return self.data[:, :, 1]

    @property  # alias for errors
    def e(self):
        return self.errors

    @errors.setter
    def errors(self, errors):
        """
        set errors, shape of numpy array must match existing values
        set all entries to np.NAN if errors == None

        :param errors: numerical array of errors
        :return:
        """

        if errors is None or errors == np.NAN:
            self._data[:, :, 1] = np.NAN
        else:
            # todo: check type of errors
            d = np.array(errors)

            if d.shape != self.values.shape:  # check if array shapes match
                raise TypeError('errors has wrong shape %s instead of %s' % (str(d.shape), str(self.values.shape)))

            self._data[:, :, 1] = errors

    @e.setter
    def e(self, errors):  # alias for errors
        self.errors = errors


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
        if len(column_indices) == 0:
            return  # nothing to do
        # check if column indices are in valid range
        if max(column_indices) > self.column_count or min(column_indices) < 0:
            raise IndexError('column indices out of range')
        self._column_dict[alias_name] = tuple(column_indices)

    def append_columns(self, column_names, values=None):
        """
        add values columns to values object
        :param column_names: list(str)
        :param values:
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

        if values is None:
            # if there is no values, create zeros
            values = np.empty((self.row_count, len(column_names)))
            values[:] = np.NAN
        else:
            values = np.array(values, dtype=float)

        # make sure values is 2 dim, even if there is only one number or one column
        if values.ndim == 0:  # single number
            values = values.reshape(1, 1)

        if values.ndim == 1:  # single column
            values = values.reshape(values.shape[0], 1)

        values = values[:, :, np.newaxis]  # add extra dimension for errors
        values = np.concatenate((values, np.zeros_like(values)), axis=2)  # add zeroes in 3rd dimension as errors
        values[:, :, 1] = np.NAN  # set errors to NAN

        # append new values
        self._data = np.concatenate((self._data, values), axis=1)

        # update "all" alias to comprise also the new columns
        self._update_all_alias()


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


    def _convert_input_to_data(self, input):
        '''
        convert given data to 3D numpy array

        :param data:
        :return: 3D numpy array, representing matrix of values and errors as used by RockPyData.data
        '''
        if input is None:
            return None

        # convert input data to a numpy array
        data = np.array(input, dtype=float)

        if data.ndim > 3:
            raise RuntimeError( 'data has dimension > 3')


        if data.ndim == 1:  # values for one row, no errors
            data = data[np.newaxis, :] # add extra dimension to make data 2D with single row

        if data.ndim == 2:  # values for one or multiple rows, no errors
            data = data[:, :, np.newaxis]  # add extra dimension for errors


        # now data must be 3D
        if data.shape[2] == 0 or data.shape[2] > 2:
            raise RuntimeError( 'data.shape[2] must be 1 or 2 and not %d' % data.shape[2])

        if data.shape[2] == 1:  # only values, need to add errors
            data = np.concatenate((data, np.zeros_like(data)), axis=2)  # add zeroes in 3rd dimension as errors
            data[:, :, 1] = np.NAN  # set errors to NAN

        # if data.shape[2] == 2 -> erros are already included in data

        return data

    def append_rows(self, data, row_names=None):
        '''
        append rows with data and optionally row_names
        :param row_names: can be either an 1-3 dim array or anoteher RockPyData object with matching number of columns
        :param data: can be only values or values + errors
        :return:
        '''
        # check if we have another rockpydata object to append
        if isinstance( data, RockPyData):
            row_names = data.row_names
            data = data.data

        # todo: check if column names match????

        if self.row_names is None and row_names is not None and self.row_count > 0:
            raise RuntimeError('cannot append rows with row_names to RockPyData object without row_names')

        if self.row_names is not None and row_names is None:
            raise RuntimeError('cannot append data without row_names to RockPyData object with row_names')

        data = self._convert_input_to_data(data)

        if data is None:
            return self  # do nothing

        if data.shape[1] != self.column_count:  # check if number of data columns match number of columns in rpd object
            raise RuntimeError('column count of data does not match number of columns')

        row_names = _to_tuple( row_names)

        if row_names[0] is not None and data.shape[0] != len( row_names):
            raise RuntimeError('number of rows in data does not match number row names given')

        self_copy = deepcopy(self)

        # todo check if row names are unique
        if row_names is not None:
            self_copy.row_names.extend(row_names) # add one or more row names

        self_copy._data = np.concatenate((self_copy._data, data), axis=0)

        return self_copy

    def delete_rows(self, idx):
        '''
        delete rows specified by idx
        :param idx: single index or list of numeric row indices
        :return: None
        '''
        self_copy = deepcopy( self)
        # delete rows from self_copy._data
        self_copy._data = np.delete( self_copy._data, idx, axis=0)
        # delete corresponding row_names
        if self_copy.row_names is not None:
            for i in sorted( _to_tuple( idx), reverse=True):
                del self_copy.row_names[i]
        return self_copy

    def _find_duplicate_variable_rows(self):
        '''
        find rows with identical variables
        :return: list of arrays with indices of rows with identical variables
        '''

        # create structured array
        a = self['variable'].v
        varrows = np.ascontiguousarray(a).view(np.dtype((np.void,a.dtype.itemsize * (a.shape[1] if a.ndim == 2 else 1))))

        # get unique elements of variable columns
        uar, inv = np.unique(varrows, return_index=False, return_inverse=True)
        # uar: array with unique variables
        # inv: array of indices from uar to reconstruct original array

        # return only elements with more than one entry, i.e. duplicate row indices
        return [tuple(np.where(inv == i)[0]) for i in range(len(uar)) if len(np.where(inv == i)[0]) > 1]

    def eliminate_duplicate_variable_rows(self, subst=None):
        '''
        eliminate rows with non unique variables
        :param subst: determines wich data replaces  the removed non-unique variable rows
                    None: nothing, rows with identical variables are just deleted
                    'max': maximum value of each column
                    'min': minimum value of each column
                    'mean': average value of all values removed values in each row, error is set to the standard deviation
                    'median': median value of all values removed values in each row, error is set to the standard deviation
        :return: ?
        '''

        # find rows with identical variables
        dup = self._find_duplicate_variable_rows()

        self_copy = deepcopy( self)

        for d in dup:
            duprows = self.filter_idx(d)

            if subst is None:
                pass
            elif subst == 'max':
                raise NotImplemented
            elif subst == 'min':
                raise NotImplemented
            elif subst == 'mean':
                res = duprows.mean()
                #print new
                self_copy = self_copy.append_rows( res)
            elif subst == 'median':
                raise NotImplemented
            else:
                raise ValueError('unknown value for subst: %s' % str( subst))

        # delete all rows with identical variable columns
        return self_copy.delete_rows(list(itertools.chain.from_iterable(dup)))


    def interpolate(self, new_variables, method='linear'):
        '''
        interpolate existig data columns to new variables
        ??? how is this done for mutli-column-variables ???
        :param new_variables:
        :param method:
        :return: ?
        '''

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

    def _keyseq2colseq(self, key):
        """
        convert a given list of keys to a list of column indices

        :param keys: can be single string or single int or sequence of those
        :return: tuple of column indices
        """

        colidxs = []
        # check type of key and convert to tuple of column indices
        try:
            if isinstance(key, basestring):  # single string
                colidxs.extend(self.column_dict[key])
            elif isinstance(key, int):  # single int
                if key < self.column_count and key >= 0:
                    colidxs.append(key)
                else:
                    raise KeyError('key is out of range')
            elif all(isinstance(k, basestring) for k in key):  # list of strings
                for k in key:
                    colidxs.extend(self.column_dict[k])
            elif all(isinstance(k, int) for k in key):  # list of ints
                if max(key) < self.column_count and min(key) >= 0:
                    colidxs = key
                else:
                    raise KeyError('at least one key is out of range')
            else:
                raise KeyError('invalid key %s' % str(key))
        except TypeError:
            raise KeyError('invalid key %s' % str(key))

        return colidxs


    def __getitem__(self, key):
        """
        allows access to data columns by index (names)
        accepts single column or sequence of columns
        e.g. data['mass']
        """

        if self._data is None:
            return None
            # todo: return multiple Nones corresponding to alias length

        colidxs = self._keyseq2colseq(key)

        return RockPyData(column_names=self.column_indices_to_names(colidxs),
                          row_names=self.row_names,
                          units=None,
                          data=self.data[:, colidxs])

        # return appropriate columns from self.data numpy array
        # d = self.values[:, self._column_dict[key]]
        # if d.shape[1] == 1:
        #    d = d.T[0]
        #return d

    def __setitem__(self, key, values):
        """
        allows access to data columns by index (names)
        e.g. data['Mx'] = (1,2,3)
        """

        if values is None:
            return

        # check if key is valid
        if key not in self._column_dict:
            raise KeyError('key %s is not a valid column name or alias' % key)

        if not isinstance(values, np.ndarray):
            values = np.array(values)

        # if we have no data, initialize everything to np.NAN with number of lines matching the new data
        if self._data is None:
            try:
                values.shape[0]
            except IndexError:
                values = values.reshape((1,))

            self._data = np.empty((values.shape[0], self.column_count, 2))
            self._data[:] = np.NAN

        # make sure data is 2 dim, even if there is only one column
        if values.ndim == 1:
            values = values.reshape(values.shape[0], 1)

        self._data[:, self._column_dict[key], 0] = values
        self.errors = None

    """
    todo: arithmetic operations
    =====================

    There are several cases to distinguish when doing math with RockPyData objects!

    RockPyData objects can have several variable columns (defined via alias) and several data columns
    Depending on the content of the RockPyData objects arithmetic operations work differently
    Units and errors are propagated when possible


    ROW MATCHING
    If both operands contain a variable (one or many columns) calculation is performed only on
    rows with matching variables. Only those rows are returned.
    If at least one operand does not contain a variable, number of rows must match. Calculations are performed row by row.


    COLUMN MATCHING
    If second operand contains more than one data column calculation is performed only on matching columns
    If second operand contains only one data column, calculation is applied to all columns of first operand


    open questions
    * how are row labels handled?
    * variable columns must be unique to make matching work, better row label matching?
    """


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

        # print '\nrcn', result_c_names, '\nrv', results_variable, '\nrd1', rd1[:,:,0], '\nrd1', rd2[:,:,0]

        # todo: care about errors
        results_data = np.append(results_variable, rd1[:, :, 0] - rd2[:, :, 0],
                                 axis=1)  # variable columns + calculated data columns

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

        # todo: care about errors
        results_data = np.append(results_variable, rd1[:, :, 0] + rd2[:, :, 0],
                                 axis=1)  # variable columns + calculated data columns

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

        # todo: care about errors
        results_data = np.append(results_variable, rd1[:, :, 0] * rd2[:, :, 0],
                                 axis=1)  # variable columns + calculated data columns

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

        # todo: care about errors
        results_data = np.append(results_variable, rd1[:, :, 0] / rd2[:, :, 0],
                                 axis=1)  # variable columns + calculated data columns

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
        d1 = self['variable'].values
        # make sure d1 is 2 dim, even if there is only one column
        if d1.ndim == 1:
            d1 = d1.reshape(d1.shape[0], 1)

        d2 = other['variable'].values
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

        tab = PrettyTable(('row_name',) + tuple(self.column_names))
        for i in range(self.row_count):
            linestrs = tuple(['%s +- %s' % (str(v), str(u)) if not np.isnan(u) else str(v) for (v, u) in self.data[i]])
            if self.row_names is None:
                l = (i,) + linestrs  # if there are no row labels, put numeric index in first column
            else:
                l = (self.row_names[i],) + linestrs  # otherwise put row label in first column
            tab.add_row(l)

        return tab.get_string()

    """ METHODS returning ARRAYS """

    def magnitude(self, key='data'):
        """
        calculate magnitude of vector columns
        return
        * np.array of data
        """

        return np.sum(np.abs(self[key].values) ** 2, axis=-1) ** (1. / 2)

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
        raise NotImplemented

    def differentiate(self):
        raise NotImplemented

    def filter(self, tf_array):
        """
        Returns a copy of the data filtered by rows according to a True_False array. False entries are not returned.

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
            self_copy._row_names = list(
                np.array(self_copy._row_names, dtype=object)[tf_array])  # filter row names with same true/false array
        return self_copy

    def filter_idx(self, index_list, invert=False):
        """
        Returns a copy of the data filtered by rows according to indices specified in index_list.

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
            tf_array = [False if x in index_list else True for x in range(len(self.data))]
        else:
            tf_array = [True if x in index_list else False for x in range(len(self.data))]
        return self.filter(tf_array)

    def mean(self):
        '''
        calculate mean values for each column and return as new RockPyData object
        standard deviations are set as errors
        :return: RockPyData object
        '''
        val = np.nanmean( self.values, axis=0)[np.newaxis, :, np.newaxis]
        err = np.nanstd( self.values, axis=0)[np.newaxis, :, np.newaxis]

        data = np.concatenate((val,err), axis=2)

        if self.row_names is not None:
            row_name = 'mean_' + '_'.join( self.row_names)
        rpd = RockPyData( self.column_names, row_names=row_name, units=self.unitstrs, data=data)
        # todo set variable columns right
        return rpd


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
        self.data = self.data[self.data[idx].argsort()]


    def lin_regress(self, column_name_x, column_name_y):
        """
        calculates a least squares linear regression for given x/y data
        :param column_name_x:
        :param column_name_y:
        :returns : slope, sigma, y_intercept, x_intercept
        """

        x = self[column_name_x].v
        y = self[column_name_y].v

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

        if n <= 2:  # stdev not valid for two points
            sigma = np.nan
        else:
            sigma = np.sqrt((2 * y_sum_diff_sq - 2 * slope * mixed_sum) / ((n - 2) * x_sum_diff_sq))

        y_intercept = y_mean - (slope * x_mean)
        x_intercept = - y_intercept / slope

        return slope, sigma, y_intercept, x_intercept


    def derivative(self, dependent_var, independent_var, smoothing=0):
        """
        calculate d( independent_var) / d( dependent_var)
        :param dependent_var: column name
        :param independent_var: column name
        :return:
        """
        x = self[independent_var].v
        y = self[dependent_var].v

        # aux = [[x[i], (y[i - smoothing] - y[i + smoothing]) / (x[i - smoothing] - x[i + smoothing])] for i in
        #        range(smoothing, len(x) - smoothing)]

        aux = [[(x[i-smoothing]+x[i+1+smoothing])/2., (y[i-smoothing]-y[i+1+smoothing]) / (x[i-smoothing]-x[i+1+smoothing])] for i in range(smoothing, len(x)-1-smoothing)]
        aux = np.array(aux)

        out = RockPyData(column_names=[independent_var, dependent_var],
                         data=aux)
        out.define_alias('d' + dependent_var + '/d' + independent_var, dependent_var)
        return out
