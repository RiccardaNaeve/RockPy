from unittest import TestCase
import RockPy
import RockPy.Tutorials.sample

__author__ = 'mike'


class TestSampleGroup(TestCase):
    # def setUp(self):
    # self.s1 = RockPy.Sample('sample1')
    #     self.s2 = RockPy.Sample('sample2')
    #     self.s3 = RockPy.Sample('sample3')
    #     self.s4 = RockPy.Sample('sample4')
    #     self.group = RockPy.SampleGroup(sample_list=[self.s1, self.s2, self.s3, self.s4])

    # def test_add_samples(self):
    #     group = RockPy.SampleGroup(sample_list=[self.s1, self.s2, self.s3, self.s4])
    #     self.assertEquals(['sample1', 'sample2', 'sample3', 'sample4'], sorted(group.sdict.keys()))
    #     self.assertEquals([self.s1, self.s2, self.s3, self.s4], group.slist)
    #     # check if successfully added to sample.sgroups
    #     self.assertTrue(self.group in self.s1.sgroups)
    #
    # def test_remove_samples(self):
    #     self.group.remove_samples(s_list='sample1')
    #     self.assertEquals(['sample2', 'sample3', 'sample4'], sorted(self.group.sdict.keys()))
    #     self.assertEquals([self.s2, self.s3, self.s4], self.group.slist)
    #
    #     # check if successfully removed from sample.sgroups
    #     self.assertTrue(self.group not in self.s1.sgroups)


    # def test_average_sample(self):
    #     s = RockPy.Tutorials.sample.get_sample_with_multiple_hys()
    #     sg = RockPy.SampleGroup(sample_list=[s, s])
    #
    #     mean = sg.mean_sample(interpolate=False)
    #     print mean.mean_measurements


    def test_info_dict(self):
        s = RockPy.Tutorials.sample.get_sample_with_multiple_hys()
        sg = RockPy.SampleGroup(sample_list=[s, s])

        s_keys, sg_keys = [], []

        for mtype in s.info_dict['mtype_ttype_tval'].keys():
            for ttype in s.info_dict['mtype_ttype_tval'][mtype].keys():
                for tval in s.info_dict['mtype_ttype_tval'][mtype][ttype].keys():
                    s_keys.append('_'.join([mtype, ttype, str(tval)]))
                    
        for mtype in sg.info_dict['mtype_ttype_tval'].keys():
            for ttype in sg.info_dict['mtype_ttype_tval'][mtype].keys():
                for tval in sg.info_dict['mtype_ttype_tval'][mtype][ttype].keys():
                    sg_keys.append('_'.join([mtype, ttype, str(tval)]))

        # self.assertEqual(sorted(s_keys), sorted(sg_keys))
