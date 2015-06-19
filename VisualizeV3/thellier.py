__author__ = 'mike'
import base
import Features.arai
import Features.dunlop
import Features.generic

class Arai(base.Visual):
    _required = ['thellier']

    def __init__(self, plt_input=None, plt_index=None, fig=None, name=None,
                 component='mag', tmin=0, tmax=700):
        super(Arai, self).__init__(plt_input=plt_input, plt_index=plt_index, fig=fig, name=name)

        # for Arai line calculation. If no parameters are given, standard is assumed
        self._calculation_parameter = dict(tmin=tmin, tmax=tmax, component=component)
        self.__dict__.update(self.calculation_parameter)

    def init_visual(self):
        ''' this part is needed by every plot, because it is executed automatically '''

        self.features = [self.feature_arai_points,
                         self.feature_arai_fit,
                         self.feature_ck_checks,
                         self.feature_add_temperatures,
                         ] #list containing all features that have to be plotted for each measurement

        self.single_features = []  # list of features that only have to be plotted one e.g. zero lines

        self.xlabel = 'pTRM gained'
        self.ylabel = 'NRM remaining'
        self.title = 'title'

    def feature_arai_points(self, mobj=None, **plt_opt):
        """
        Feature for plotting the points in the arai diagram. Calls the Feature.arai_points

        Parameters
        ----------
           mobj: RockPy.Measurement
              measurement object to be plotted
           plt_opt: plot options like

        """
        Features.arai.arai_points(self.ax,
                                  mobj=mobj,
                                  tmin=self.tmin, tmax=self.tmax, component=self.component,
                                  **plt_opt)

    def feature_arai_fit(self, mobj=None, **plt_opt):
        """
        Feature for plotting the best line fit in the arai diagram. Calls the Feature.arai_fit

        Parameters
        ----------
           mobj: RockPy.Measurement
              measurement object to be plotted
           plt_opt: plot options like

        """
        Features.arai.arai_fit(self.ax,
                               mobj=mobj,
                               tmin=self.tmin, tmax=self.tmax, component=self.component,
                               **plt_opt)

    def feature_ck_checks(self, m_obj=None, **plt_opt):
        Features.arai.add_ck_check(ax=self.ax,
                                   mobj=m_obj,
                                   component=self.component,
                                   **plt_opt)

    def feature_add_temperatures(self, m_obj=None, **plt_opt):
        Features.arai.add_temperatures(ax=self.ax,
                                       mobj=m_obj,
                                       component=self.component,
                                       **plt_opt)

    def feature_add_banc(self, m_obj=None, **plt_opt):
        Features.generic.add_result_text(ax=self.ax, mobj=m_obj, result='b_anc', text='$B_{anc}$: ', unit='$\\mu T$',
                                         **plt_opt)
