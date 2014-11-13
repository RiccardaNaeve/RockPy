from unittest import TestCase

__author__ = 'mike'
from Structure.project import Sample

class TestAfDemag(TestCase):
    def setUp(self):
        #sample data files
        jr6_file = '../testing/test_data/MUCSPN_afdemag.jr6'
        cryomag_file = '../testing/test_data/NLCRYO_test.af'
        sushibar_file = '../testing/test_data/MUCSUSH_af_test.af'

        #creating samples
        self.jr6_sample = Sample(name='VA')
        self.sushibar_sample = Sample(name='WURM')
        self.cryomag_sample = Sample(name='DA6B')

        #adding measurements
        self.jr6_af = self.jr6_sample.add_measurement(mtype='afdemag', mfile=jr6_file, machine='jr6')
        self.cryomag_af = self.cryomag_sample.add_measurement(mtype='afdemag', mfile=cryomag_file, machine='cryomag', demag_type='x')
        self.sushibar_af = self.sushibar_sample.add_measurement(mtype='afdemag', mfile=sushibar_file, machine='sushibar')

    def test_calculate_mdf(self):
        self.cryomag_af.calculate_mdf()
        self.assertAlmostEqual(self.cryomag_af.result_mdf().v, 24.40, places=1)