__author__ = 'wack'

import numpy as np
from RockPy.Structure.sample import Sample
from RockPy.Measurements.anisotropy import Anisotropy
from RockPy.Structure.data import RockPyData
import RockPy.Visualize.anisotropy
import RockPy.Visualize.stereo
from random import random
from matplotlib.backends.backend_pdf import PdfPages

from matplotlib import pyplot


def test():
    """
    # define measurement data file
    ani_file1 = 'test_data/anisotropy/S1_isotropic_sushi_1D.ani'
    ani_file2 = 'test_data/anisotropy/S2_sushi.ani'

    # create a sample
    sample1 = Sample(name='S1')
    sample2 = Sample(name='S2')
    sample3 = Sample(name='S3')
    """

    def do_box_plot(axes, values, label, ylim):
        axes.boxplot(values, notch=1, whis=999999)  # whis high -> whiskers mark maximum and minimum data
        if ylim is not None:
            axes.set_ylim(ylim)
        pyplot.setp(axes.get_xticklabels(), visible=False)
        axes.set_xlabel(label)
        axes.set_xlim((0.9, 1.1))


    # create samples
    evals=(0.99, 1.01, 1.00)
    measerr=0.001

    samples = []
    for i in range(100):
        s = Sample(name=str(i))
        m = s.add_simulation(mtype='anisotropy', color=(random(), random(), random()), evals=evals,
                                mdirs=[[225.0, 0.0], [135.0, 0.0], [90.0, 45.0],
                                       [90.0, -45.0], [0.0, -45.0], [0.0, 45.0]],
                                measerr=measerr)

        samples.append(s)

    sg = RockPy.SampleGroup(sample_list=samples)
    study = RockPy.Study(samplegroups=sg)

    pdf_pages = PdfPages('out_sushi__ev%.2f_%.2f_%.2f_err%.3f.pdf' % (evals[0], evals[1], evals[2], measerr))


    startoffset = 0

    for s in samples:
        s.measurements[0]._data['data']['D'] = s.measurements[0]._data['data']['D'].v + startoffset-1


    # values for all offsets
    Ds, Tmeans, Pmeans, Lmeans, Fmeans, E12means, E13means, E23means, sdmeans, QFmeans = [], [], [], [], [], [], [], [], [], []


    for d in range(5):
        for s in samples:
            #modify reference directions
            #add to inclination
            #m._data['data']['I'] = m._data['data']['I'].v + 2
            #add to declination
            s.measurements[0]._data['data']['D'] = s.measurements[0]._data['data']['D'].v + 1

        aniplt = RockPy.Visualize.anisotropy.Anisotropy(study, plt_primary="samples", plt_secondary=None)

        # get figure
        fig1 = aniplt.figs[aniplt.name][0]

        L, F, T, P, E12, E13, E23, sd, QF = [], [], [], [], [], [], [], [], []

        samples[0].measurements[0].calculate_tensor()
        #print samples[0].measurements[0].results
        for s in samples:
            s.measurements[0].calculate_tensor()
            T.extend(s.measurements[0].results['T'].v)
            L.extend(s.measurements[0].results['L'].v)
            F.extend(s.measurements[0].results['F'].v)
            P.extend(s.measurements[0].results['P'].v)
            E12.extend(s.measurements[0].results['E12'].v)
            E13.extend(s.measurements[0].results['E13'].v)
            E23.extend(s.measurements[0].results['E23'].v)
            sd.extend(s.measurements[0].results['stddev'].v)
            QF.extend(s.measurements[0].results['QF'].v)


        fig2, axarr = pyplot.subplots(1, 9)
        do_box_plot(axarr[0], P, 'P', (.99, 1.15))
        do_box_plot(axarr[1], L, 'L', (.99, 1.15))
        do_box_plot(axarr[2], F, 'F', (.99, 1.15))
        do_box_plot(axarr[3], T, 'T', (-1.0, 1.0))
        do_box_plot(axarr[4], E12, 'E12', (0, 90))
        do_box_plot(axarr[5], E13, 'E13', (0, 90))
        do_box_plot(axarr[6], E23, 'E23', (0, 90))
        do_box_plot(axarr[7], sd, 'stddev', None)
        do_box_plot(axarr[8], QF, 'QF', None)



        pyplot.tight_layout()

        fig1.suptitle("sushi geometry, meas_err: %.3f, evals: %.2f,%.2f,%.2f, D offset: %d" %
                      (measerr, evals[0], evals[1], evals[2], d+startoffset))

        pdf_pages.savefig(fig1)
        pdf_pages.savefig(fig2)

        Pmeans.append(np.mean(P))
        Tmeans.append(np.mean(T))
        Lmeans.append(np.mean(L))
        Fmeans.append(np.mean(F))
        E12means.append(np.mean(E12))
        E13means.append(np.mean(E13))
        E23means.append(np.mean(E23))
        sdmeans.append(np.mean(sd))
        QFmeans.append(np.mean(QF))


        print d+startoffset
        Ds.append(d+startoffset)


    fig3, (axu, axd) = pyplot.subplots(2, 1)
    l = []
    l.append(axu.plot(Ds, Pmeans, color='blue', marker='+', label='P'))
    l.append(axu.plot(Ds, Lmeans, color='springgreen', marker='+', label='L'))
    l.append(axu.plot(Ds, Fmeans, color='forestgreen', marker='+', label='F'))
    axu2 = axu.twinx()
    l.append(axu2.plot(Ds, Tmeans, color='peru', marker='+', label='T'))
    axu.set_ylim((0.99, 1.15))
    axu2.set_ylim((-1.05, 1.05))

    axu.legend(loc='upper left', bbox_to_anchor=(0, 1.20), fancybox=True, shadow=True, ncol=10)
    axu2.legend(loc='upper right', bbox_to_anchor=(1.0, 1.20), fancybox=True, shadow=True)


    l.append(axd.plot(Ds, E12means, 'r+-', label='E12'))
    l.append(axd.plot(Ds, E13means, 'rx-', label='E13'))
    l.append(axd.plot(Ds, E23means, 'r*-', label='E23'))
    axd.set_ylim((0.0, 90.0))
    axd.legend(loc='lower center', bbox_to_anchor=(0.5, -0.3), fancybox=True, shadow=True, ncol=10)


    pdf_pages.savefig(fig3)
    pdf_pages.close()

if __name__ == '__main__':
    test()