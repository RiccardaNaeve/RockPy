__author__ = 'mike'
from Structure.sample import Sample

def test():
    data = 'test_data/MUCSPN_afdemag.jr6'

    S = Sample(name='VB')

    M = S.add_measurement(mtype='afdemag', machine='jr6', mfile=data)
    # M.plt_afdemag(norm=True)
    M.calc_all()
    print M.results

if __name__ == '__main__':
    test()