__author__ = 'mike'

__author__ = 'mike'
import base
import RockPy
import RockPy.core
from Features import hysteresis

class ResultVsTreatment(base.Visual):
    # _required for searching through samples for plotables
    _required = ['hys']

    def __init__(self, result, treatment, plt_index,
                 plt_input=None, plot=None, name=None,
                 mtype = None, calculation_parameters=None):

        # initialize
        self.treatment = treatment # the treatment that should be plotted
        self.result = result # the result that should be plotted
        self.mtype = mtype # if provided, the visual will only take this mtypes into account

        # If there is no result stored in the measurement from an earlier call
        # e.g. hysteresis.calculate_ms(SOME_PARAMETERS)
        # self.calculation parameters can provide the parameters for the calculation of the result.

        if not calculation_parameters: calculation_parameters = dict()
        self.calculation_parameters = calculation_parameters

        self.res_treat_data = dict() # dictionary for all treatments and results

        super(ResultVsTreatment, self).__init__(plt_input=plt_input, plt_index=plt_index, plot=plot)
        self.logger.info('CREATING new %s Vs. %s plot' %(result, treatment))

    def plt_visual(self):
        self.add_standard()
        study, all_measurements = self.get_virtual_study()

        res_treat_dict = dict()
        # plotting over study/ virtual study - > samplegroup / virtual SG ...
        for sg_idx, sg in enumerate(study):
            for sample_idx, sample in enumerate(sg):
                if not all_measurements:
                    measurements = sample.get_measurements(self.mtype) # if mtype = None -> returns all measurements
                else:
                    measurements = study[0][0]
                for m in measurements:
                    if m.has_result(self.result) and m.has_treatment(self.treatment):
                        tval = m.get_treatments(ttypes=self.treatment)
                        res = m.calculate_result(result = self.result, **self.calculation_parameters)
                        # res_treat_dict.setdefault(tval, []).append((res , m.sample_obj.name))


    def init_visual(self):
        self.features = [self.feature_res_v_treat]
        self.single_features = [self.feature_grid]

        self.xlabel = self.treatment
        self.ylabel = self.result

    def feature_res_v_treat(self, mobj, **plt_opt):
        print self.result
        print self.treatment


