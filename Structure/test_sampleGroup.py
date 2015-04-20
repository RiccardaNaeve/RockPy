from unittest import TestCase
import RockPy

__author__ = 'mike'


class TestSampleGroup(TestCase):
    def setUp(self):
        self.s1 = RockPy.Sample('sample1')
        self.s2 = RockPy.Sample('sample2')
        self.s3 = RockPy.Sample('sample3')
        self.s4 = RockPy.Sample('sample4')
        self.group = RockPy.SampleGroup(sample_list=[self.s1, self.s2, self.s3, self.s4])

    def test_add_samples(self):
        group = RockPy.SampleGroup(sample_list=[self.s1, self.s2, self.s3, self.s4])
        self.assertEquals(['sample1', 'sample2', 'sample3', 'sample4'], sorted(group.sdict.keys()))
        self.assertEquals([self.s1, self.s2, self.s3, self.s4], group.slist)
        # check if successfully added to sample.sgroups
        self.assertTrue(self.group in self.s1.sgroups)

    def test_remove_samples(self):
        self.group.remove_samples(s_list='sample1')
        self.assertEquals(['sample2', 'sample3', 'sample4'], sorted(self.group.sdict.keys()))
        self.assertEquals([self.s2, self.s3, self.s4], self.group.slist)

        # check if successfully removed from sample.sgroups
        self.assertTrue(self.group not in self.s1.sgroups)
