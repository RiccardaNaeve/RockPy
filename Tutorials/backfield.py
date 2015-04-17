__author__ = 'volk'
import numpyson
import RockPy
from RockPy.Structure.sample import Sample
def test():
    # define measurement data file
    vftb_file = 'test_data/MUCVFTB_test.coe'

    # create a sample
    sample = Sample(name='vftb_test_sample')

    # add measurement
    M = sample.add_measurement(mtype='backfield', mfile=vftb_file, machine='vftb', suffix='test 1 none')


    sg = RockPy.SampleGroup(sample_list=sample)
    study = RockPy.Study(samplegroups=sg)
    # get bcr
    M.calculate_bcr()  # prints the linear interpolation of the value (internal calculation)
    print 'bcr', M.bcr  # returns the calculated value
    print M.s300  # returns the S300 value

    M.calc_all()  # calculates all possible results using standard parameters
    print M.results  # returns the calculated value
    # rudimentary plot
    M.plt_backfield()
    sample.calc_all()
if __name__ == '__main__':
    test()