__author__ = 'volk'
import numpyson

from RockPy.Structure.project import Sample
def test():
    # define measurement data file
    vftb_file = 'test_data/MUCVFTB_test2.coe'

    # create a sample
    sample = Sample(name='vftb_test_sample')

    # add measurement
    M = sample.add_measurement(mtype='backfield', mfile=vftb_file, machine='vftb')
    print M
    d = numpyson.dumps(M)

    print d
    M2 = numpyson.loads(d)
    print M2

    # get bcr
    M.calculate_bcr()  # prints the linear interpolation of the value (internal calculation)
    print 'bcr', M.bcr  # returns the calculated value
    # print M.s300  # returns the S300 value

    M.calc_all()  # calculates all possible results using standard parameters
    # print M.results  # returns the calculated value
    # rudimentary plot
    # M.plt_backfield()

if __name__ == '__main__':
    test()