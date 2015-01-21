__author__ = 'wack'

import RockPy
from RockPy.Structure.sample import Sample


def test():
    # define measurement data file
    ani_file = '/home/wack/data/Python/svn/RockPy/Tutorials/test_data/anisotropy/S1_isotropic_sushi.ani'

    # create a sample
    sample = Sample(name='S1')

    # add measurement
    M = sample.add_measurement(mtype='anisotropy', mfile=ani_file, machine='ani')


    #sg = RockPy.SampleGroup(sample_list=sample)
    #study = RockPy.Study(samplegroups=sg)

    print sample

    # sample.calc_all()
if __name__ == '__main__':
    test()