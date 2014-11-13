import matplotlib.pyplot as plt
import numpy as np

from RockPy.Structure.data import RockPyData
import base


class AfDemag(base.Measurement):
    '''
    '''

    def __init__(self, sample_obj,
                 mtype, mfile, machine,
                 mag_method='', demag_type='af3',
                 **options):

        self.demag_type = demag_type

        super(AfDemag, self).__init__(sample_obj,
                                      mtype, mfile, machine,
                                      **options)
        self.mag_method = mag_method

    def format_jr6(self):
        self.data = RockPyData(column_names=['field', 'x', 'y', 'z'], data=self.machine_data.out_afdemag())
        self.data.define_alias('m', ( 'x', 'y', 'z'))
        self.data = self.data.append_columns('mag', self.data.magnitude('m'))

    def format_sushibar(self):
        self.data = RockPyData(column_names=['field', 'x', 'y', 'z'],
                               data=self.machine_data.out_afdemag())  # , units=['mT', 'Am^2', 'Am^2', 'Am^2'])
        self.data.define_alias('m', ( 'x', 'y', 'z'))
        self.data = self.data.append_columns('mag', self.data.magnitude('m'))

    def format_cryomag(self):
        self.data = RockPyData(column_names=self.machine_data.float_header,
                               data=self.machine_data.get_float_data())
        if self.demag_type != 'af3':
            idx = [i for i, v in enumerate(self.machine_data.steps) if v == self.demag_type]
            self.data = self.data.filter_idx(idx)
        self.data = self.data.append_columns('mag', self.data.magnitude('m'))
        self.data.rename_column('step', 'field')

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

        component = parameter.get('component', 'mag')
        data = self.data  # normalize data #todo replace with normalize function
        data.define_alias('variable', component)
        data_max = max(data[component].v)
        data = data.sort('mag')
        data = data.interpolate([data_max*0.5])
        self.results['mdf'] = data['field'].v

    # ## INTERPOLATION

    def interpolate_smoothing_spline(self, y_component='mag', x_component='field', out_spline=False):
        """
        Interpolates using a smoothing spline between a x and y component
        :param y_component:
        :param x_component:
        :param out_spline:
        :return:
        """
        from scipy.interpolate import UnivariateSpline

        x_old = self.data[x_component].v  #
        y_old = self.data[y_component].v
        smoothing_spline = UnivariateSpline(x_old, y_old, s=1)

        if not out_spline:
            x_new = np.linspace(min(x_old), max(x_old), 100)
            y_new = smoothing_spline(x_new)
            out = RockPyData(column_names=[x_component, y_component], data=np.c_[x_new, y_new])
            return out
        else:
            return smoothing_spline

    def interpolation_spline(self, y_component='mag', x_component='field', out_spline=False):

        from scipy.interpolate import UnivariateSpline

        x_old = self.data[x_component].v  #
        y_old = self.data[y_component].v
        smoothing_spline = UnivariateSpline(x_old, y_old, s=1)

        if not out_spline:
            x_new = np.linspace(min(x_old), max(x_old), 100)
            y_new = smoothing_spline(x_new)
            out = RockPyData(column_names=[x_component, y_component], data=np.c_[x_new, y_new])
            return out
        else:
            return smoothing_spline

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