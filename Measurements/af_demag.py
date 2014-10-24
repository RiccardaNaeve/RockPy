import matplotlib.pyplot as plt

import base
from Structure.rockpydata import RockPyData


class AfDemag(base.Measurement):
    '''
    '''

    def __init__(self, sample_obj,
                 mtype, mfile, machine,
                 **options):
        super(AfDemag, self).__init__(sample_obj,
                                      mtype, mfile, machine,
                                      **options)

    def format_jr6(self):
        self.data = RockPyData(column_names=['field', 'x', 'y', 'z'], data=self.machine_data.out_afdemag())
        self.data.define_alias('m', ( 'x', 'y', 'z'))
        self.data.append_columns('mag', self.data.magnitude('m'))

    def plt_afdemag(self, norm=False):
        if norm:
            norm_factor = max(self.data['mag'])
        else:
            norm_factor = 1
        plt.plot(self.data['field'], self.data['mag'] / norm_factor, '.-')
        plt.show()