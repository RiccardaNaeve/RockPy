__author__ = 'volk'
from Structure.sample import Sample

def test():
    # thellier output file from cryomag
    cryomag_file = 'test_data/NLCRY_Thellier_test.TT'
    cryomag_is_file = 'test_data/NLCRY_Thellier_is_test.TT'
    # creating a sample
    sample = Sample(name='1a')
    M = sample.add_measurement(mtype='thellier', mfile=cryomag_file, machine='cryomag')
    M.set_initial_state(mtype='trm', mfile=cryomag_is_file, machine='cryomag')
    M.add_sval(stype='pressure', sval=0.0)
    M.series[0].add_value('max_p', 0.6)
    M.series[0].add_value('tonnage', 3)
    M.series[0].add_value('release_time', 30.0)

    # M.plt_arai(norm='is')

    print M.th
    print M.initial_state.data

    print M.th / M.initial_state.data
    print M.initial_state.data['m'][0]
    print M.th / M.initial_state.data['m'][0]

if __name__ == '__main__':
    test()