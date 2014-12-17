__author__ = 'volk'
from Structure.sample import Sample

def test():
    dfile = 'test_data/MUCVFTB_test.rmp'

    sample = Sample(name='vftb_test')

    M = sample.add_measurement(mtype='thermocurve', mfile=dfile, machine='vftb')

    M.plt_thermocurve()
    # plt.plot(field, diff/max(diff))
    # plt.plot(field, rev/max(rev))
    # plt.show()
    # print M.up_field['field']

if __name__ == '__main__':
    test()