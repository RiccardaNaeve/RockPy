__author__ = 'volk'
from Structure.project import Sample

def test():
    vftb_file = 'test_data/MUCVFTB_test.irm'

    sample = Sample(name='vftb_test_sample')

    M = sample.add_measurement(mtype='irm', mfile=vftb_file, machine='vftb')
    M.calc_all()
    print M.results
    M.plt_irm()

if __name__ is '__main__':
    test()