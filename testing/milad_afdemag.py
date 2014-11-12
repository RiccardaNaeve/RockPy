__author__ = 'wack'

from RockPy.Structure.project import Sample
from RockPy.Visualize import demag


def test():
    basenames = ('DA6', 'DA7', 'HA2', 'HA3', 'HA6', 'HA8', 'HA9', 'TA1', 'TA3', 'TA4', 'TA6', 'TA7')
    bnames = [bn+'B' for bn in basenames]
    cnames = [bn+'C' for bn in basenames]

    cfB = 'test_data/milad/groupB.txt'
    cfC = 'test_data/milad/groupC.txt'

    # create sample
    bsamples = [Sample(name=n) for n in bnames]
    csamples = [Sample(name=n) for n in cnames]

    for bsample in bsamples:
        bsample.add_measurement(mfile=cfB, mtype='afdemag', machine='cryomag', mag_method='IRM', demag_type='x', suffix='x')
        bsample.add_measurement(mfile=cfB, mtype='afdemag', machine='cryomag', mag_method='IRM', demag_type='y', suffix='y')
        bsample.add_measurement(mfile=cfB, mtype='afdemag', machine='cryomag', mag_method='IRM', demag_type='z', suffix='z')

    for csample in csamples:
        csample.add_measurement(mfile=cfC, mtype='afdemag', machine='cryomag', mag_method='IRM', demag_type='x', suffix='x')
        #csample.add_measurement(mfile=cfC, mtype='afdemag', machine='cryomag', mag_method='IRM', demag_type='y', suffix='y')
        #csample.add_measurement(mfile=cfC, mtype='afdemag', machine='cryomag', mag_method='IRM', demag_type='z', suffix='z')

    demag.AfDemag(bsamples)
    demag.AfDemag(csamples)


if __name__ == '__main__':
    test()