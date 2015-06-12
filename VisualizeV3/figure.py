import logging
from matplotlib import pyplot as plt
import RockPy
from RockPy.core import _to_list
from RockPy.VisualizeV3.base import Visual

__author__ = 'mike'


class NewFigure(object):
    def __init__(self):
        """
        Container for visuals.

        Parameters
        ----------

        """
        self.logger = logging.getLogger(__name__)
        self.logger.info('CREATING new plot')

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

    def add_visual(self, visual, name=None, plt_input=None, **visual_opt):
        """
        adds a visual to the plot. This creates a new subplot.

        Parameters
        ----------

           visual: list, str
              name of visual to add.

        """
        input_exchange = []

        # convert visual to list
        visuals = _to_list(visual)
        for visual in visuals:
            # check if visual exists otherwise don't create it
            if visual in Visual.inheritors():
                if not name:
                    name = visual
                n = self._n_visuals
                # create instance of visual by dynamically calling from inheritors dictionary
                visual_obj = Visual.inheritors()[visual](plt_input=plt_input, plt_index=n, plot=self, name = name, **visual_opt)
                self._visuals.append([name, visual, visual_obj])
                self._n_visuals += 1
            else:
                self.logger.warning('VISUAL << %s >> not implemented yet' % visual)
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

    def show(self):
        self.plt_all()
        plt.show()