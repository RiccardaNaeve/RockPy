__author__ = 'volk'
import logging
import Functions.general
import numpy as np
import copy


class data(object):
    Functions.general.create_logger('RockPy.DATA')
    def __init__(self,
                 variable, measurement,
                 var_unit, measure_unit,
                 std_dev=None, time=None,
                 **options):
        '''
        Generic 3D / 1D data contains with rudimentary functions concerning paleomagnetic data
        '''

        if not isinstance(variable, np.ndarray):
            variable = np.array(variable)
        if not isinstance(measurement, np.ndarray):
            measurement = np.array(measurement)
        if not isinstance(std_dev, np.ndarray):
            std_dev = np.array(std_dev)

        self.dimension = measurement.size / variable.size
        self.log = logging.getLogger('RockPy.DATA.data(%i, %i)' %(measurement.size/self.dimension, self.dimension))
        self.log.debug('CREATING data structure: dimension << (%i, %i) >>' %(measurement.size/self.dimension, self.dimension))

        # units
        self.var_unit = var_unit
        self.measure_unit = measure_unit

        if time is None:
            time = np.zeros(variable.size)
        self.time = time

        if std_dev is None:
            std_dev = np.zeros(variable.size)
        self.std_dev = std_dev

        self.variable = variable

        if self.dimension == 3:
            self.log.debug('CALCULATING << m >> for data structure: dimension << %i >>' % self.dimension)
            self.measurement = np.c_[measurement, np.array([np.linalg.norm(i) for i in measurement])]
        else:
            self.measurement = measurement

    @property
    def m_utype(self):
        '''
        lookup table for unit type: e.g. mg -> mass
        :return: str
               unit type for measurement
        '''
        table = {
            'length': ['nm', 'mum', 'mm', 'cm', 'dm', 'km',
                            'angstrom',
                            'line', 'inch', 'foot', 'yard ', 'mile', 'league'],
            'mass': ['ng', 'mug', 'mg', 'g', 'kg', 'T'],
                 }

        for i in table:
            if self.measure_unit in table[i]:
                return i

    @property
    def data(self):
        return self.measurement


