from unittest import TestCase
import os.path
import RockPy.file_operations

__author__ = 'mike'


class TestExtract_info_from_filename(TestCase):
    def test_extract_info_from_filename(self):
        path = '/Users/mike/Dropbox/experimental_data/FeNiX/FeNi20J/1mT_hys/FeNi_FeNi20-Jd006\'-G03_HYS_VSM#61,8[mg]_[]_[]##STD019.002'
        compare = RockPy.file_operations.extract_info_from_filename(path=path)
        compare.pop('idx')
        dictionary = dict(mtype='hys', mfile=path, machine='VSM',
                          name='FeNi20-Jd006\'-G03',
                          STD=19, sample_group='FeNi', series='',
                          mass_unit='mg', mass=61.8,
                          )
        self.assertEqual(dictionary, compare)


class TestGenerate_file_name(TestCase):
    def test_generate_file_name(self):
        info_dict = dict(sample_group='LF4C-HX', sample_name='1a', mtype='TT', machine='CRY',
                         mass=320, mass_unit='mg', height=5.17, height_unit='mm', diameter=5.87,
                         series='pressure', svals=1.2, sunits='GPa')

        gen_fname = RockPy.get_fname_from_info(**info_dict)
        print gen_fname
        idict = RockPy.extract_info_from_filename(os.path.join(RockPy.test_data_path,gen_fname))