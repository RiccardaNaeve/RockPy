__author__ = 'wack'

import numpy as np
from RockPy.Structure.sample import Sample
from RockPy.Measurements.anisotropy import Anisotropy
from RockPy.Structure.data import RockPyData
import RockPy.Visualize.anisotropy
import RockPy.Visualize.stereo
from random import random


def test():
    """
    # define measurement data file
    ani_file1 = 'test_data/anisotropy/S1_isotropic_sushi_1D.ani'
    ani_file2 = 'test_data/anisotropy/S2_sushi.ani'

    # create a sample
    sample1 = Sample(name='S1')
    sample2 = Sample(name='S2')
    sample3 = Sample(name='S3')
    """
    # create samples

    samples = []
    for i in range(100):
        s = Sample(name=str(i))
        m = s.add_simulation(mtype='anisotropy', evals=(1.01, 1.01, 0.99),
                                mdirs=[[225.0, 0.0], [135.0, 0.0], [90.0, 45.0],
                                       [90.0, -45.0], [0.0, -45.0], [0.0, 45.0]],
                                measerr=0.01)

        #modify reference directions
        #add to inclination
        #m._data['data']['I'] = m._data['data']['I'].v + 2
        #add to declination
        m._data['data']['D'] = m._data['data']['D'].v + 5


        samples.append(s)
        print s.measurements[0]._data['data']
        #print i
    """
    # add measurement, read from file
    #M1 = sample1.add_measurement(mtype='anisotropy', mfile=ani_file2, machine='ani')
    M3 = sample2.add_simulation(mtype='anisotropy', evals=(1.5, 1.5, 0.3),
                                mdirs=[[225.0, 0.0], [135.0, 0.0], [90.0, 45.0],
                                       [90.0, -45.0], [0.0, -45.0], [0.0, 45.0]])
    M4 = sample3.add_simulation(mtype='anisotropy', evals=(1.5, 1.3, 0.3),
                                mdirs=[[225.0, 0.0], [135.0, 0.0], [90.0, 45.0],
                                       [90.0, -45.0], [0.0, -45.0], [0.0, 45.0]])
    #M4 = sample2.add_simulation(mtype='anisotropy', evals=(1.1, 1.5, 1.3),
    #                            mdirs=[[225.0, 0.0], [135.0, 0.0], [90.0, 45.0],
    #                                   [90.0, -45.0], [0.0, -45.0], [0.0, 45.0]])

    # print "M._data", M._data



    #M1.calculate_tensor()
    #M3.calculate_tensor()
    #M4.calculate_tensor()

    #M1.calc_all()  # broken

    #print M1.results
    #print M3.results
    #print M4.results
    """
    sg = RockPy.SampleGroup(sample_list=samples)
    study = RockPy.Study(samplegroups=sg)
    plt = RockPy.Visualize.anisotropy.Anisotropy(sg, plt_primary='sample', plt_secondary=None)
    plt.show()

    for s in samples:
        s.measurements[0].calculate_tensor()
        print s.measurements[0].results['T']

if __name__ == '__main__':
    test()