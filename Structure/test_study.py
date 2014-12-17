from unittest import TestCase
import RockPy
import study

__author__ = 'mike'


class TestStudy(TestCase):
    def setUp(self):
        self.sample_group = RockPy.SampleGroup()
        self.sample = RockPy.Sample(name='test_sample')
        self.sample_group.add_samples(self.sample)
        self.study = RockPy.Study(self.sample_group)

    def test_save_to_file(self):
        self.study.save_study(folder='/Users/mike/Desktop/', name='test')


    def test__check_samplegroup_list(self):
        # test sample
        self.assertIsInstance(self.study._check_samplegroup_list(self.sample), list)
        # test sample_list
        self.assertIsInstance(self.study._check_samplegroup_list([self.sample, self.sample]), list)
        # test samplegroup
        self.assertIsInstance(self.study._check_samplegroup_list(self.sample_group), list)
        # test samplegroup_list
        self.assertIsInstance(self.study._check_samplegroup_list([self.sample_group, self.sample_group]), list)
        # test mixed_list
        self.assertIsNone(self.study._check_samplegroup_list([self.sample_group, self.sample]))
        # check if list of sample_groups is returned
        self.assertIsInstance(self.study._check_samplegroup_list([self.sample_group, self.sample_group])[0],
                              RockPy.SampleGroup)


    def test_add_samplegroup(self):
        study = RockPy.Study(samplegroups=self.sample_group)
        self.assertEqual(1, len(study.samplegroups))
        # add second sample_group
        study.add_samplegroup(self.sample_group)
        # adding two sample_groups should make three sample_groups because all_samplegroup is added automatically
        self.assertEqual(3, len(study.samplegroups))
