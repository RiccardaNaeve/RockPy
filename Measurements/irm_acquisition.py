__author__ = 'volk'
import matplotlib.pyplot as plt

import base
from RockPy.Structure.data import RockPyData
import nrm


class Irm_Acquisition(base.Measurement):
    def __init__(self, sample_obj,
                 mtype, mfile, machine,
                 **options):
        super(Irm_Acquisition, self).__init__(sample_obj, mtype, mfile, machine)

        self._data = {'remanence': self.remanence,
                      'induced': self.induced}

    def format_vftb(self):
        data = self.machine_data.out_irm()
        header = self.machine_data.header
        self.log.debug('FORMATTING << %s >> raw_data for << VFTB >> data structure' % (self.mtype))
        self.remanence = RockPyData(column_names=header, data=data[0])

    def format_vsm(self):
        raise NotImplemented

    def format_cryomag(self):
        self.log.debug('FORMATTING << %s >> raw_data for << cryomag >> data structure' % (self.mtype))

        data = self.machine_data.out_trm()
        header = self.machine_data.float_header
        self.remanence = RockPyData(column_names=header, data=data)
        self.induced = None


    def plt_irm(self):
        plt.title('IRM acquisition %s' % (self.sample_obj.name))
        std, = plt.plot(self.remanence['field'].v, self.remanence['mag'].v, zorder=1)
        plt.grid()
        plt.axhline(0, color='#808080')
        plt.axvline(0, color='#808080')
        plt.xlabel('Field [%s]' % ('T'))  # todo data.unit
        plt.ylabel('Magnetic Moment [%s]' % ('Am2'))  # todo data.unit
        plt.show()