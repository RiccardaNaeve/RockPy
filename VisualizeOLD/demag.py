__author__ = 'mike'
import matplotlib.pyplot as plt

import RockPy.PlottingOLD
from RockPy.PlottingOLD import af_demagnetization
import base
import numpy as np


class AfDemag(base.Generic):
    """
    Basic visualization for af_demag measurement class:

    :builtin options::
       mdf_line
       mdf_text
       diff
       diff_fill
       smoothing
    """

    def __init__(self, sample_list, norm='mass',
                 component='mag',
                 plot='show', folder=None, name='af-demagnetization',
                 plt_opt=None, style='screen',
                 **options):

        super(AfDemag, self).__init__(sample_list, norm=norm,
                                      plot=plot, folder=folder, name=name,
                                      plt_opt=plt_opt, style=style,
                                      **options)
        self.component = component
        self.show(**options)

        self.x_label = 'AF-Field [%s]' % ('mT')  # todo get_unit
        self.y_label = 'Magnetic Moment [%s]' % ('Am2')  # todo get_unit
        plt.title('%s' % " ,".join(self.sample_names))
        # plt.ylim([0, 1])
        if style == 'publication':
            self.setFigLinesBW()

        self.out()

    def show(self, **options):
        mdf_line = options.get('mdf_line', False)
        mdf_text = options.get('mdf_text', False)
        diff_fill = options.get('diff_fill', False)
        smoothing = options.get('smoothing', 1)
        diff = options.get('diff', 1)
        shift = 0
        for sample, measurements in self.get_measurement_dict(mtype='afdemag').iteritems():
            for measurement in measurements:
                plt_opt = self.get_plt_opt(sample, measurements, measurement)
                plt_opt.update({'zorder': 10})
                norm_factor = self.get_norm_factor(measurement)
                RockPy.PlottingOLD.af_demagnetization.field_mom(self.ax, measurement,
                                                             component=self.component, norm_factor=norm_factor,
                                                             **plt_opt)
                if mdf_line:
                    RockPy.PlottingOLD.af_demagnetization.mdf_line(self.ax, measurement,
                                                                component=self.component, norm_factor=norm_factor,
                                                                **plt_opt)
                if mdf_text:
                    RockPy.PlottingOLD.af_demagnetization.mdf_txt(self.ax, measurement,
                                                               component=self.component, norm_factor=norm_factor,
                                                               y_shift=shift,
                                                               **plt_opt)
                if diff_fill:
                    RockPy.PlottingOLD.af_demagnetization.diff_fill(self.ax, measurement,
                                                                 component=self.component, norm_factor=norm_factor,
                                                                 smoothing=smoothing, diff=diff,
                                                                 **plt_opt)
                shift += 0.1
        plt.grid()

    def get_norm_factor(self, measurement):

        if not self.norm:
            return [1, 1]

        if self.norm == 'max':
            idx = np.argmax(abs(measurement.data[self.component].v))
            nf = measurement.data[self.component].v[idx]
            return [1, nf]

        if self.norm == 'mass':
            # return [1, measurement.sample_obj.mass_kg.v]
            return [1, 1]

        if self.norm == 'is':
            if measurement.initial_state:
                return [1, max(measurement.initial_state.data[self.component].v)]
            else:
                return [1, max(measurement.data[self.component].v)]
