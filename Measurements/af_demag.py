import matplotlib.pyplot as plt
import numpy as np

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

    def result_mdf(self, component='mag', recalc=False):
        """
        Calculates the MDF (median destructive field from data using linear interpolation between closest points
        :param parameter:
        :param recalc:
        :return:
        """
        parameter = {'component': component}
        self.calc_result(parameter, recalc)
        return self.results['mdf']

    def calculate_mdf(self, **parameter):
        self.log.info('CALCULATING << MDF >> parameter from linear interpolation')

        component = parameter.get('component', 'mag')
        data = self.data[component] / max(self.data[component])  # normalize data
        idx = np.argmin(np.abs(data) - 0.5)  # index of closest to 0.5

        if data.all() > 0.5:
            self.log.warning('MDF not reached in measurement, mdf from extrapolated data')
            # getting indices from last two elements
            idx2 = len(data) - 1  # last index
            idx1 = idx2 - 1  # second to last idx

        else:
            if data[idx] < 0.5:
                idx1 = idx
                idx2 = idx - 1
            else:
                idx1 = idx + 1
                idx2 = idx

        i = [idx1, idx2]

        d = self.data.filter_idx(index_list=i)
        slope, sigma, y_intercept, x_intercept = d.lin_regress('field', component)
        mdf = abs((y_intercept * 0.5 ) / slope)
        self.results['mdf'] = mdf


    def plt_afdemag(self, norm=False):
        if norm:
            norm_factor = max(self.data['mag'])
        else:
            norm_factor = 1
        plt.plot(self.data['field'], self.data['mag'] / norm_factor, '.-')
        plt.show()