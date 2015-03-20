__author__ = 'volk'
import RockPy

def test():
    vftb_file = 'test_data/MUCVFTB_test.irm'

    sample = RockPy.Sample(name='vftb_test_sample')

    M = sample.add_measurement(mtype='irm_acquisition', mfile=vftb_file, machine='vftb')
    print list(M.data['remanence']['field'].v)
    print list(M.data['remanence']['mag'].v)
    # M.calc_all()
    # print M.results
    # M.plt_irm()

if __name__ == '__main__':
    test()