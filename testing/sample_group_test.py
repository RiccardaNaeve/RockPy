__author__ = 'mike'
from Structure.samplegroup import SampleGroup

def test():
    sample_file = 'test_data/sample_info.csv'
    tt_data = 'test_data/NLCRY_Thellier_test.TT'

    SG = SampleGroup()
    SG.import_multiple_samples(sample_file=sample_file)

    for sample in SG.sample_list:
        M = sample.add_measurement(mtype='thellier', mfile=tt_data, machine='cryomag', suffix='p0')
        # M.plt_dunlop()

    SG.get_results(mtype='thellier')

if __name__ is '__main__':
    test()