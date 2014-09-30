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

        # results
        result_methods = [i[7:] for i in dir(self) if i.startswith('result_')]  # search for implemented results methods
        self.results = rockpydata(
            column_names=result_methods)  # dynamic entry creation for all available result methods

        if callable(getattr(self, 'format_' + machine)):  # check for available formatting NEEDS TO START WITH format_
            getattr(self, 'format_' + machine)()  # call format_ for appropriate machine

    def format_cryomag(self):
        '''
        Formats cryomag output dictionary into thellier measurement data format.

        Beware: NRM step has to be called NRM or TH

        :return:
        '''
        self.all_data = rockpydata(column_names=['type', 'x', 'y', 'z', 'moment', 'time', 'temp', 'std_dev'])
        self.all_data['x'] = self.raw_data['x']
        self.all_data['y'] = self.raw_data['y']
        self.all_data['z'] = self.raw_data['z']
        self.all_data['moment'] = self.raw_data['m']
        self.all_data['temp'] = self.raw_data['step']

        TH_idx = np.where(self.raw_data['type'] == 'TH')[0]
        PT_idx = np.where(self.raw_data['type'] == 'PT')[0]
        NRM_idx = np.where(self.raw_data['type'] == 'NRM')[0]
        TRM_idx = np.where(self.raw_data['type'] == 'TRM')[0]

        self.nrm = self.all_data.filter_idx(NRM_idx)
        self.trm = self.all_data.filter_idx(TRM_idx)
        self.th = self.all_data.filter_idx(np.append(NRM_idx, TH_idx))
        self.pt = self.all_data.filter_idx(np.append(NRM_idx, PT_idx))
        self.ptrm = self.pt.minus_equal_var(self.th, 'temp')

        self.ac = self.all_data.filter_idx(np.where(self.raw_data['type'] == 'AC')[0])
        self.ck = self.all_data.filter_idx(np.where(self.raw_data['type'] == 'CK')[0])
        self.tr = self.all_data.filter_idx(np.where(self.raw_data['type'] == 'TR')[0])


    def format_sushibar(self):
        raise NotImplementedError

    # ## plotting functions
    def plt_dunlop(self):
        # ## workaround until data.sort()
        # todo implements data.sort
        xy = np.c_[self.th['temp'], self.th['moment']]
        xy = xy[np.lexsort((xy[:, 1], xy[:, 0]))]
        plt.plot(xy[:, 0], xy[:, 1], '.-', zorder=1)

        # plt.plot(self.th['temp'], self.th['moment'], '.-', zorder=1) #todo uncomment when data.sort
        plt.plot(self.pt['temp'], self.pt['moment'], '.-', zorder=1)
        plt.plot(self.tr['temp'], self.tr['moment'], 's')
        plt.grid()
        plt.title('Dunlop Plot %s' % (self.sample_obj.name))
        plt.xlabel('Temperature [%s]' % ('C'))
        plt.ylabel('Moment [%s]' % ('Am^2'))
        plt.xlim([min(self.th['temp']), max(self.th['temp'])])
        plt.show()

    def plt_arai(self):
        raise NotImplementedError

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