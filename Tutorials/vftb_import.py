__author__ = 'volk'
import RockPy
import os.path


def test():
    dfile = os.path.join(RockPy.test_data_path, 'vftb', 'MUCVFTB_test.rmp')

    sample = RockPy.Sample(name='vftb_test')

    M = sample.add_measurement(mtype='thermocurve', mfile=dfile, machine='vftb')

    M.plt_thermocurve()
    # plt.plot(field, diff/max(diff))
    # plt.plot(field, rev/max(rev))
    # plt.show()
    # print M.up_field['field']


if __name__ == '__main__':
    test()