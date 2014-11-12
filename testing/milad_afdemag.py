__author__ = 'wack'

import time
from RockPy.Structure.project import Sample
from RockPy.Readin.cryomag import CryoMag
from Visualize import demag
def test():
    start = time.clock()
    cfB = 'test_data/milad/groupB.txt'
    cfC = 'test_data/milad/groupC.txt'

    # creat sample
    DA6B = Sample(name='DA6B')
    DA7B = Sample(name='DA7B')
    samples = [DA6B, DA7B]
    for sample in samples:
        sample.add_measurement(mfile=cfB, mtype='afdemag', machine='cryomag', mag_method='IRM', demag_type='x', suffix = 'x')
        sample.add_measurement(mfile=cfB, mtype='afdemag', machine='cryomag', mag_method='IRM', demag_type='y', suffix = 'y')
        sample.add_measurement(mfile=cfB, mtype='afdemag', machine='cryomag', mag_method='IRM', demag_type='z', suffix = 'z')

    demag.AfDemag(samples)


if __name__ == '__main__':
    test()