import matplotlib.pyplot as plt
import numpy as np
from copy import deepcopy

from RockPy.Structure.data import RockPyData
import base


class Parm_Spectra(base.Measurement):
    '''
    '''

    def __init__(self, sample_obj,
                 mtype, mfile, machine,
                 mag_method='',
                 **options):
        super(Parm_Spectra, self).__init__(sample_obj,
                                           mtype, mfile, machine,
                                           **options)

    def format_sushibar(self):
        data = self.machine_data.out_parm_spectra()
        self.af3 = RockPyData(column_names=data[1],
                              data=data[0][0],
                              units=data[2])
        self.af3.define_alias('m', ( 'x', 'y', 'z'))
        self.af3 = self.af3.append_columns('mag', self.af3.magnitude('m'))
        self.af3 = self.af3.append_columns(column_names='mean_window',
                                           data=np.array([self.af3['upper_window'].v + self.af3['lower_window'].v])[
                                                    0] / 2)

        self.data = RockPyData(column_names=data[1],
                               data=data[0][1:],
                               units=data[2])
        self.data.define_alias('m', ( 'x', 'y', 'z'))
        self.data = self.data.append_columns('mag', self.data.magnitude('m'))
        self.data = self.data.append_columns(column_names='mean_window',
                                             data=np.array([self.data['upper_window'].v + self.data['lower_window'].v])[
                                                      0] / 2)

    def plt_parm_spectra(self, subtract_af3=True, rtn=False, norm=False, fill=False):
        plot_data = deepcopy(self.data)

        if subtract_af3:
            plot_data['x'] = plot_data['x'].v - self.af3['x'].v
            plot_data['y'] = plot_data['y'].v - self.af3['y'].v
            plot_data['z'] = plot_data['z'].v - self.af3['z'].v
            plot_data['mag'] = plot_data.magnitude('m')

        if norm:
            norm_factor = max(plot_data['mag'].v)
        else:
            norm_factor = 1

        if fill:
            plt.fill_between(plot_data['mean_window'].v, 0, plot_data['mag'].v / norm_factor,
                             alpha=0.1,
                             label='pARM spetra')
        else:
            plt.plot(plot_data['mean_window'].v, 0, plot_data['mag'].v / norm_factor,
                     label='pARM spetra')
        if not rtn:
            plt.show()


    def plt_parm_acquisition(self, subtract_af3=True, rtn=False, norm=False):
        plot_data = deepcopy(self.data)



        if subtract_af3:
            plot_data['x'] = plot_data['x'].v - self.af3['x'].v
            plot_data['y'] = plot_data['y'].v - self.af3['y'].v
            plot_data['z'] = plot_data['z'].v - self.af3['z'].v
            plot_data['mag'] = plot_data.magnitude('m')

        plot_data['x'] = [np.sum(plot_data['x'].v[:i]) for i in range(len(plot_data['x'].v))]
        plot_data['y'] = [np.sum(plot_data['y'].v[:i]) for i in range(len(plot_data['y'].v))]
        plot_data['z'] = [np.sum(plot_data['z'].v[:i]) for i in range(len(plot_data['z'].v))]
        plot_data['mag'] = plot_data.magnitude('m')

        if norm:
            norm_factor = max(plot_data['mag'].v)
        else:
            norm_factor = 1

        plt.plot(plot_data['mean_window'].v, plot_data['mag'].v / norm_factor, label='pARM acquisition')

        if not rtn:
            plt.show()


    def plt_acq_spec(self, subtract_af3=True, norm=True):
        self.plt_parm_spectra(subtract_af3=subtract_af3, rtn=True, norm=norm, fill=True)
        self.plt_parm_acquisition(subtract_af3=subtract_af3, rtn=True, norm=norm)
        plt.xlabel('AF field [mT]')
        plt.grid()
        plt.show()