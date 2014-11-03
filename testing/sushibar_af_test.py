__author__ = 'mike'
from Structure.project import Sample
from Visualize import demag

def test():
    data = 'test_data/MUCSUSH_af_test.af'
    S = Sample(name='Wurm')
    M=S.add_measurement(mtype='afdemag', mfile=data, machine='SushiBar')
    # M.plt_afdemag()
    print M.result_mdf()
    demag.AfDemag(S, norm='max')
if __name__ == '__main__':
    test()