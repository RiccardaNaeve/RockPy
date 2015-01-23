__author__ = 'wack'

import numpy as np
from RockPy.Structure.sample import Sample


def test():
    # define measurement data file
    ani_file1 = 'test_data/anisotropy/S1_isotropic_sushi_1D.ani'
    ani_file2 = 'test_data/anisotropy/S2_sushi.ani'

    # create a sample
    sample = Sample(name='S1')

    # add measurement, read from file
    M1 = sample.add_measurement(mtype='anisotropy', mfile=ani_file2, machine='ani')

    mdata = {'mdirs': [[225.0, 0.0], [135.0, 0.0], [90.0, 45.0], [90.0, -45.0], [0.0, -45.0], [0.0, 45.0]],
             'measurements': np.array([1.1, 1.1, 1.1, 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 0.9, 0.9, 0.9])}

    M2 = sample.add_measurement(mtype='anisotropy', mdata=mdata)

    # print "M._data", M._data
    #sg = RockPy.SampleGroup(sample_list=sample)
    #study = RockPy.Study(samplegroups=sg)

    M1.calculate_tensor()
    M2.calculate_tensor()
    #print M1._data
    #M.calc_all()  # broken
    #print M.aniso_dict
    print M1.results
    print M2.results


if __name__ == '__main__':
    test()