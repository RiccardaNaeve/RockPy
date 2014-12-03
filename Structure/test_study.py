from unittest import TestCase
import RockPy
import study
__author__ = 'mike'


class TestStudy(TestCase):
    def setUp(self):
        self.sample_group= RockPy.SampleGroup()
        self.sample = RockPy.Sample(name = 'test_sample')
        self.sample_group.add_samples(self.sample)
        self.study = RockPy.Study(self.sample_group)

    def test_save_to_file(self):
        print self.study.samplegroups.sample_names
        self.study.save_to_file(folder='/Users/mike/Desktop/', name='test')