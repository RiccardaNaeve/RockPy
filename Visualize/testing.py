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
    ms = S.get_measurements(mtype=['hysteresis', 'backfield'])
    results = S.mean_results_from_list(mlist=ms)
    print results
    # plot = RockPy.Visualize.combined.Day1977(S)
    # plot = RockPy.Visualize.combined.Day1977(SG)
    # plot = RockPy.Visualize.combined.Day1977(ST)
    # print(plot.input_type)
    # print plot.get_plot_samples()


def test():
    S = RockPy.Tutorials.sample.get_hys_all_sample()
    ms = S.get_measurements(mtype='hysteresis')
    results = S.mean_results_from_list(mlist=ms)
    print results

def Arai():
    pass

if __name__ == '__main__':
    Day1977()
    # test()