__author__ = 'wack'

import numpy as np
from RockPy.Structure.sample import Sample
from RockPy.Measurements.anisotropy import Anisotropy
import RockPy.Visualize.anisotropy
import RockPy.Visualize.stereo



def test():
    # define measurement data file
    ani_file1 = 'test_data/anisotropy/S1_isotropic_sushi_1D.ani'
    ani_file2 = 'test_data/anisotropy/S2_sushi.ani'

    # create a sample
    sample1 = Sample(name='S1')
    sample2 = Sample(name='S2')


    # add measurement, read from file
    M1 = sample1.add_measurement(mtype='anisotropy', mfile=ani_file2, machine='ani')

    mdata = {'mdirs': [[225.0, 0.0], [135.0, 0.0], [90.0, 45.0], [90.0, -45.0], [0.0, -45.0], [0.0, 45.0]],
             'measurements': np.array([1.1, 1.1, 1.1, 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 0.9, 0.9, 0.9])}

    print mdata

    #M2 = sample.add_measurement(mtype='anisotropy', mdata=mdata)

    M3 = sample2.add_simulation(mtype='anisotropy', evals=(1.5, 1.5, 0.3),
                                mdirs=[[225.0, 0.0], [135.0, 0.0], [90.0, 45.0],
                                       [90.0, -45.0], [0.0, -45.0], [0.0, 45.0]])


    # print "M._data", M._data
    sg = RockPy.SampleGroup(sample_list=(sample1, sample2))
    #study = RockPy.Study(samplegroups=sg)

    M1.calculate_tensor()
    #M2.calculate_tensor()
    M3.calculate_tensor()

    #M.calc_all()  # broken

    print M1.results
    #print M2.results
    print M3.results


    #plt = Stereo(sample)
    plt = RockPy.Visualize.anisotropy.Anisotropy(sample1, plt_primary='sample', plt_secondary=None)
    plt.show()

if __name__ == '__main__':
    test()