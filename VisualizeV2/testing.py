__author__ = 'mike'
import RockPy
import RockPy.Tutorials.sample_group
import RockPy.VisualizeV2.Paleointensity
import RockPy.VisualizeV2.combined

def Day1977():

    SG = RockPy.Tutorials.sample_group.get_hys_cor_irm_rmp_sample_group()
    study = RockPy.Study(name = 'day_plot', samplegroups=SG)
    sample = SG.sample_list[0]

    plot = RockPy.VisualizeV2.combined.Day1977(SG)
    print sample.plottable

if __name__ == '__main__':
    Day1977()