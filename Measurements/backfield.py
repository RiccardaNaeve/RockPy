__author__ = 'volk'
import base
import Structure.data
import Structure.rockpydata
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
        self.remanence = Structure.rockpydata.rockpydata(column_names=('field', 'moment', 'temperature', 'time',
                                                                  'std_dev', 'susceptibility'), data= self.raw_data)

    def plt_backfield(self):
        plt.plot(self.remanence['field'], self.remanence['moment'])

        if self.induced:
            plt.plot(self.induced['field'], self.induced['moment'])

        plt.title('Backfield %s' %(self.sample_obj.name))
        plt.xlabel('Field [%s]' %('T')) #todo replace with data unit
        plt.ylabel('Moment [%s]' %('Am^2')) #todo replace with data unit
        plt.show()