# coding=utf-8
__author__ = 'volk'
from Structure.rockpydata import rockpydata
import base
import numpy as np
import scipy as sp
import Structure.data
import matplotlib.pyplot as plt
import sys


class Thellier(base.Measurement):
    def __init__(self, sample_obj,
                 mtype, mfile, machine,
                 **options):
        super(Thellier, self).__init__(sample_obj, mtype, mfile, machine)

        # ## initialize data
        # paint data
        self.th = None  # thermal demag steps
        self.pt = None  # in field steps
        # checks
        self.ac = None  #
        self.tr = None  #
        self.ck = None  #

        if callable(getattr(self, 'format_' + machine)):  # check for available formatting NEEDS TO START WITH format_
            getattr(self, 'format_' + machine)()  # call format_ for appropriate machine


    def format_cryomag(self):
        '''
        Formats cryomag output dictionary into thellier measurement data format.

        Beware: NRM step has to be called NRM or TH

        :return:
        '''
        self.all_data = rockpydata(column_names=['temp', 'x', 'y', 'z', 'moment', 'time', 'std_dev'])
        self.all_data['x'] = self.raw_data['x']
        self.all_data['y'] = self.raw_data['y']
        self.all_data['z'] = self.raw_data['z']
        self.all_data['moment'] = self.raw_data['m']
        self.all_data['temp'] = self.raw_data['step']
        self.all_data['std_dev'] = self.raw_data['sm']

        TH_idx = np.where(self.raw_data['type'] == 'TH')[0]
        PT_idx = np.where(self.raw_data['type'] == 'PT')[0]
        NRM_idx = np.where(self.raw_data['type'] == 'NRM')[0]
        TRM_idx = np.where(self.raw_data['type'] == 'TRM')[0]

        self.nrm = self.all_data.filter_idx(NRM_idx)
        self.trm = self.all_data.filter_idx(TRM_idx)
        self.th = self.all_data.filter_idx(np.append(NRM_idx, TH_idx))
        self.th.define_alias('m', ( 'x', 'y', 'z'))
        self.th.sort('temp')

        self.pt = self.all_data.filter_idx(np.append(NRM_idx, PT_idx))
        self.pt.sort('temp')
        self.pt.define_alias('m', ('x', 'y', 'z'))

        # ## PTRM
        var_index = np.array([(i, j) for i, v1 in enumerate(self.th['temp']) for j, v2 in enumerate(self.pt['temp'])
                              if v1 == v2])

        t = [self.pt['temp'][j] for i, j in var_index]
        x = [self.pt['x'][j] - self.th['x'][i] for i, j in var_index]
        y = [self.pt['y'][j] - self.th['y'][i] for i, j in var_index]
        z = [self.pt['z'][j] - self.th['z'][i] for i, j in var_index]
        m = [self.pt['moment'][j] - self.th['moment'][i] for i, j in var_index]
        std_dev = [self.pt['std_dev'][j] + self.th['std_dev'][i] for i, j in var_index]
        data = np.c_[t, x, y, z, m, std_dev]

        data = data[data[:, 0].argsort()]

        self.ptrm = rockpydata(column_names=['temp', 'x', 'y', 'z', 'moment', 'std_dev'], data=data)
        self.ptrm.define_alias('m', ( 'x', 'y', 'z'))
        self.ptrm.append_columns('mag', self.ptrm.magnitude('m'))
        ### SUM
        var_index = np.array([(i, j) for i, v1 in enumerate(self.th['temp']) for j, v2 in enumerate(self.ptrm['temp'])
                              if v1 == v2])

        t = [self.th['temp'][j] for i, j in var_index]
        x = [self.ptrm['x'][j] + self.th['x'][i] for i, j in var_index]
        y = [self.ptrm['y'][j] + self.th['y'][i] for i, j in var_index]
        z = [self.ptrm['z'][j] + self.th['z'][i] for i, j in var_index]
        m = [self.ptrm['moment'][j] + self.th['moment'][i] for i, j in var_index]
        std_dev = [self.ptrm['x'][j] + self.th['std_dev'][i] for i, j in var_index]
        data = np.c_[t, x, y, z, m, std_dev]
        data = data[data[:,0].argsort()]

        self.sum = rockpydata(column_names=['temp', 'x', 'y', 'z', 'moment', 'std_dev'], data=data)
        self.sum.define_alias('m', ( 'x', 'y', 'z'))
        self.sum.append_columns('mag', self.sum.magnitude('m'))

        self.ac = self.all_data.filter_idx(np.where(self.raw_data['type'] == 'AC')[0])
        self.ck = self.all_data.filter_idx(np.where(self.raw_data['type'] == 'CK')[0])
        self.tr = self.all_data.filter_idx(np.where(self.raw_data['type'] == 'TR')[0])


    def format_sushibar(self):
        raise NotImplementedError

    # ## plotting functions
    def plt_dunlop(self):

        plt.plot(self.th['temp'], self.th['moment'], '.-', zorder=1)
        # plt.plot(self.ptrm['temp'], self.ptrm['moment'], '.-', zorder=1)
        plt.plot(self.ptrm['temp'], self.ptrm['mag'], '.-', zorder=1)
        plt.plot(self.sum['temp'], self.sum['mag'], '.--', zorder=1)
        plt.plot(self.tr['temp'], self.tr['moment'], 's')
        plt.grid()
        plt.title('Dunlop Plot %s' % (self.sample_obj.name))
        plt.xlabel('Temperature [%s]' % ('C'))
        plt.ylabel('Moment [%s]' % ('Am^2'))
        plt.xlim([min(self.th['temp']), max(self.th['temp'])])
        plt.show()

    def plt_arai(self):
        equal = set(self.th['temp']) & set(self.ptrm['temp'])
        idx = [i for i,v in enumerate(self.th['temp']) if v in equal]
        th = self.th.filter_idx(idx)
        plt.plot(self.ptrm['moment'], th['moment'], '.-', zorder=1)
        plt.grid()
        plt.title('Arai Diagram %s' % (self.sample_obj.name))
        plt.xlabel('NRM remaining [%s]' % ('C'))
        plt.ylabel('pTRM gained [%s]' % ('Am^2'))
        plt.show()

    @property
    def generic(self):
        '''
        helper function that returns the value for a given statistical method. If result not available will calculate
        it with standard parameters
        '''
        return self.result_generic()

    def result_generic(self, parameters='standard'):
        '''
        Generic for for result implementation. Every calculation of result should be in the self.results data structure
        before calculation.
        It should then be tested if a value for it exists, and if not it should be created by calling
        _calculate_result_(result_name).

        '''
        if self.results['generic'] is None:
            self.calculate_generic(parameters)
        return self.results['generic']

    def calculate_generic(self, parameters):
        '''
        actual calculation of the result

        :return:
        '''
        self.results['generic'] = 0