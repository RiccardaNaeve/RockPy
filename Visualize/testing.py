__author__ = 'mike'
import RockPy
import RockPy.Tutorials.sample
import RockPy.Tutorials.sample_group
import RockPy.Visualize.paleointensity
import RockPy.Visualize.combined
import RockPy.Visualize.base


def Day1977():
    SG = RockPy.Tutorials.sample_group.get_hys_coe_irm_rmp_sample_group(load=False)
    ST = RockPy.Study(name='day_plot', samplegroups=SG)
    S = SG.sample_list[0]

    m = S.get_measurements('hysteresis')[0]

    m.show_plots()
    # plot = RockPy.Visualize.combined.Day1977(S)
    # plot.feature_day_grid()
    # plot = RockPy.Visualize.combined.Day1977(SG)
    # plot = RockPy.Visualize.combined.Day1977(ST)
    # plot.show()


def test():
    S = RockPy.Tutorials.sample.get_hys_all_sample()
    ms = S.get_measurements(mtype='hysteresis')
    results = S.mean_results(mlist=ms)
    print results

def Arai():
    S = RockPy.Tutorials.sample_group.get_thellier_samplegroup()
    ST = RockPy.Study(S, name='TT-test-ST')

    P = RockPy.Visualize.paleointensity.Arai(ST)
    P.add_all_samples()
    P.show()

if __name__ == '__main__':
    Day1977()
    # Arai()
    # test()