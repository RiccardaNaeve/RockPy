__author__ = 'wack'

import RockPy
from RockPy.Structure.sample import Sample


def test():
    # define measurement data file
    ani_file = 'test_data/anisotropy/S2_sushi.ani'

    # create a sample
    sample = Sample(name='S1')

    # add measurement
    M = sample.add_measurement(mtype='anisotropy', mfile=ani_file, machine='ani')
    #print "M._data", M._data
    #sg = RockPy.SampleGroup(sample_list=sample)
    #study = RockPy.Study(samplegroups=sg)

    #print sample
    M.calculate_tensor()
    print M.results

if __name__ == '__main__':
    test()