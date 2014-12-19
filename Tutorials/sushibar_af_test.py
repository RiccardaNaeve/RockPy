__author__ = 'mike'
from Structure.sample import Sample
from Visualize import demag


def test():
    data = 'test_data/MUCSUSH_af_test.af'
    S = Sample(name='WURM')
    M = S.add_measurement(mtype='afdemag', mfile=data, machine='SushiBar')
    # M.plt_afdemag()
    # print M.result_mdf(interpolation='smooth_spline')
    demag.AfDemag(S, norm='max', mdf_text=True, mdf_line=True, diff_fill=True, plot='save', smoothing=1, diff=1)


if __name__ == '__main__':
    test()