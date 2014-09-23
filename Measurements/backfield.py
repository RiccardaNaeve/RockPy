__author__ = 'volk'
import base
import Structure.data
import matplotlib.pyplot as plt


class Backfield(base.Measurement):
    def __init__(self, sample_obj,
                 mtype, mfile, machine,
                 **options):
        super(Backfield, self).__init__(sample_obj, mtype, mfile, machine)

        data_formatting = {'vftb': self.format_vftb,
        }
        # ## initialize
        self.remanence = None
        self.induced = None

        data_formatting[self.machine]()

    def format_vftb(self):
        self.remanence = Structure.data.data(variable=self.raw_data['field'], var_unit='T',
                                             measurement=self.raw_data['moment'], measure_unit='emu',
                                             std_dev=self.raw_data['std_dev'])

    def plt_backfield(self):
        plt.plot(self.remanence.variable, self.remanence.measurement)
        if self.induced:
            plt.plot(self.induced.variable, self.induced.measurement)
        plt.show()