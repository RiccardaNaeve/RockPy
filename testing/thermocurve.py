__author__ = 'volk'
from Structure.sample import Sample


def test():
    vftb_file = 'test_data/MUCVFTB_test.rmp'
    sample = Sample(name='vftb_test_sample')

    M = sample.add_measurement(mtype='thermocurve', mfile=vftb_file, machine='vftb')
    M.plt_thermocurve()


if __name__ == "__main__":

    test()