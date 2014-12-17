__author__ = 'volk'
import RockPy

def test():
    vftb_file = 'test_data/MUCVFTB_test.hys'
    vsm_file = 'test_data/MUCVSM_test.hys'

    sample = RockPy.Sample(name='vftb_test_sample')
    sample2 = RockPy.Sample(name='vsm_test_sample')

    M = sample.add_measurement(mtype='hysteresis', mfile=vftb_file, machine='vftb')
    M = sample2.add_measurement(mtype='hysteresis', mfile=vsm_file, machine='vsm')

    study = RockPy.Study(samplegroups=[sample, sample2])

    RockPy.save(study, file_name='test.rpy')

    study2 = RockPy.load(file_name='test.rpy')
    print study2
if __name__ == '__main__':
    test()