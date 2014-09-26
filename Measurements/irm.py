from Structure.rockpydata import rockpydata

__author__ = 'volk'
import base
import numpy as np
import Structure.data
import matplotlib.pyplot as plt


class Irm(base.Measurement):
    def __init__(self, sample_obj,
                 mtype, mfile, machine,
                 **options):
        super(Irm, self).__init__(sample_obj, mtype, mfile, machine)

        data_formatting = {
            'vftb': self.format_vftb,
            'vsm': self.format_vsm,
        }

        # ## initialize
        self.data = None

        data_formatting[self.machine]()


    def format_vftb(self):
        self.log.debug('FORMATTING << %s >> raw_data for << VFTB >> data structure' % ('IRM'))
        self.data = rockpydata(column_names=('field', 'moment', 'temperature', 'time',
                                             'std_dev', 'susceptibility'), data=self.raw_data)

    def format_vsm(self):
        raise NotImplemented


    def plt_irm(self):
        plt.title('IRM acquisition %s' % (self.sample_obj.name))
        std, = plt.plot(self.data['field'], self.data['moment'], zorder=1)
        plt.grid()
        plt.axhline(0, color='#808080')
        plt.axvline(0, color='#808080')
        plt.xlabel('Field [%s]' % ('T'))  # todo data.unit
        plt.ylabel('Magnetic Moment [%s]' % ('Am^2'))  # todo data.unit
        plt.show()