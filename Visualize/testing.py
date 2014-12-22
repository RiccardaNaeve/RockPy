__author__ = 'mike'
import RockPy
import RockPy.Tutorials.sample_group
import RockPy.VisualizeV2.paleointensity
import RockPy.VisualizeV2.combined
import RockPy.VisualizeV2.base


def Day1977():
    SG = RockPy.Tutorials.sample_group.get_hys_cor_irm_rmp_sample_group()
    ST = RockPy.Study(name='day_plot', samplegroups=SG)
    S = SG.sample_list[0]
    # plot = RockPy.Visualize.combined.Day1977(S)
    # print plot.get_plot_samples()
    # plot = RockPy.Visualize.combined.Day1977(SG)
    # print plot.get_plot_samples()
    plot = RockPy.VisualizeV2.combined.Day1977(ST)
    print plot.get_plot_samples()


if __name__ == '__main__':
    Day1977()