from RockPy.VisualizeV3 import NewFigure

__author__ = 'mike'
import RockPy
from os.path import join
from RockPy import VisualizeV3

if __name__  == '__main__':

    folder = join(RockPy.test_data_path, 'vsm', 'visualizev3_test')
    study = RockPy.Study(name='visualize V3 test')

    ''' SG 1 '''
    sg1 = RockPy.SampleGroup(name='SG1')
    s1a = RockPy.Sample(name='1a')
    s1b = RockPy.Sample(name='1b')
    sg1.add_samples([s1a, s1b])

    # adding measurements
    s1a.add_measurement(mtype='mass', value=62.7, unit='mg')
    h1a1 = s1a.add_measurement(mtype='hys', mfile=join(folder, 'FeNi_FeNi20-Jd001\'-G01_HYS_VSM#62,7[mg]_[]_[]##STD014.001'), machine='vsm')
    s1a.add_measurement(mtype='mass', value=51.5, unit='mg')
    h1a2 = s1a.add_measurement(mtype='hys', mfile=join(folder, 'FeNi_FeNi20-Jd001\'-G02_HYS_VSM#51,5[mg]_[]_[]##STD014.001'), machine='vsm')
    s1b.add_measurement(mtype='mass', value=60.0, unit='mg')
    h1b1 = s1b.add_measurement(mtype='hys', mfile=join(folder, 'FeNi_FeNi20-Jd120-G02_HYS_VSM#60,0[mg]_[]_[]##STD015.001'), machine='vsm')
    s1b.add_measurement(mtype='mass', value=50.8, unit='mg')
    h1b2 = s1b.add_measurement(mtype='hys', mfile=join(folder, 'FeNi_FeNi20-Jd120-G03_HYS_VSM#50,8[mg]_[]_[]##STD015.001'), machine='vsm')

    # adding series parapmeters
    h1a1.add_svalue(stype='mtime', sval=1)
    h1a2.add_svalue(stype='mtime', sval=1)
    h1b1.add_svalue(stype='mtime', sval=120)
    h1b2.add_svalue(stype='mtime', sval=120)
    #
    # ''' SG 2 '''
    # sg2 = RockPy.SampleGroup(name='SG2')
    # s2a = RockPy.Sample(name='2a', mass=1, mass_unit='mg')
    # s2b = RockPy.Sample(name='2b', mass=1, mass_unit='mg')
    # sg2.add_samples([s2a, s2b])
    # s2a.add_measurement(mtype='hysteresis', mfile=join(folder, 'LTPY_512,2a_HYS_VSM#[]_[]_[]#TEMP_300_K##STD000#.000'), machine='vsm')
    # s2a.add_measurement(mtype='hys', mfile=join(folder, 'LTPY_527,1a_HYS_VSM#[]_[]_[]#TEMP_300_K##STD000#.000'), machine='vsm')
    # s2b.add_measurement(mtype='hys', mfile=join(folder, 'LTPY_527,1a_HYS_VSM#[]_[]_[]#TEMP_300_K##STD000#.001'), machine='vsm')
    # s2b.add_measurement(mtype='hys', mfile=join(folder, 'LTPY_512,2a_HYS_VSM#[]_[]_[]#TEMP_300_K##STD000#.001'), machine='vsm')
    #
    # study.add_samplegroup([sg1, sg2])

    # print study.info()

    fig = NewFigure()
    h1 = fig.add_visual(visual='hysteresis', name='hys', plt_input=sg1)
    h2 = fig.add_visual(visual='hysteresis', name='hys', plt_input=sg1)
    # c1 = fig.add_visual(visual='backfield', name='coe', plt_input=sg1)
    s1 = fig.add_visual(visual='resultvsseries', result='bc', series='mtime', name='rvs', plt_input=sg1)
    s2 = fig.add_visual(visual='resultvsseries', result='bc', series='mtime', name='rvs', plt_input=sg1)
    # h2 = fig.add_visual(visual='hysteresis', name='hys2', plt_input=study)
    # h1.remove_single_feature(features=['grid'])
    # h1.remove_single_feature(features=['zero_lines'])
    # h1.add_single_feature(features=['zero_lines'])
    # h1.add_single_feature(features=['zero_lines', 'grid', 'nothing'])
    h1.normalize_all(reference='mass', norm_dtypes=['mag'])
    s1.normalize_all(reference='mass', norm_dtypes=['mag'])
    # h2.normalize_all(reference='down_field', vval=1, ntypes=['mag'])
    fig.show()