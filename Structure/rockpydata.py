__author__ = 'wack'

import numpy as np


class rockpydata(object):
    '''
    class to manage specific numeric data based on a numpy array
    e.g. d = rockpydata( column_names=( 'F','Mx', 'My', 'Mz'))
    '''

    def __init__(self, column_names, units = None, data = None):
        '''
            * columns: sequence of strings naming individual columns
        '''

        # initialize member variables
        self._column_names = list( column_names)
        # todo: make sure this is a list of strings!
        self._data = None

        self._updatecolumndictionary()

        # define some default aliases
        self._update_all_alias()
        self._column_dict[ 'variable'] = (0,)
        self._column_dict[ 'measurements'] = tuple( range( self.columncount)[1:])

        self['all'] = data

    def _updatecolumndictionary(self, column_names = None):
        '''
        update internal _column_dict to assign single column names and aliases to column indices
        * if column_names == None, populate _column_dict with all columns, aliases will be lost
        * if column_names is list of column names (which must already exist in self._column_names), add or update those in _column_dict
        e.g. {'Mx': (0,),'My': (1,), 'Mz': (2,), 'Mx': (0,1,2))
        '''

        if column_names == None:
            self._column_dict = dict((name, (index,)) for (index, name) in enumerate( self._column_names))
        else:
            for n in column_names: # check if all column_names are valid, i.e. exist in self._column_names
                if not self.column_exists( n):
                    raise IndexError( 'column %s does not exist' % n)
            for n in column_names: # add or update each column to _column_dict
                # todo: rewrite this to dict comprehension for Python 2.7
                self._column_dict[ n] = (self._column_names.index( n),)


    def _update_all_alias(self):#
        self._column_dict[ 'all'] = tuple( range( self.columncount))

    @property
    def columncount(self):
        return len( self._column_names)

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
        if data == None:
            self._data = None # clear existing data
            return

        d = np.array( data)
        if d.ndim != 2:
            raise TypeError( 'wrong data dimension')

        if d.shape[1] != self.columncount:
            raise TypeError( 'wrong number of columns in data')

        self._data = np.array( data)

    def definealias(self, alias_name, column_names):
        '''
        define an alias for a sequence of existing columns
        e.g. d.definealias( 'M', ('Mx', 'My', 'Mz'))
        '''
        # todo: check if all column names exist and that there is at least one column

        # add alias to _column_dict
        self._definealias_indices(alias_name, tuple(self._column_dict[cn][0] for cn in column_names))

    def _definealias_indices(self, alias_name, column_indices):
        '''
        define an alias as a sequence of numeric column indices
        '''
        # todo check if column_indices is integer array?
        # check if column indices are in valid range
        if max( column_indices) > self.columncount or min( column_indices) < 0:
            raise IndexError( 'column indices out of range')
        self._column_dict[alias_name] = tuple( column_indices)

    def append_columns(self, column_names, data = None):
        '''
        add data columns to data object
        column_names: list of strings
        '''
        # todo: also allow simple string to add single column

        # check if column names are already used as keys (= column names and aliases)
        for n in column_names:
            if self.key_exists( n):
                raise IndexError( 'column %s already exists' % n)

        # append new column names to the list
        self._column_names.extend( column_names)

        # update internal column dictionary
        self._updatecolumndictionary( column_names)


        if data == None:
            # if there is no data, create zeros
            data = np.zeros( (self.rowcount, len( column_names)))

        # make sure data is 2 dim, even if there is only one column
        if data.ndim == 1:
            data = data.reshape( data.shape[0], 1)

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
        if not self.key_exists( key):
            raise KeyError( 'key %s is not a valid column name or alias' % key)

        # return appropriate columns from self.data numpy array
        return self._data[:, self._column_dict[ key]]

    def __setitem__(self, key, data):
        '''
        allows access to data columns by index (names)
        e.g. data['Mx'] = (1,2,3)
        '''
        # check if key is valid
        if key not in self._column_dict:
            raise KeyError( 'key %s is not a valid column name or alias' % key)

        if not isinstance(data, np.ndarray):
            data = np.array(data)

        # if we have no data, initialize everything to zero with number of lines matching the new data
        if self._data == None:
            self._data = np.zeros( ( data.shape[0], self.columncount))

        # make sure data is 2 dim, even if there is only one column
        if data.ndim == 1:
            data = data.reshape( data.shape[0], 1)

        self._data[:, self._column_dict[ key]] = data


    def magnitude(self, column_name = 'measurement', result_column = None):
        '''
        calculate magnitude of vector columns
        return
        * np.array of data if new column is None
        * reference to self including the newly calculated column
        '''

        mag = np.sum( np.abs( self[ column_name])**2,axis=-1)**(1./2)

        if result_column == None:
            return mag # return the calculated magnitudes directly
        else:
            if not self.column_exists( result_column): # if result_column doesn't exist -> append it
                self.append_columns( (result_column,))

            self[result_column] = mag # write result into specified column

            return self


    def differentiate(self):
        pass