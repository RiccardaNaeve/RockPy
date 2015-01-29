__author__ = 'mike'
import sample_group

if __name__ == '__main__':
    sg = sample_group.get_thellier_samplegroup()
    s = sg.mean_sample()
    print s.filtered_data
    print s.calc_all()
    print s.get_mean_results()