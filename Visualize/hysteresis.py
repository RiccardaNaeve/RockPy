__author__ = 'mike'
import base
import Features.hysteresis


class Hysteresis(base.Generic):
    _required = ['hys']


    def initialize_visual(self):
        self.add_plot()
        self.ax = self.figs[self.name][0].gca()
        self.standard_features = [self.feature_hys, self.feature_virgin]
        self.single_features = [self.feature_grid, self.feature_zero_lines]
        self.xlabel = 'Field'
        self.ylabel = 'Moment'

    def feature_hys(self, hys_obj, **plt_opt):
        print hys_obj
        hys_obj = hys_obj.normalize(**self.norm)
        lines, texts = Features.hysteresis.df_branch(self.ax, hys_obj, **plt_opt)
        self._add_line_text_dict(lines, texts)
        lines, texts = Features.hysteresis.uf_branch(self.ax, hys_obj, **plt_opt)
        self._add_line_text_dict(lines, texts)

    def feature_virgin(self, hys_obj, **plt_opt):
        if hys_obj.virgin:
            lines, texts = Features.hysteresis.virgin_branch(self.ax, hys_obj, **plt_opt)
            self._add_line_text_dict(lines, texts)

    def feature_zero_lines(self):
        pass
