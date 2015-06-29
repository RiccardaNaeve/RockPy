from unittest import TestCase
import os.path
import RockPy.file_operations
from pprint import pprint

__author__ = 'mike'


class Test_file_operations(TestCase):
    def test_get_info_from_fname(self):
        path = '/Users/mike/Dropbox/experimental_data/FeNiX/FeNi20J/1mT_hys/FeNi_FeNi20-Jd006\'-G03_HYS_VSM#61,8[mg]_[]_[]##STD019.002'
        compare = RockPy.file_operations.get_info_from_fname(path=path)
        compare.pop('idx')
        dictionary = dict(mtype='hys', mfile=path, machine='VSM',
                          name='FeNi20-Jd006\'-G03',
                          STD=19, sample_group='FeNi', series='',
                          mass_unit='mg', mass=61.8,
                          )
        self.assertEqual(dictionary, compare)


    def test_get_fname_from_info(self):
        info_dict = dict(sample_group='LF4C-HX', sample_name='1a', mtype='TT', machine='cry',
                         mass=320.0, mass_unit='mg', height=5.17, height_unit='mm', diameter=5.87,
                         series='pressure', svals=1.2, sunits='GPa', idx=0, std=19)

        gen_fname = RockPy.get_fname_from_info(**info_dict)

        info_dict.pop('height_unit')
        info_dict.pop('machine')
        info_dict.update(dict(length_unit='mm'))
        info_dict.update(dict(series='_'.join([info_dict.pop('series'),
                                               str(info_dict.pop('svals')).replace('.',','),
                                               info_dict.pop('sunits')])))

        info_dict['name'] = info_dict.pop('sample_name')

        info_dict['mtype']='thellier'

        idict = RockPy.get_info_from_fname(os.path.join(RockPy.test_data_path,gen_fname))
        idict.pop('mfile')
        idict.pop('machine')

        pprint(info_dict)
        pprint(idict)
        # self.maxDiff = None
        self.assertEqual(idict, info_dict)