__author__ = 'mike'
import base
import Features.hysteresis


class Hysteresis(base.Generic):
    _required = ['hysteresis']

    def initialize_visual(self):
        self.add_plot()
        self.ax = self.figs[self.name][0].gca()
        self.standard_features = [self.feature_hys]


    def plotting(self, samples, **plt_opt):
        samples = self.get_plot_samples()
        hys_dict = None

        for sample in samples:
            hys = sample.get_measurements(mtype='hysteresis')
            hys_dict = sample.sort_mlist_in_ttype_dict(hys)
        for ttype in hys_dict:
            tvals = sorted(hys_dict[ttype].keys())
            colors = self.create_heat_color_map(value_list=tvals, reverse=False)
            for i, tval in enumerate(sorted(hys_dict[ttype].keys())):
                for h in hys_dict[ttype][tval]:
                    for feature in self.standard_features:
                        plt_opt = {'color':colors[i]}
                        feature(h, **plt_opt)

    def feature_hys(self, hys_obj, **plt_opt):
        lines, texts = Features.hysteresis.df_branch(self.ax, hys_obj, **plt_opt)
        lines, texts = Features.hysteresis.uf_branch(self.ax, hys_obj, **plt_opt)
        self._add_line_text_dict(lines, texts)