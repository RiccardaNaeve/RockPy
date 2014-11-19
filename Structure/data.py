__author__ = 'wack'

from copy import deepcopy

import logging
import numpy as np
import scipy
import scipy.interpolate
import itertools
import re  # regular expressions
from prettytable import PrettyTable

from RockPy.Structure import ureg
from RockPy.Functions import general

general.create_logger(__name__)
log = logging.getLogger(__name__)

def _to_tuple( oneormoreitems):
    '''
    convert argument to tuple of elements
    :param oneormoreitems: single number or string or list of numbers or strings
    :return: tuple of elements
    '''
    return tuple(oneormoreitems) if hasattr(oneormoreitems, '__iter__') else (oneormoreitems, )

class RockPyData(object):
    # todo units
    """
    class to manage specific numeric data based on a numpy array
    e.g. d = rockpydata( column_names=( 'F','Mx', 'My', 'Mz'))

    internally numeric data is organized as a numpy array with dimensions row x col x 2
    the last dimension holds pairs of value and error estimate

    every column has a unique name and a unit can be assigned

    rows can be labeled as well


    column variable naming scheme:
       key: can be column_name and alias
       column_name: only used for single columns
       alias: only used for alias
    """

    @staticmethod
    def _convert_to_2D(input, column=False):
        '''
        convert given input to 2D numpy array
        :param input: array data consisting of values or errors
        :param column: if FALSE -> 1D data is treated as a single row, otherwise as single column
        :return: 2D numpy array, representing matrix of values or errors as used by RockPyData.data
        '''
        # convert input data to a numpy array
        data = np.array(input, dtype=float)

        if data.ndim > 2:
            raise RuntimeError('data has dimension > 2')

        if data.ndim == 0:  # single number
            data = data[np.newaxis]  # convert to 1D array
        if data.ndim == 1:  # values for one row or column, no errors
            if not column:
                data = data[np.newaxis, :]  # add extra dimension to make data 2D with single row
            else:
                data = data[:, np.newaxis]  # single column data

        return data


    @staticmethod
    def _convert_to_data3D(input, column=False):
        '''
        convert given data to 3D numpy array
        :param input: array data consisting of values (and errors)
        :param column: if FALSE -> 1D data is treated as a single row, otherwise as single column
        :return: 3D numpy array, representing matrix of values and errors as used by RockPyData.data
        '''
        if input is None:
            return None

        # convert input data to a numpy array
        data = np.array(input, dtype=float)

        if data.ndim > 3:
            raise RuntimeError('data has dimension > 3')

        if data.ndim <= 1:  # values for one row or column, no errors
            data = RockPyData._convert_to_2D(data, column=column)

        if data.ndim == 2:  # values for one or multiple rows or columns, no errors
            data = data[:, :, np.newaxis]  # add extra dimension for errors

        # now data must be 3D
        if data.shape[2] == 0 or data.shape[2] > 2:
            raise RuntimeError('data.shape[2] must be 1 or 2 and not %d' % data.shape[2])

        if data.shape[2] == 1:  # only values, need to add errors
            data = np.concatenate((data, np.zeros_like(data)), axis=2)  # add zeroes in 3rd dimension as errors
            data[:, :, 1] = np.NAN  # set errors to NAN

        # if data.shape[2] == 2 -> errors are already included in data

        return data

    def __init__(self, column_names, row_names=None, units=None, data=None):
        """
            :param column_names: sequence of strings naming individual columns
            :param row_names: optional sequence of strings niming individual rows
            :param units:
            :param values: numpy array with values
            :param errors: numpy array with error estimates
        """
        #log.info( 'Creating new ' + type(self).__name__)

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
        self._define_alias_indices('variable', 0)

        self.data = RockPyData._convert_to_data3D( data)

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

        if column_names is None:
            # Python < 2.7
            # self._column_dict = dict((name, (index,)) for (index, name) in enumerate(self._column_names))
            # Python > 2.7
            self._column_dict = {name: (index,) for (index, name) in enumerate(self._column_names)}
        else:
            column_names = _to_tuple(column_names)
            for n in column_names:  # check if all column_names are valid, i.e. exist in self._column_names
                if not self.column_exists(n):
                    raise IndexError('column %s does not exist' % n)
            for n in column_names:  # add or update each column to _column_dict
                self._column_dict[n] = (self._column_names.index(n),)

    def _update_all_alias(self):
        '''
        update 'all' alias to comprise all columns
        :return: None
        '''
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
        '''
        get numeric values (without errors)
        :return: 2D numpy array of values
        '''
        return self.data[:, :, 0] # always return 2D data

    @property  # alias for values
    def v(self):
        '''
        get numeric values (without errors)
        :return: return self.values if more than one column, otherwise self.values.T[0]
        '''
        return self.values.T[0] if self.data.shape[1] == 1 else self.values

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

        d = RockPyData._convert_to_2D(values, column=True)

        if d.ndim != 2:
            raise TypeError('wrong data dimension (%d)' % d.ndim)

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
        '''
        get numeric errors (no values)
        :return: 2D numpy array of erros
        '''
        return self.data[:, :, 1]

    @property  # alias for errors
    def e(self):
        '''
        get numeric errors
        :return: return self.errors if more than one column, otherwise self.errors.T[0]
        '''
        return self.errors.T[0] if self.data.shape[1] == 1 else self.errors

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
        if alias 'variable' is redefined, automatically updates 'dep_var' alias to all other columns
        :param alias_name: str
        :param column_indices: single or list of column indices
        :return: None
        """
        column_indices = _to_tuple(column_indices)

        # todo check if column_indices is integer array?
        if len(column_indices) == 0:
            return  # nothing to do
        # check if column indices are in valid range
        if max(column_indices) > self.column_count or min(column_indices) < 0:
            raise IndexError('column indices out of range')
        self._column_dict[alias_name] = tuple(column_indices)

        # if alias 'variable' was redefined, automatically update 'dep_var' alias to all other columns
        if alias_name == 'variable':
            self._column_dict['dep_var'] = [i for i in range(self.column_count) if i not in self._keyseq2colseq('variable')]

    def append_columns(self, column_names, data=None):
        """
        add one or more columns to values object
        :param column_names: list(str)
        :param data: array fo values (and errors) for the new columns
        :return: new RockPyData object with appended data
        """

        column_names = _to_tuple(column_names)

        # check if column names are already used as keys (= column names and aliases)
        for n in column_names:
            if self.key_exists(n):
                raise IndexError('column %s already exists' % n)

        self_copy = deepcopy( self)

        # append new column names to the list
        self_copy._column_names.extend(column_names)

        # update internal column dictionary
        self_copy._update_column_dictionary(column_names)


        if data is None:
            # if there are no data, fill with NAN
            data = np.empty((self_copy.row_count, len(column_names)))
            data[:] = np.NAN

        data = RockPyData._convert_to_data3D(data, column=True)

        # append new values
        self_copy._data = np.concatenate((self_copy._data, data), axis=1)

        # update "all" alias to comprise also the new columns
        self_copy._update_all_alias()

        # update 'variable' and 'dep_var' aliases
        self_copy._define_alias_indices('variable', self.column_dict['variable'])

        return self_copy

    def rename_column(self, old_cname, new_cname):
        '''
        renames a column according to specified key

        .. code-block:: python

           d = data(column_names=('Temp','M'), data=[[10, 1.3],[30, 2.2],[20, 1.5]])
           d.rename_column('Temp', 't')
           d.column_names
           ['t', 'M']

        :param old_key: str
        :param new_key: str
        :return: None
        '''

        if self.column_exists(new_cname):
            raise KeyError('Column %s already exists.' % new_cname)
        if not self.column_exists(old_cname):
            raise KeyError('Column %s does not exist.' % old_cname)

        idx = self._column_names.index(old_cname)
        self._column_names[idx] = new_cname
        self._update_column_dictionary(self._column_names)

    def append_rows(self, data, row_names=None, ignore_row_names=False):
        '''
        append rows with data and optionally row_names
        :param data: can be either an 1-3 dim array or another RockPyData object with matching number of columns
        :param row_names: one or multiple row names matching the number of data rows. if data is another
                            RockPyData object, row labels will be taken from that
        :param ignore_row_names: if true, no row names will be appended in any case
        :return:
        '''
        # check if we have another RockPyData object to append
        if isinstance(data, RockPyData):
            row_names = data.row_names
            data = data.data

        # todo: check if column names match????

        if ignore_row_names:
            row_names = None

        if self.row_names is None and row_names is not None and self.row_count > 0:
            raise RuntimeError('cannot append rows with row_names to RockPyData object without row_names')

        if self.row_names is not None and row_names is None:
            raise RuntimeError('cannot append data without row_names to RockPyData object with row_names')

        data = RockPyData._convert_to_data3D(data)

        if data is None:
            return self  # do nothing

        if data.shape[1] != self.column_count:  # check if number of data columns match number of columns in rpd object
            raise RuntimeError('column count (%i) of data does not match number of columns (%s)' % (data.shape[1], self.column_count))

        row_names = _to_tuple(row_names)

        if row_names[0] is not None and data.shape[0] != len(row_names):
            raise RuntimeError('number of rows in data does not match number row names given')

        self_copy = deepcopy(self)

        # todo check if row names are unique
        if row_names[0] is not None:
            self_copy.row_names.extend(row_names)  # add one or more row names

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

    def eliminate_duplicate_variable_rows(self, substfunc=None):
        '''
        eliminate rows with non unique variables
        :param substfunc: deleted rows will be replaced by the result of this function
                    None: nothing, rows with identical variables are just deleted
                    'max': maximum value of each column
                    'min': minimum value of each column
                    'mean': average value of all values removed values in each row, error is set to the standard deviation
                    'median': median value of all values removed values in each row, error is set to the standard deviation
                    'fist', 'last': first or last row with same variable
        :return: returns modified copy of RockPyData object
        '''

        # find rows with identical variables
        dup = self._find_duplicate_variable_rows()

        self_copy = deepcopy(self)

        for d in dup:
            duprows = self.filter_idx(d)

            if substfunc is not None:
                res = duprows.__getattribute__(substfunc)()
                self_copy = self_copy.append_rows(res)

        # delete all rows with identical variable columns
        return self_copy.delete_rows(list(itertools.chain.from_iterable(dup)))

    def interpolate(self, new_variables, method='interp1d', kind=None, substdupvarfunc='mean', includesourcedata=False):
        '''
        interpolate existing data columns to new variables
        first duplicated variables are averaged to make interpolation unique
        :param new_variables: one or multiple values for which the data columns will be interpolated
        :param method: defines interpolation method
            'inter1d' works with single variable column only, uses scipy.interpolate.inter1p
        :param kind: defines which kind of interpolation is done
            for 'inter1d' this defaults to linear, other possible options: 'nearest', 'zero', 'slinear', 'quadratic', 'cubic'
        :param substdupvarfunc: substfunc for eliminated duplicated rows
        :param includesourcedata: if true, source data points within interpolation range will be included in result
        :return: new RockPyData object with the interpolated data
        '''

        # average away duplicated variable rows and sort by variable
        rpd_copy = self.eliminate_duplicate_variable_rows(substfunc=substdupvarfunc).sort()

        if method == 'interp1d':
            if len(rpd_copy.column_dict['variable']) != 1:
                raise RuntimeError('%s works only with single column variables' % method)
            newv = _to_tuple(new_variables)
            oldv = rpd_copy['variable'].v
            log.info('INTERPOLATING to new variables (interp1d)')

            # get function to interpolate all columns
            ipf = scipy.interpolate.interp1d(oldv, rpd_copy['dep_var'].values.T, kind=kind if kind is not None else 'linear', bounds_error=False, axis=1)

            # calculate interpolated values for all dep_var columns
            interp_values = ipf(newv).T

            # put everything back together in new RockPyData object
            rpd_copy.cleardata()
            rpd_copy['variable'] = newv
            rpd_copy['dep_var'] = interp_values

            if includesourcedata:
                # works only with single column variable!
                srcdata = self.filter((self['variable'].v >= min(newv)) & (self['variable'].v <= max(newv)))
                rpd_copy = rpd_copy.append_rows(srcdata, ignore_row_names=True)  # append original data to interpolated data

            return rpd_copy

        else:
            raise NotImplemented('interpolation method %s not implemented' % method)

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

    def cleardata(self):
        '''
        clears all data, column structure stays unchanged
        :return:
        '''
        self._data = None
        self._row_names = None

    """
    arithmetic operations (two RockPyData objects)
    ==============================================

    There are several cases to distinguish when doing math with RockPyData objects!

    RockPyData objects must have at least one variable column (defined via alias 'variable') and
    can have several data columns (alias 'dep_var').
    Depending on the content of the RockPyData objects arithmetic operations work differently.
    Todo: Units and errors are propagated when possible.


    ROW MATCHING
    Calculation is performed with matching variables. Only those rows are returned.
    In this case use interpolate to get matching variables. Operation fails when variables are not unique
    in one of the two objects. In this case use eliminate_duplicate_variable_rows first.


    COLUMN MATCHING
    If both operands contain more than one data column calculation is applied on matching columns
    (i.e. with same column_name) e.g. (V,A,B,C) + (V,A,D,B) = (V,A+A,B+B)
    If one operand contains only one data column, which does not exist in the other operand,
    calculation is applied to all columns of other operand
    e.g. (V,A,B,C) + (V,A) = (V,A+A)
    e.g. (V,A,B,C) + (V,D) = (V,A+D,B+D,C+D)


    open questions / Todo:
    * how are row labels handled? at the moment the result has no row labels at all
    * how are errors handled

    arithmetic operations (RockPyData object and number / array of numbers)
    =======================================================================
    TODO:
    When an arithmetic operation of a RockPyData object and a simple number is requested, that operation will be applied
    to all non variable elements of the RockPyData object.
    e.g. A + 1, A * 2

    The length of a list of numbers must match the number of non variable columns in the RockPyData object.
    Operation will be applied to all columns

    A 2D numpy array with one row or one column will be broadcasted to non-variable columns or rows

    Todo: what to do with errors?
    """

    def __sub__(self, other):
        """
        subtract operator
        subtracts other rockpydata object

        .. code-block:: python

           A = B - C

        :param other: rockpydata
        :return: new rockpydat object with the results
        """
        return self._arithmetic_op(other, '-')

    def __add__(self, other):
        """
        addition operator
        add other rockpydata object

        .. code-block:: python

           A = B + C

        :param other: rockpydata
        :return: new rockpydat object with the results
        """
        return self._arithmetic_op(other, '+')

    def __mul__(self, other):
        """
        subtract operator
        subtracts other rockpydata object

        .. code-block:: python

           A = B - C

        :param other: rockpydata
        :return: new rockpydat object with the results
        """
        return self._arithmetic_op(other, '*')

    def __div__(self, other):
        """
        subtract operator
        subtracts other rockpydata object

        .. code-block:: python

           A = B/C

        :param other: rockpydata
        :return: new rockpydat object with the results
        """

        return self._arithmetic_op(other, '/')

    def _arithmetic_op(self, other, op):
        """
        looks for matching entries in the 'variable' aliased columns and for matching data columns
        this is needed to prepare an arithmetic operation of two rockpydata objects

        :param other: rockpydata
        :param op: operand ('+','-','/','*')
        :return
        """
        # check if we have a proper rockpydata object for arithmetic operation
        if not isinstance(other, RockPyData):  # todo implement for floats
            raise ArithmeticError('only rockpydata objects can be computed')

        # check if 'variable' alias exist in both objects
        if not (self.key_exists('variable') and other.key_exists('variable')):
            raise ArithmeticError("alias 'variable' not known")

        # check if 'variable' columns match
        if not sorted(self.column_names_from_key('variable')) == sorted(other.column_names_from_key('variable')):
            raise ArithmeticError("'variable' columns do not match")

        # check if variables are unique in both objects
        if len( self._find_duplicate_variable_rows()) > 0:
            raise ArithmeticError("%s has non unique variables" % self.__str__())
        if len( other._find_duplicate_variable_rows()) > 0:
            raise ArithmeticError("%s has non unique variables" % other.__str__())

        # check if remaining columns for matching pairs, only those will be subtracted and returned
        cnames1 = self.column_indices_to_names(set(range(self.column_count)) - set(self.column_dict['variable']))
        cnames2 = other.column_indices_to_names(set(range(other.column_count)) - set(other.column_dict['variable']))

        # get intersection of name sets
        matching_cnames = set(cnames1) & set(cnames2)
        # get indices of matching column names
        mcidx = np.array([(self.column_names.index(n), other.column_names.index(n)) for n in matching_cnames])

        # if we have no intersecting columns, we have to check if one operand has only one column
        if len(matching_cnames) == 0:  # no matching columns
            if len(cnames1) == 1:
                mcidx = np.array([(self.column_names.index(cnames1[0]), other.column_names.index(n)) for n in cnames2])
            elif len(cnames2) == 1:
                mcidx = np.array([(self.column_names.index(n), other.column_names.index(cnames2[0])) for n in cnames1])
            else:
                # none of the operands has only one column which does not match any column in the other operand
                raise ArithmeticError("arithmetic operation failed since there are no matching columns and no operand with single data column")

        # get indices of matching 'variable' values
        d1 = self['variable'].values
        d2 = other['variable'].values
        mridx = np.array(np.all((d1[:, None, :] == d2[None, :, :]), axis=-1).nonzero()).T

        result_c_names = self.column_names_from_key('variable') + self.column_indices_to_names(mcidx[:, 0])
        results_variable = d1[mridx[:, 0], :]  # all columns of variable but only those lines which match in both rockpydata objects

        # data for calculation of both objects with reordered columns according to mcidx
        rd1 = self.data[mridx[:, 0], :][:, mcidx[:, 0]][:, :, 0]
        rd2 = other.data[mridx[:, 1], :][:, mcidx[:, 1]][:, :, 0]


        # todo: care about errors
        if op == '+':
            result_data = rd1 + rd2
        elif op == '-':
            result_data = rd1 - rd2
        elif op == '*':
            result_data = rd1 * rd2
        elif op == '/':
            result_data = rd1 / rd2

        # todo: get column_names and units right
        results_rpd_data = np.append(results_variable, result_data, axis=1)  # variable columns + calculated data columns

        return RockPyData(column_names=result_c_names, row_names=None, data=results_rpd_data)

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
        d = self[column_name].v
        return d / np.max(d) * value

    """ METHODS returning OBJECTS """

    def running_ave(self):
        raise NotImplemented

    def differentiate(self):
        raise NotImplemented

    def filter(self, tf_array):
        """
        Returns a copy of the data filtered by rows according to a True_False array. False entries are not returned.

        tf_array = (d['Mx'].v > 10) & (d['Mx'].v < 20)
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

    def filter_row_names(self, row_names, invert=False):
        '''
        extract rows that match the specified row_names
        :return:
        '''
        if self.row_names is None:
            raise RuntimeError( 'no row names in RockPyData object')
        return self.filter_idx([i for i,x in enumerate( self.row_names) if x in _to_tuple( row_names)], invert=invert)

    def filter_match_row_names(self, regex):
        '''
        extract rows with labels matching regex
        :return:
        '''
        if self.row_names is None:
            raise RuntimeError('no row names in RockPyData object')
        return self.filter([bool(re.match( regex, rn)) for rn in self.row_names])

    def _multirow_op(self, kind):
        '''
        calculate result row out of existing rows
        :param kind: kind of operation
        :return: RockPyData object with results
        '''
        if kind == 'mean':
            val = np.nanmean(self.values, axis=0)[np.newaxis, :, np.newaxis]
            err = np.nanstd(self.values, axis=0)[np.newaxis, :, np.newaxis]
        elif kind == 'median':
            val = np.nanmedian(self.values, axis=0)[np.newaxis, :, np.newaxis]
            err = np.nanstd(self.values, axis=0)[np.newaxis, :, np.newaxis]
        elif kind == 'min':
            minidx = np.nanargmin(self.values, axis=0)
            val = self.values[minidx, range(self.column_count)][np.newaxis, :, np.newaxis]
            err = self.errors[minidx, range(self.column_count)][np.newaxis, :, np.newaxis]
        elif kind == 'max':
            maxidx = np.nanargmax(self.values, axis=0)
            val = self.values[maxidx, range(self.column_count)][np.newaxis, :, np.newaxis]
            err = self.errors[maxidx, range(self.column_count)][np.newaxis, :, np.newaxis]
        elif kind == 'last':
            val = self.values[-1, :][np.newaxis, :, np.newaxis]
            err = self.errors[-1, :][np.newaxis, :, np.newaxis]
        elif kind == 'first':
            val = self.values[0, :][np.newaxis, :, np.newaxis]
            err = self.errors[0, :][np.newaxis, :, np.newaxis]
        else:
            return None  # error

        data = np.concatenate((val, err), axis=2)

        if self.row_names is not None:
            row_name = kind + '_' + '_'.join(self.row_names)
        rpd = RockPyData(self.column_names, row_names=row_name, units=self.unitstrs, data=data)
        # set variable columns the same way
        rpd._column_dict['variable'] = self._column_dict['variable']
        rpd._column_dict['dep_var'] = self._column_dict['dep_var']
        return rpd

    def mean(self):
        '''
        calculate mean values for each column and return as new RockPyData object
        standard deviations are set as errors
        :return: RockPyData object
        '''
        return self._multirow_op('mean')

    def median(self):
        '''
        calculate median values for each column and return as new RockPyData object
        standard deviations are set as errors
        :return: RockPyData object
        '''
        return self._multirow_op('median')

    def min(self):
        '''
        calculate minimum values for each column and return as new RockPyData object
        errors are propagated
        :return: RockPyData object
        '''
        return self._multirow_op('min')

    def max(self):
        '''
        calculate maximum values for each column and return as new RockPyData object
        errors are propagated
        :return: RockPyData object
        '''
        return self._multirow_op('max')

    def first(self):
        '''
        get first row and return as new RockPyData object
        errors are propagated
        :return: RockPyData object
        '''
        return self._multirow_op('first')

    def last(self):
        '''
        get first row and return as new RockPyData object
        errors are propagated
        :return: RockPyData object
        '''
        return self._multirow_op('last')



    def sort(self, key='variable'):
        """
        sorting all data according to one or multiple columns, last column is primary sort order -> see np.lexsort
        e.g.

        .. code-block:: python

           d = data(column_names=('Temp','M'), data=[[10, 1.3],[30, 2.2],[20, 1.5]])
           c = d.sort('Temp')
           c.data
           array([[ 10. ,   1.3],
           [ 20. ,   1.5],
           [ 30. ,   2.2]])

        :param key: str
                  column_name or alias
        :return: new RockPyData object with reordered rows
        """

        self_copy = deepcopy( self)

        data = self[key].values
        sortidx = np.lexsort(data.T, axis=0)  # get indices of ordered rows
        self_copy._data = self_copy.data[ sortidx]  # reorder rows according to sorted indices

        if self_copy.row_names is not None:
            self_copy._row_names = [self_copy.row_names[i] for i in sortidx]  # reorder row names in the same manner

        return self_copy

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
