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
                          name = 'FeNi20-Jd006\'-G03',
                          STD=19, sample_group='FeNi', series='',
                          mass_unit = 'mg', mass = 61.8,
                          )
        self.assertEqual(dictionary, compare)

        folder = os.path.split(path)[0]
        fname = os.path.split(path)[1]

        compare = RockPy.file_operations.extract_info_from_filename(fname=fname, folder=folder)
        compare.pop('idx')

        self.assertEqual(dictionary, compare)
