__author__ = 'volk'
import RockPy

def get_hys_all_sample():
    S = RockPy.Structure.sample.Sample(name='test_sample',
                                 mass=14.2, mass_unit='mg',
                                 diameter=5.4, length_unit='nm',
                                 height=23.8)
    mfile1 = '../Tutorials/test_data/MUCVSM_test.hys'
    mfile2 = '../Tutorials/test_data/MUCVFTB_test.coe'
    S.add_measurement(mtype='hysteresis', mfile=mfile1, machine='vsm')
    S.add_measurement(mtype='backfield', mfile=mfile2, machine='vftb')
    return S


def get_hys_coe_irm_rmp_sample():
    S = RockPy.Sample(name='test_sample')
    hys = './test_data/MUCVFTB_test.hys'
    coe = './test_data/MUCVFTB_test.coe'
    irm = './test_data/MUCVFTB_test.irm'
    rmp = './test_data/MUCVFTB_test.rmp'
    S.add_measurement(mtype='hysteresis', mfile=hys, machine='vftb')
    S.add_measurement(mtype='backfield', mfile=coe, machine='vftb')
    S.add_measurement(mtype='irm_acquisition', mfile=irm, machine='vftb')
    S.add_measurement(mtype='thermocurve', mfile=rmp, machine='vftb')
    return S

def test():
    S = get_hys_coe_irm_rmp_sample()
    study = RockPy.Study("study", samplegroups=S)
    #RockPy.save(study, 'hys_coe_irm_rmp.rpy')
    #print S.plottable
    print study.all_samplegroup.mtypes

if __name__ == '__main__':
    test()