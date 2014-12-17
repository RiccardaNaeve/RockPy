__author__ = 'volk'
import matplotlib.pyplot as plt
import numpy as np

import base
from RockPy.Structure.data import RockPyData


class ThermoCurve(base.Measurement):
    def __init__(self, sample_obj,
                 mtype, mfile, machine,
                 **options):
        super(ThermoCurve, self).__init__(sample_obj, mtype, mfile, machine)

        # ## initialize
        self.data = None


    def format_vftb(self):
        data = self.machine_data.out_thermocurve()
        header = self.machine_data.header
        if len(data) > 2:
            self.log.warning('LENGTH of machine.out_thermocurve =! 2. Assuming data[0] = heating data[1] = cooling')
        if len(data) > 1:
            self.up_temp = RockPyData(column_names=header, data=data[0])
            self.down_temp = RockPyData(column_names=header, data=data[1])
        else:
            self.log.error('LENGTH of machine.out_thermocurve < 2.')

    def format_vsm(self):
        data = self.machine_data.out_thermocurve()
        header = self.machine_data.header
        segments = self.machine_data.segment_info

        ut = [i for i, v in enumerate(segments['initial temperature'])
              if segments['initial temperature'][i] < segments['final temperature'][i]]
        dt = [i for i, v in enumerate(segments['initial temperature'])
              if segments['initial temperature'][i] > segments['final temperature'][i]]


        up_data = np.array([data[i] for i in ut])
        up_data = [j for i in up_data for j in i]
        down_data = [data[i] for i in dt]
        down_data = [j for i in down_data for j in i]

        self.up_temp = RockPyData(column_names=header, data=up_data)
        self.up_temp.rename_column('temperature', 'temp')
        self.up_temp.rename_column('moment', 'mag')

        self.down_temp = RockPyData(column_names=header, data=down_data)
        self.down_temp.rename_column('temperature', 'temp')
        self.down_temp.rename_column('moment', 'mag')

    @property
    def ut(self):
        return self.up_temp

    @property
    def dt(self):
        return self.down_temp


    def plt_thermocurve(self):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(self.ut['temp'].v, self.ut['mag'].v, '-', color='red')
        ax.plot(self.dt['temp'].v, self.dt['mag'].v, '-', color='blue')
        ax.grid()
        # ax.axhline(0, color='#808080')
        # ax.axvline(0, color='#808080')

        unit = 'T'
        field = np.mean(self.ut['field'].v)

        if field < 0.01:
            field *= 1000.
            unit = 'mT'

        ax.text(0.01, 1.01, 'mean field: %.3f %s' % (field, unit),  # replace with data.unit
                verticalalignment='bottom', horizontalalignment='left',
                transform=ax.transAxes,

                )
        ax.set_xlabel('Temperature [%s]' % ('C'))  # todo data.unit
        ax.set_ylabel('Magnetic Moment [%s]' % ('Am2'))  # todo data.unit
        ax.set_title('Thermocurve %s' %self.sample_obj.name)

        plt.show()
