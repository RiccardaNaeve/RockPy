__author__ = 'wack'


def stereogrid(self, **plt_opt):
        # set the grid up
        Grid_D = np.arange(-180.0, 180.0, self.grid_D_spacing)
        Grid_I = np.arange(-90.0, 0.0, self.grid_I_spacing)

        # draw parallel and meridian grid, labels are off.
        self.stereomap.drawmeridians(Grid_D)
        self.stereomap.drawparallels(Grid_I, latmax=90)

def stereogridlabels(self, **plt_opt):
        # draw declination labels
        for D in np.arange(0, 360, self.grid_D_spacing):
            x = (0.55*np.sin(np.deg2rad(D)))+0.5
            y = (0.55*np.cos(np.deg2rad(D)))+0.5
            self.ax.text(x, y, "%i" % D, transform=self.ax.transAxes,
                         horizontalalignment='center', verticalalignment='center')

        # draw inclination labels
        for I in np.arange(self.grid_I_spacing, 90, self.grid_I_spacing):
            (x, y) = self.stereomap(0, -I)
            self.ax.text(x-0.1, y-0.07, "%i" % I, horizontalalignment='center', verticalalignment='center')


def points(self, m_obj, **plt_opt):
        d, i = (30, 50, 120, 150), (-10, -20, -30, -40)
        lines = self.ax.plot(*self.stereomap(d, i), **plt_opt)
        self._add_line_text_dict(m_obj.sample_obj.name, '_'.join(m_obj.stypes), '_'.join(map(str, m_obj.svals)), lines)
