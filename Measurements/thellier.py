__author__ = 'volk'
from Structure.rockpydata import rockpydata
import base
import numpy as np
import Structure.data
import matplotlib.pyplot as plt


class Thellier(base.Measurement):
    def __init__(self, sample_obj,
                 mtype, mfile, machine,
                 **options):
        super(Thellier, self).__init__(sample_obj, mtype, mfile, machine)

        data_formatting = {'cryomag': self.format_cryomag,
                           'sushibar': self.format_sushibar}

        # ## initialize data
        # paint data
        self.th = None  # thermal demag steps
        self.pt = None  # in field steps
        # checks
        self.ac = None  #
        self.tr = None  #
        self.ck = None  #
        # results
        self.results = None

        data_formatting[self.machine]()
        print self.th['moment']
        print self.th['temp']

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
        self.ptrm = None

        self.ac = self.all_data.filter_idx(np.where(self.raw_data['type'] == 'AC')[0])
        self.ck = self.all_data.filter_idx(np.where(self.raw_data['type'] == 'CK')[0])
        self.tr = self.all_data.filter_idx(np.where(self.raw_data['type'] == 'TR')[0])


    def format_sushibar(self):
        raise NotImplementedError

    # ## plotting functions
    def plt_dunlop(self):
        ### workaround until data.sort()
        # todo implements data.sort
        xy = np.c_[self.th['temp'], self.th['moment']]
        xy = xy[np.lexsort((xy[:,1], xy[:,0]))]
        plt.plot(xy[:,0], xy[:,1], '.-', zorder=1)

        # plt.plot(self.th['temp'], self.th['moment'], '.-', zorder=1) #todo uncomment when data.sort
        plt.plot(self.pt['temp'], self.pt['moment'], '.-', zorder=1)
        plt.plot(self.tr['temp'], self.tr['moment'], 's')
        plt.grid()
        plt.title('Dunlop Plot %s' %(self.sample_obj.name))
        plt.xlabel('Temperature [%s]' %('C'))
        plt.ylabel('Moment [%s]' %('Am^2'))
        plt.xlim([min(self.th['temp']), max(self.th['temp'])])
        plt.show()

    def plt_arai(self):
        raise NotImplementedError
