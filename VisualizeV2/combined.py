__author__ = 'mike'
import numpy as np
import base
import RockPy.Functions.general
import RockPy.Measurements.hysteresis
import RockPy.Measurements.backfield
import RockPy.Plotting.hysteresis
import RockPy.Plotting.backfield
import RockPy.Plotting.day_plot


class Day1977(base.Generic):
    def initialize_visual(self):
        # super(Day1977, self).initialize_visual()
        self._required = ['hysteresis', 'backfield']
        self.add_plot()
        self.ax = self.figs[self.name][0].gca()
        RockPy.Plotting.day_plot.grid(self.ax)
        self.ax.set_xlim([0, 8])
        # self.ax.set_ylim([0, 0.6])
        self.ax.set_xlabel('$B_{cr} / B_c$')
        self.ax.set_ylabel('$M_{rs} / M_{s}$')

    def plotting(self, samples, **plt_opt):
        samples = self._to_sample_list(samples)
        for sample in samples:
            hys = sample.get_measurements(mtype='hysteresis')[0]
            coe = sample.get_measurements(mtype='backfield')[0]
            hys.calc_all()
            coe.calc_all()
            mrs_ms = hys.results['mrs'].v / hys.results['ms'].v
            bcr_bc = coe.results['bcr'].v / hys.results['bc'].v
            self.ax.plot(bcr_bc, mrs_ms, '.')

    def add_mixing_lines(self, mix_lines=None, **plt_opt):
        """
        MD/SD Mixing lines after Dunlup2002a
        """
        color = plt_opt.pop('color', 'k')
        zorder = plt_opt.pop('zorder', 0)
        marker = plt_opt.pop('marker', '.')
        ls = plt_opt.pop('ls', '--')

        if not mix_lines:
            mix_lines = ['all']
        else:
            mix_lines = RockPy.Functions.general._to_list(mix_lines)

        mix_line_data = {
            'sd_md1': np.array(
                [[1.259, 0.500], [1.296, 0.448], [1.337, 0.404], [1.404, 0.353], [1.473, 0.305], [1.569, 0.259],
                 [1.704, 0.211], [1.913, 0.163], [2.275, 0.114], [2.556, 0.090], [3.012, 0.067], [3.767, 0.043],
                 [4.155, 0.036], [4.601, 0.029], [5.366, 0.019]]),
            'langevin': np.array(
                [[1.259, 0.498], [1.412, 0.472], [1.619, 0.444], [1.941, 0.407], [2.351, 0.371], [2.715, 0.348],
                 [3.151, 0.324], [3.628, 0.302], [4.172, 0.281], [4.862, 0.261], [5.629, 0.239], [6.610, 0.217],
                 [7.823, 0.194], [9.424, 0.171], [11.432, 0.150], [14.353, 0.125], [18.754, 0.100]]),
            'sd_md2': np.array(
                [[1.431, 0.378], [1.508, 0.341], [1.601, 0.306], [1.702, 0.270], [1.810, 0.234], [1.973, 0.198],
                 [2.186, 0.161], [2.494, 0.125], [2.928, 0.090], [3.214, 0.072], [3.646, 0.053], [4.151, 0.036],
                 [5.025, 0.018]]),
            'sd_sp_93': np.array(
                [[2.820, 0.100], [4.035, 0.091], [6.375, 0.075], [13.641, 0.050], [35.278, 0.025], [99.429, 0.010]]),
            'SP_saturation_envelope': np.array(
                [[1.255, 0.498], [1.414, 0.473], [1.622, 0.450], [1.945, 0.426], [2.512, 0.402], [3.764, 0.376],
                 [7.411, 0.352], [8.874, 0.350], [17.269, 0.343], [34.897, 0.338], [57.714, 0.336]])
        }

        mix_line_text = {
            'sd_md1': {'texts': ['0%', '20%', '40%', '60%', '80%', '90%', '95%', '100%'],
                       'positions': [[1.259, 0.500], [1.337, 0.404], [1.473, 0.305], [1.704, 0.211], [2.275, 0.114],
                                     [3.012, 0.067], [4.155, 0.036], [5.366, 0.019]]},
            'sd_md2': {'texts': [], 'positions':[]},
            'langevin': {'texts': [], 'positions':[]},
            'sd_sp_93': {'texts': [], 'positions':[]},
            'SP_saturation_envelope': {'texts': [], 'positions':[]}
        }

        if 'all' in mix_lines:
            for name, data in mix_line_data.iteritems():
                self.ax.plot(data[:, 0], data[:, 1], color=color, marker=marker, ls=ls, zorder=zorder, **plt_opt)
                for idx, text in enumerate(mix_line_text[name]['texts']):
                    print text, mix_line_text[name]['positions'][idx]
                    self.ax.text(mix_line_text[name]['positions'][idx][0], mix_line_text[name]['positions'][idx][1], text,
                            verticalalignment='top', horizontalalignment='right',
                            # transform=self.ax.transAxes,
                            color='k', fontsize=10)

                else:
                    for line in mix_lines:
                        if line in mix_line_data:
                            data = mix_line_data[line]
                            self.ax.plot(data[:, 0], data[:, 1], color=color, marker=marker, ls=ls, zorder=zorder, **plt_opt)


class Fabian2010(base.Generic):
    def initialize_visual(self):
        super(Fabian2010, self).initialize_visual()
        self._required = ['hysteresis', 'backfield']
        self.add_plot()
        self.ax = self.figs['fabian2010'][0].gca()
        self.ax.set_xlabel('Field [T]')
        self.ax.set_ylabel('Moment [$Am2$]')
        self.ax.ticklabel_format(axis='both', style='sci', scilimits=(-2, 2))

    def plotting(self, sample):
        hys = sample.get_measurements(mtype='hysteresis')[0]
        coe = sample.get_measurements(mtype='backfield')[0]

        p_cor = self.options.get('paramag_correct', False)
        if p_cor:
            hys.simple_paramag_cor()

        RockPy.Plotting.hysteresis.zero_lines(self.ax, color='k')
        RockPy.Plotting.hysteresis.up_field_branch(self.ax, hysteresis_obj=hys, color='k')
        RockPy.Plotting.hysteresis.down_field_branch(self.ax, hysteresis_obj=hys, color='k')
        RockPy.Plotting.hysteresis.vigin_branch(self.ax, hysteresis_obj=hys, color='k')
        # RockPy.Plotting.hysteresis.hys_text(self.ax, hysteresis_obj=hys) #todo
        RockPy.Plotting.backfield.backfield(self.ax, coe, color='k')

