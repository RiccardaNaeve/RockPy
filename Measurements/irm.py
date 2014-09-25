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
        self.data = Structure.data.data(variable=self.raw_data['field'], var_unit='T',
                                        measurement=self.raw_data['moment'], measure_unit='Am^2',
                                        std_dev=self.raw_data['std_dev'])

    def format_vsm(self):
        pass


    def plt_irm(self):
        std, = plt.plot(self.data.variable, self.data.measurement)
        plt.xlabel('Field [%s]' % self.data.var_unit)
        plt.ylabel('Magnetic Moment [%s]' % self.data.measure_unit)
        plt.show()