__author__ = 'volk'
import os
from os.path import join
import RockPy
import itertools
from copy import deepcopy

def get_hys_all_sample():
    folder = RockPy.test_data_path
    S = RockPy.Sample(name='test_sample',
                      mass=14.2, mass_unit='mg',
                      diameter=5.4, length_unit='nm',
                      height=23.8)

    mfile1 = join(folder, 'MUCVSM_test.hys')
    mfile2 = join(folder, 'MUCVFTB_test.hys')
    S.add_measurement(mtype='hys', mfile=mfile1, machine='vsm')
    S.add_measurement(mtype='hys', mfile=mfile2, machine='vftb')
    return S


def get_hys_coe_irm_rmp_sample():
    # folder = os.getcwd().split('RockPy')[0]
    folder = RockPy.test_data_path
    S = RockPy.Sample(name='test_sample')
    hys = join(folder, 'vftb', 'MUCVFTB_test.hys')
    coe = join(folder, 'vftb', 'MUCVFTB_test.coe')
    irm = join(folder, 'vftb', 'MUCVFTB_test.irm')
    rmp = join(folder, 'vftb', 'MUCVFTB_test.rmp')
    S.add_measurement(mtype='hys', mfile=hys, machine='vftb', treatments='temp_20_C; pressure_1_GPa')
    S.add_measurement(mtype='hys', mfile=hys, machine='vftb', treatments='temp_20_C')
    S.add_measurement(mtype='backfield', mfile=coe, machine='vftb')
    S.add_measurement(mtype='irm_acquisition', mfile=irm, machine='vftb')
    S.add_measurement(mtype='thermocurve', mfile=rmp, machine='vftb')
    return S


def get_af_demag_sample():
    folder = RockPy.test_data_path
    S = RockPy.Sample(name='WURM')
    af = join(folder, 'MUCSUSH_af_test.af')
    S.add_measurement(mtype='afdemag', mfile=af, machine='sushibar', magtype='irm')
    return S


def get_pmd_demag():
    S = RockPy.Sample(name='test_sample')
    dm = 'RockPy/tutorials.rst/test_data/HA2A.pmd'
    S.add_measurement(mtype='afdemag', mfile=dm, machine='pmd')
    return S

def get_sample_with_multiple_hys():
    sample = RockPy.Sample(name='test_sample',
                           mass=34.5, mass_unit='mg',
                           diameter=5.4, height=4.3, length_unit='mm',
                           treatments='pressure_0.0_GPa; temperature_300.0_C')
    vftb_hys_file = join(RockPy.test_data_path, 'vftb', 'MUCVFTB_test.hys')
    m1 = sample.add_measurement(mtype='hys', machine='vftb', mfile=vftb_hys_file,
                           treatments='pressure_0.0_GPa; temperature_100.0_C')

    m2 = deepcopy(m1)
    m3 = deepcopy(m2)

    for dtype in m2.data:
        for column in m2.data[dtype].column_names:
            m2.data[dtype][column] = 0.1 + m2.data[dtype][column].v

    for dtype in m3.data:
        for column in m3.data[dtype].column_names:
            m3.data[dtype][column] = 0.1 + m3.data[dtype][column].v
    return sample

def get_hys_with_multiple_cond():
    sample = RockPy.Sample(name='test_sample',
                           mass=34.5, mass_unit='mg',
                           diameter=5.4, height=4.3, length_unit='mm',
                           treatments='pressure_0.0_GPa; temperature_300.0_C')

    # vftb
    vftb_hys_file = join(RockPy.test_data_path, 'vftb', 'MUCVFTB_test.hys')

    sample.add_measurement(mtype='hys', machine='vftb', mfile=vftb_hys_file,
                           treatments='pressure_0.0_GPa; temperature_100.0_C')

    sample.add_measurement(mtype='hys', machine='vftb', mfile=vftb_hys_file,
                           treatments='pressure_1.0_GPa; temperature_200.0_C')

    sample.add_measurement(mtype='hys', machine='vftb', mfile=vftb_hys_file,
                           treatments='pressure_2.0_GPa; temperature_300.0_C')

    sample.add_measurement(mtype='hys', machine='vftb', mfile=vftb_hys_file,
                           treatments='pressure_3.0_GPa; temperature_400.0_C')

    sample.add_measurement(mtype='hys', machine='vftb', mfile=vftb_hys_file,
                           treatments='pressure_4.0_GPa; temperature_500.0_C')
    return sample


def test():
    sample = get_hys_with_multiple_cond()
    measurements = sample.measurements
    # sample.filter(ttype='temperature', tval=300.)
    # sample.recalc_info_dict()

if __name__ == '__main__':
    test()