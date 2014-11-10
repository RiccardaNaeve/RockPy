__author__ = 'mike'
import matplotlib.pyplot as plt

import base
import arai


class Sample_sheet(base.Generic):
    def __init__(self, sample_list, norm='mass',
                 t_min=20, t_max=700, component='mag',
                 line=True, check=True,
                 plot='show', folder=None, name='arai plot',
                 plt_opt=None, style='screen',
                 **options):
        """

        implemented options:
           arai_line: adds the line fit to the arai_plot

        """

        super(Sample_sheet, self).__init__(sample_list, norm=None,
                                           plot=plot, folder=folder, name=name,
                                           plt_opt=plt_opt, style=style,
                                           create_fig=False, create_ax=False,
                                           **options)
        # parameter for PalInt calculations
        self.parameter = {'t_min': t_min,
                          't_max': t_max,
                          'component': component}



        # initializing figure and axis
        self.fig = plt.figure(figsize=(11.69, 8.27), dpi=100)

        # axis objects
        self.dunlop = plt.subplot2grid((5, 5), (0, 0), colspan=3, rowspan=2)
        self.difference = plt.subplot2grid((5, 5), (2, 0), colspan=3, rowspan=1)
        self.arai = plt.subplot2grid((5, 5), (3, 0), colspan=2, rowspan=2)
        self.decay = plt.subplot2grid((5, 5), (3, 2), rowspan=2, colspan=2)
        self.zijderveld_ptrm = plt.subplot2grid((5, 5), (0, 3))
        self.zijderveld_th = plt.subplot2grid((5, 5), (0, 4))
        self.stereo_ptrm = plt.subplot2grid((5, 5), (1, 3))
        self.stereo_th = plt.subplot2grid((5, 5), (1, 4))

        plt.tight_layout()
        self.show(**options)
        self.out('nolable')

    def show(self, **options):
        self.dunlop.set_title('dunlop')
        self.arai.set_title('arai')
        self.difference.set_title('difference')
        self.decay.set_title('decay')
        self.zijderveld_th.set_title('TH')
        self.zijderveld_ptrm.set_title('PTRM')
        self.stereo_th.set_title('TH')
        self.stereo_ptrm.set_title('TH')

        if len(self.sample_list) > 1:
            self.log.warning('MORE than one sample, using first')

        sample = self.sample_list[0]
        # thellier_objs = sample.get_measurements(mtype='thellier')
        # for thellier in thellier_objs:
        arai.Arai(sample, plot='get_ax', fig=self.fig, ax=self.arai)
            # self.dunlop = arai.Arai(sample, plot='None', fig=self.fig, ax = self.arai).get_ax()
