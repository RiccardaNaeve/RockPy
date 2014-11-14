__author__ = 'volk'
from RockPy.Structure.project import Sample
# thellier output file from cryomag

def test():
    cryomag_file = 'test_data/NLCRY_Thellier_test.TT'
    cryomag_file = '/Users/mike/PycharmProjects/RockPy/testing/test_data/NLCRY_Thellier_test.TT'

    # creating a sample
    sample = Sample(name='1a')

    # adding the measurement to the sample
    M = sample.add_measurement(mtype='thellier', mfile=cryomag_file, machine='cryomag')

    print 'calculation of slope'
    print 'just returning the standard values'
    print M.result_slope()
    print M.slope
    # print 'recalculating with different parameters'
    # print M.result_slope(t_min=300)
    # print 'calculating slope 1: t_min=400'
    # M.calculate_slope(t_min=400, component='z')  # calculation with non standard parameters
    # print 'returning calculation'
    # print M.result_slope(), M.result_sigma()
    #
    # print 'getting results -> simple calculation with standard parameters'
    # print M.result_slope(), M.result_sigma(), M.result_y_int(), M.result_x_int()
    #
    # print M.result_b_anc(t_min=300)
    # print M.result_sigma_b_anc(t_min=300)
    # M.calc_all()
    # print M.results
    # print M.calculate_y_dash()
    # plotting dunlop plot
    # M.plt_dunlop()

    # plotting arai diagram
    # M.plt_arai()
    # M.calc_all()
    # print M.results
if __name__ == '__main__':
    test()