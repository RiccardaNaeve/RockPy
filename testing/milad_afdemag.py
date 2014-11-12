__author__ = 'wack'

import time
from RockPy.Structure.project import Sample
from RockPy.Readin.cryomag import CryoMag

def test():
    start = time.clock()
    cfB = 'test_data/milad/groupB.txt'
    cfC = 'test_data/milad/groupC.txt'

    # creat sample
    sample = Sample(name='1a')

    CB = CryoMag(dfile=cfB, sample_name=sample.name)
    CC = CryoMag(dfile=cfC, sample_name=sample.name)

    print sample.calc_all()



if __name__ == '__main__':
    test()