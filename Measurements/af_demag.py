import matplotlib.pyplot as plt
import numpy as np

from RockPy.Structure.data import RockPyData
import base


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

    def format_sushibar(self):
        self.data = RockPyData(column_names=['field', 'x', 'y', 'z'],
                               data=self.machine_data.out_afdemag())  # , units=['mT', 'Am^2', 'Am^2', 'Am^2'])
        self.data.define_alias('m', ( 'x', 'y', 'z'))
        self.data.append_columns('mag', self.data.magnitude('m'))

    def smoothing_spline(self, y_component='mag', x_component='field', out_spline=False):
        from scipy.interpolate import UnivariateSpline
        x_old = self.data[x_component].v
        y_old = self.data[y_component].v
        smoothing_spline = UnivariateSpline(x_old, y_old, s=1)

        if not out_spline:
            x_new = np.linspace(min(x_old), max(x_old), 100)
            y_new = smoothing_spline(x_new)
            out = RockPyData(column_names=[x_component, y_component], data=np.c_[x_new, y_new])
            return out
        else:
            return smoothing_spline

    def result_mdf(self, component='mag', interpolation='linear', recalc=False):
        """
        Calculates the MDF (median destructive field from data using linear interpolation between closest points
        :param parameter: interpolation:
           interpolation methods:

           'linear' : linear interpolation between points
           'smooth_spline' : calculation using a smoothing spline


        :param recalc:
        :return:
        """
        parameter = {'component': component,
                     'interpolation': interpolation}
        self.calc_result(parameter, recalc)
        return self.results['mdf']

    def calculate_mdf(self, **parameter):
        interpolation = parameter.get('interpolation', 'linear')
        self.log.info('CALCULATING << MDF >> parameter from %s interpolation' %interpolation)


        methods = {'linear': self.calc_mdf_linear,
                   'smooth_spline': self.calc_mdf_smooth}

        methods[interpolation](**parameter)
        self.calculation_parameters['mdf'] = parameter

    def calc_mdf_smooth(self, **parameter):
        self.log.error('NOT IMPLEMENTED YET')
        self.results['mdf'] = np.nan

        return

        component = parameter.get('component', 'mag')
        data = self.data[component].v / max(self.data[component].v)  # normalize data

        if np.all(data > 0.5):
            self.log.warning('MDF not reached in measurement, mdf from extrapolated data')
            self.results['mdf'] = np.nan
            return

        smooth_spline = self.smoothing_spline(y_component='field', x_component=component, out_spline=False)
        # smooth_spline = self.smoothing_spline(x_component='field', y_component=component, out_spline=False)
        print smooth_spline
        plt.plot(self.data['field'].v, self.data['mag'].v, '.')
        plt.plot(smooth_spline['field'].v, smooth_spline['mag'].v)
        plt.show()
        # mdf = smooth_spline(0.5*max(self.data[component].v))
        # self.results['mdf'] = mdf

    def calc_mdf_linear(self, **parameter):
        component = parameter.get('component', 'mag')
        data = self.data[component].v / max(self.data[component].v)  # normalize data
        idx = np.argmin(np.abs(data - 0.5))  # index of closest to 0.5

        if np.all(data > 0.5):
            self.log.warning('MDF not reached in measurement, mdf from extrapolated data')
            # getting indices from last two elements
            idx2 = len(data) - 1  # last index
            idx1 = idx2 - 1  # second to last idx

        else:
            print data[idx - 1], data[idx], data[idx + 1]
            if data[idx] < 0.5:
                idx1 = idx - 1
                idx2 = idx
            else:
                idx1 = idx
                idx2 = idx + 1

        i = [idx1, idx2]
        d = self.data.filter_idx(index_list=i)
        slope, sigma, y_intercept, x_intercept = d.lin_regress('field', component)
        mdf = abs((0.5 * max(self.data[component].v) - y_intercept) / slope)
        self.results['mdf'] = mdf

    def plt_afdemag(self, norm=False):
        if norm:
            norm_factor = max(self.data['mag'])
        else:
            norm_factor = 1

        plt.title('%s' % self.sample_obj.name)
        plt.plot(self.data['field'].v, self.data['mag'].v / norm_factor, '.-')
        plt.xlabel('field [%s]' % 'mT')
        plt.ylabel('Moment [%s]' % 'Am^2')
        plt.grid()
        plt.show()