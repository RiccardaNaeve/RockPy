__author__ = 'mike'
import RockPy
import sample
from os.path import join
import os


def get_thellier_samplegroup():
    folder = RockPy.test_data_path

    sample_file = join(folder, 'sample_info.csv')
    tt_data = join(folder, 'NLCRY_Thellier_test.TT')

    SG = RockPy.SampleGroup(name='TT-test-SG')
    SG.import_multiple_samples(sample_file=sample_file)
    for sample in SG.sample_list:
        M = sample.add_measurement(mtype='thellier', mfile=tt_data, machine='cryomag', suffix='p0')
    return SG


def get_hys_coe_irm_rmp_sample_group(load=False):
    if load:
        SG = RockPy.load(file_name='hys_coe_irm_rmp.rpy')
    else:
        S = sample.get_hys_coe_irm_rmp_sample()
        SG = RockPy.SampleGroup(name='hys/coe/irm/rmp', sample_list=S)
        study = RockPy.Study(SG)
        RockPy.save(study, file_name='hys_coe_irm_rmp.rpy')
    return SG


def test():
    # SG = get_thellier_samplegroup()
    # SG = get_hys_coe_irm_rmp_sample_group()
    S = RockPy.load('hys_coe_irm_rmp.rpy', '/Users/mike/Desktop/')


if __name__ == '__main__':
    test()