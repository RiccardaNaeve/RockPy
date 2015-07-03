import logging

from profilehooks import profile
from matplotlib import pyplot as plt

import RockPy
from RockPy.core import to_list
import RockPy.VisualizeV3.core
from RockPy.VisualizeV3.base import Visual

__author__ = 'mike'


class NewFigure(object):
    def __init__(self): #todo size of figure
        """
        Container for visuals.

        Parameters
        ----------

        """
        self.logger = logging.getLogger(__name__)
        self.logger.info('CREATING new figure')

        # create dictionary for visuals {visual_name:visual_object}
        self._visuals = []
        self._n_visuals = 0

        self.fig = plt.figure()  # initialize figure

    @property
    def visuals(self):
        return self._visuals

    def __getitem__(self, item):
        """
        Asking for an item from the plot will result in one of two things.
           1. If you ask for a name or an index, and the name or index are
        :param item:
        :return:
           Visual Object
        """
        # try:
        if item in self.vtypes:
            idx = [i for i, v in enumerate(self.vtypes) if v == item]
            return [self._visuals[i][2] for i in idx]
        if item in self.vnames:
            idx = self.vnames.index(item)
            return self._visuals[idx][2]
        if type(item) == int:
            return self._visuals[item][2]
        else:
            raise KeyError('%s can not be found' % item)

    # @profile
    def add_visual(self, visual, name=None, plt_input=None,
                   calculation_parameter=None,
                   **visual_opt):
        """
        adds a visual to the plot. This creates a new subplot.

        Parameters
        ----------

           visual: list, str
              name of visual to add.

        """
        input_exchange = []
        # convert visual to list
        visuals = to_list(visual)
        for visual in visuals:
            # check if visual exists otherwise don't create it
            if visual in Visual.inheritors():
                if not name:
                    name = visual
                n = self._n_visuals
                # create instance of visual by dynamically calling from inheritors dictionary
                visual_obj = Visual.inheritors()[visual](plt_input=plt_input, plt_index=n, fig=self, name=name,
                                                         calculation_parameter=calculation_parameter,
                                                         **visual_opt)
                self._visuals.append([name, visual, visual_obj])
                self._n_visuals += 1
            else:
                self.logger.warning('VISUAL << %s >> not implemented yet' % visual)
                self.logger.warning('\tIMPLEMENTED VISUALS: %s' % Visual.inheritors().keys())

                return
            
        self.fig = self._create_fig()
        return visual_obj

    @property
    def vnames(self):
        return [i[0] for i in self._visuals]

    @property
    def vtypes(self):
        return [i[1] for i in self._visuals]

    @property
    def vinstances(self):
        return [i[2] for i in self._visuals]

    def plt_all(self):
        for name, type, visual in self._visuals:
            visual.plt_visual()

    def _create_fig(self):
        """
        Wrapper that creates a new figure but first deletes the old one.
        """
        # closes old figure before it is actually shown
        plt.close(self.fig)
        # create new figure with appropriate number of subplots
        return RockPy.VisualizeV3.core.generate_plots(n=self._n_visuals)

    def get_xylims(self, visuals=None):
        xlim = []
        ylim = []
        #cycle throu visuals to get
        if not visuals:
            visuals = self.vinstances

        for visual in visuals:
            xlim.append(visual.ax.get_xlim())
            ylim.append(visual.ax.get_ylim())

        xlim = [min([i[0] for i in xlim]), max([i[1] for i in xlim])]
        ylim = [min([i[0] for i in ylim]), max([i[1] for i in ylim])]
        return xlim, ylim

    def show(self, set_xlim=None, set_ylim=None, equal_lims=False):
        self.plt_all()
        if set_xlim == 'equal' or set_ylim == 'equal' or equal_lims:
            xlim, ylim = self.get_xylims()

            #cycle throu visuals to set
            for name, type, visual in self._visuals:
                if set_xlim == 'equal' or equal_lims:
                    visual.ax.set_xlim(xlim)
                if set_ylim == 'equal' or equal_lims:
                    visual.ax.set_ylim(ylim)

        # check if two entries and each is float or int
        if set_xlim:
            if len(set_xlim) == 2 and any(isinstance(i, (float, int)) for i in set_xlim):
                for name, type, visual in self._visuals:
                    visual.ax.set_xlim(set_xlim)
        # check if two entries and each is float or int
        if set_ylim:
            if len(set_ylim) == 2 and any(isinstance(i, (float, int)) for i in set_ylim):
                for name, type, visual in self._visuals:
                    visual.ax.set_ylim(set_ylim)

        plt.tight_layout()
        plt.show()
