__author__ = 'wack'

from RockPy.Structure.sample import Sample
from RockPy.Visualize import demag
import matplotlib.pyplot as plt


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
        csample.add_measurement(mfile=cfC, mtype='afdemag', machine='cryomag', mag_method='IRM', demag_type='y', suffix='y')
        csample.add_measurement(mfile=cfC, mtype='afdemag', machine='cryomag', mag_method='IRM', demag_type='z', suffix='z')

    #print m.data
    demag.AfDemag(bsamples, norm='max')
    #demag.AfDemag(csamples, norm='max')

    # save plots AF demag plots for all samples
    if False:
        for s in csamples:
            demag.AfDemag(s, plot='save')
        for s in bsamples:
            demag.AfDemag(s, plot='save')





    #plt.plot(m.data['field'].v, m.data['m'].v)
    #plt.show()

if __name__ == '__main__':
    test()