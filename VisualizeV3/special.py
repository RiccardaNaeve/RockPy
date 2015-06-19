__author__ = 'mike'

import base
from profilehooks import profile

import RockPy
import RockPy.core

from Features import hysteresis
import numpy as np

class ResultVsSeries(base.Visual):

    # _required for searching through samples for plotables
    _required = []

    # @profile
    def __init__(self, result, series, plt_index,
                 plt_input=None, fig=None, name=None,
                 mtype = None, calculation_parameters=None):

        # initialize
        self.series = series # the series that should be plotted
        self.result = result # the result that should be plotted
        self.mtype = mtype # if provided, the visual will only take this mtypes into account

        # If there is no result stored in the measurement from an earlier call
        # e.g. hysteresis.calculate_ms(SOME_PARAMETERS)
        # self.calculation_parameters can provide the parameters for the calculation of the result.

        if not calculation_parameters: calculation_parameters = dict()
        self.calculation_parameters = calculation_parameters

        self.res_series_raw_data = dict() # dictionary for all series and results

        self.svals = [] # list of series values
        self.res_raw = [] # list of raw results, multiple entries for multiple measuremntes
        self.res = [] # list of mean of multiples from res_raw
        self.res_std = [] # list of std of multiples of res_raw

        super(ResultVsSeries, self).__init__(plt_input=plt_input, plt_index=plt_index, fig=fig)
        self.logger.info('CREATING new << %s Vs. %s >> fig' %(result, series))

    def plt_visual(self):
        self.add_standard()
        self.calculate_res_series_dict()

        for feature in self.features:
            feature()
        for feature in self.single_features:
            feature()
        xlim = self.ax.get_xlim()
        self.ax.set_xlim([xlim[0]-xlim[1]*0.05, xlim[1]*1.1])

    def calculate_res_series_dict(self):
        study, all_measurements = self.get_virtual_study()

        res_series_dict = dict()
        # plotting over study/ virtual study - > samplegroup / virtual SG ...
        for sg_idx, sg in enumerate(study):
            for sample_idx, sample in enumerate(sg):
                if not all_measurements:
                    measurements = sample.get_measurements(self.mtype) # if mtype = None -> returns all measurements
                else:
                    measurements = study[0][0]
                for m in measurements:
                    if m.has_result(self.result) and m.has_series(self.series):
                        sval = m.get_series(stypes=self.series)[0].value
                        res = m.calculate_result(result= self.result, **self.calculation_parameters).v[0]
                        res_series_dict.setdefault(sval, {}).setdefault(sample.name, []).append(res)
        print res_series_dict
        self.res_series_raw_data = res_series_dict
        self.svals = sorted(res_series_dict.keys())
        self.res_raw = [res_series_dict[i][j] for i in self.svals for j in res_series_dict[i]]
        self.res = [np.nanmean(i) for i in self.res_raw]
        self.res_std = [np.nanstd(i) for i in self.res_raw]

        return res_series_dict

    def init_visual(self):
        self.features = [self.feature_res_v_series]
        self.single_features = [self.feature_grid]

        self.title = '%s vs. %s' %(self.result, self.series)
        self.xlabel = self.series
        self.ylabel = self.result

    def feature_res_v_series(self, **plt_opt):
        self.ax.errorbar(self.svals, self.res, yerr=self.res_std)