class data_old(object):
    def __init__(self,
                 variable, measurement,
                 var_unit, measure_unit,
                 std_dev=None, time=None,
                 **options):
        '''
        Generic 3D / 1D data contains with rudimentary functions concerning paleomagnetic data
        '''

        self.log = logging.getLogger('RockPy.DATA.data%s' % str(measurement.shape))
        self.log.debug('CREATING data structure: dimension << %s >>' % str(measurement.shape))

        if not isinstance(variable, np.ndarray):
            self.log.debug('CONVERTING variable to ndarray')
            variable = np.array(variable)

        if not isinstance(measurement, np.ndarray):
            self.log.debug('CONVERTING variable to ndarray')
            measurement = np.array(measurement)

        self.variable = variable
        # print np.c_[measurement, np.array([np.linalg.norm(i) for i in measurement])]

        if measurement.size == variable.size:
            self.log.debug('CONVERTING variable to ndarray')

            measurement = np.c_[measurement, measurement, measurement]

        self.measurement = np.c_[measurement, np.array([np.linalg.norm(i) for i in measurement])]

        # units
        self.var_unit = var_unit
        self.measure_unit = measure_unit

        self.std_dev = std_dev

        if time is None:
            time = np.zeroes(len(variable))

        self.time = time

    def __repr__(self):
        return '<Structure.data.data object len,dim: (%i,%i)> ' % (self.len, self.dim)

    ''' data properties '''

    @property
    def data(self):
        return self.measurement

    @property
    def x(self):
        if self.measurement.shape[0] == self.measurement.size:
            return self.measurement
        else:
            return self.measurement[:, 0]

    @property
    def y(self):
        if self.measurement.shape[0] == self.measurement.size:
            return self.measurement
        else:
            return self.measurement[:, 1]

    @property
    def z(self):
        if self.measurement.shape[0] == self.measurement.size:
            return self.measurement
        else:
            return self.measurement[:, 2]

    @property
    def m(self):
        if self.measurement.shape[0] == self.measurement.size:
            return self.measurement
        else:
            # out = np.array(map(np.linalg.norm, self.measurement))
            return self.measurement[:, 3]

    @property
    def d(self):
        if self.measurement.shape[0] == self.measurement.size:
            self.log.error('DATA is only 1d, << dec >> can not be calculated')
        else:
            out = np.arctan2(self.y, self.x)
            out = np.degrees(out)

            for i in range(len(out)):
                if out[i] < 0:
                    out[i] += 360
                if out[i] > 360:
                    out[i] -= 360
            return out

    @property
    def i(self):
        if self.measurement.shape[0] == self.measurement.size:
            self.log.error('DATA is only 1d, << inc >> can not be calculated')
        else:
            out = np.arcsin(self.z / self.m)
            out = np.degrees(out)
            return out

    @property
    def len(self):
        return len(self.measurement)

    @property
    def dim(self):
        return len(self.measurement.T)

    # ## functions

    def max(self, component='m'):
        out = getattr(self, component, None)
        if out:
            out = np.fabs(out)
            out = np.max(out)
            return out
        else:
            self.log.error('COMPONENT << %s >> not found' % component)

    def min(self, component='m'):
        out = getattr(self, component, None)
        if out:
            out = np.fabs(out)
            out = np.min(out)
            return out
        else:
            self.log.error('COMPONENT << %s >> not found' % component)

    def diff(self, strength=1):
        self_copy = self.__class__(copy.deepcopy(self.variable),
                                   copy.deepcopy(self.measurement),
                                   copy.deepcopy(self.time))

        aux = [[self_copy.variable[i],
                np.array((self_copy.measurement[i - strength] - self_copy.measurement[i + strength]) / (
                    self_copy.variable[i - strength] - self_copy.variable[i + strength]))]
               for i in range(strength, len(self_copy.variable) - strength)]

        self_copy.variable = np.array([i[0] for i in aux])
        self_copy.measurement = np.array([i[1] for i in aux])

        return self_copy


    # ## calculations
    def __sub__(self, other):  #
        self_copy = self.__class__(copy.deepcopy(self.variable),
                                   copy.deepcopy(self.measurement),
                                   copy.deepcopy(self.time))

        if isinstance(other, data):
            self_copy.measurement = np.array(
                [self_copy.measurement[i] - other.measurement[i] for i in range(len(self_copy.measurement))
                 if self_copy.variable[i] == other.variable[i]])

        if isinstance(other, np.ndarray):
            try:
                self_copy.measurement -= other
            except:
                print 'nope'
        return self_copy

    def __add__(self, other):
        self_copy = self.__class__(copy.deepcopy(self.variable),
                                   copy.deepcopy(self.measurement),
                                   copy.deepcopy(self.time))

        self_copy.measurement += other.measurement
        return self_copy

    def __div__(self, other):
        self_copy = self.__class__(copy.deepcopy(self.variable),
                                   copy.deepcopy(self.measurement),
                                   copy.deepcopy(self.time))

        if isinstance(other, data):
            if other.len != 1:
                self_copy.measurement = np.array(
                    [self_copy.measurement[i] / other.measurement[i] for i in range(len(self_copy.measurement))
                     if self_copy.variable[i] == other.variable[i]])
            else:
                self_copy.measurement /= other.measurement
                print self_copy.m
        if isinstance(other, np.ndarray):
            self_copy.measurement /= other

        return self_copy

    def equal_var(self, other):
        '''
        returns data object that has only the same variables as the other data_obj
        '''
        self_copy = self.__class__(copy.deepcopy(self.variable),
                                   copy.deepcopy(self.measurement),
                                   copy.deepcopy(self.time))

        idx = [i for i in range(len(self_copy.variable)) if
               self_copy.variable[i] not in other.variable]  # indices of self, not in common with other

        if idx:
            self.log.info('FOUND different variables deleting << %i >> non-equal' % len(idx))
            for i in idx:
                self_copy.variable = np.delete(self_copy.variable, i)
                self_copy.measurement = np.delete(self_copy.measurement, i, axis=0)
                self_copy.time = np.delete(self_copy.time, i)

        return self_copy


    def retrieve(self, idx):
        return self.variable[idx], self.measurement[idx], self.time[idx]

    def append(self, idx):
        pass

    def slice_range(self, low_lim=None, up_lim=None):
        '''
        Generates a copy of data with data within the specified range of variables (inclusive)

        :param low_lim:
        :param up_lim:
        :rtype : data_obj
        '''

        self_copy = self.__class__(copy.deepcopy(self.variable),
                                   copy.deepcopy(self.measurement),
                                   copy.deepcopy(self.time))
        if low_lim is None:
            low_lim = min(self_copy.variable)
        if up_lim is None:
            up_lim = max(self_copy.variable)

        idx = [i for i in range(len(self_copy.variable)) if self_copy.variable[i] < low_lim if
               self_copy.variable[i] > up_lim]
        if idx:
            self.log.debug('FOUND variables not within specified range deleting << %i >> non-equal' % len(idx))
            for i in idx:
                self_copy.variable = np.delete(self_copy.variable, i)
                self_copy.measurement = np.delete(self_copy.measurement, i)
                self_copy.time = np.delete(self_copy.time, i)

        return self_copy