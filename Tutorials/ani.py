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
    evals=(1.10, 1.10, 0.90)
    measerr=0.01
    method='proj'  # 'proj' or 'full'

    samples = []
    for i in range(100):
        s = Sample(name=str(i))
        m = s.add_simulation(mtype='anisotropy', color=(random(), random(), random()), evals=evals,
                                mdirs=[[225.0, 0.0], [45.0, 0.0], [135.0, 0.0], [315.0, 0.0], [90.0, 45.0], [270.0, -45.0],
                                       [90.0, -45.0], [270.0, 45.0], [0.0, -45.0], [180.0, 45.0], [0.0, 45.0], [180.0, -45.0]],
                                measerr=measerr)

        samples.append(s)

    sg = RockPy.SampleGroup(sample_list=samples)
    study = RockPy.Study(samplegroups=sg)

    #filename = 'out_sushi__ev%.2f_%.2f_%.2f_err%.3f.pdf' % (evals[0], evals[1], evals[2], measerr)
    filename = 'out_sushi0__45anti_I_var_ev%.2f_%.2f_%.2f_err%.3f_%s.pdf' % (evals[0], evals[1], evals[2], measerr, method)
    print "writing to %s" % filename

    pdf_pages = PdfPages(filename)


    # values for all offsets
    Ds, Tmedians, Pmedians, Lmedians, Fmedians, E12medians, E13medians, E23medians, sdpermedians, QFmedians = [], [], [], [], [], [], [], [], [], []
    eval1_err_per_medians, eval2_err_per_medians, eval3_err_per_medians = [], [], []

    # make numbers formatting float
    samples[0].measurements[0]._data['data'].showfmt['floatfmt'] = '.1f'
    samples[0].measurements[0]._data['data'].showfmt['show_rowlabels'] = False

    for d in range(10):
        if d != 0:
            for s in samples:
                #modify reference directions
                #add to inclination
                #m._data['data']['I'] = m._data['data']['I'].v + 2
                #add to declination
                refI = s.measurements[0]._data['data']['I'].v
                refD = s.measurements[0]._data['data']['D'].v
                #print refD
                #change all declinations
                #refD += 1
                refI[8] += 1
                refI[9] -= 1
                #change declination of position 3
                #refD[2] += 1

                s.measurements[0]._data['data']['D'] = refD
                s.measurements[0]._data['data']['I'] = refI



        aniplt = RockPy.Visualize.anisotropy.Anisotropy(study, plt_primary="samples", plt_secondary=None, method=method)

        # get figure
        fig1 = aniplt.figs[aniplt.name][0]
        fig1.text(0.02, 0.02, str(samples[0].measurements[0]._data['data']['D', 'I']))
        #print str( samples[0].measurements[0]._data['data']['D', 'I'].v)


        L, F, T, P, E12, E13, E23, sdper, QF, eval1_err_per, eval2_err_per, eval3_err_per = [], [], [], [], [], [], [], [], [], [], [], []

        #samples[0].measurements[0].calculate_tensor()
        #print samples[0].measurements[0].results
        for s in samples:
            s.measurements[0].calculate_tensor(method='proj')
            T.extend(s.measurements[0].results['T'].v)
            L.extend(s.measurements[0].results['L'].v)
            F.extend(s.measurements[0].results['F'].v)
            P.extend(s.measurements[0].results['P'].v)
            E12.extend(s.measurements[0].results['E12'].v)
            E13.extend(s.measurements[0].results['E13'].v)
            E23.extend(s.measurements[0].results['E23'].v)
            eval1_err_per.extend(s.measurements[0].results['eval1_err'].v/s.measurements[0].results['eval1'].v*100)
            eval2_err_per.extend(s.measurements[0].results['eval2_err'].v/s.measurements[0].results['eval2'].v*100)
            eval3_err_per.extend(s.measurements[0].results['eval3_err'].v/s.measurements[0].results['eval3'].v*100)
            sdper.extend(s.measurements[0].results['stddev'].v / s.measurements[0].results['M'].v * 100)
            QF.extend(s.measurements[0].results['QF'].v)


        fig2, axarr = pyplot.subplots(1, 11)
        do_box_plot(axarr[0], P, 'P', (.99, 1.25))
        do_box_plot(axarr[1], L, 'L', (.99, 1.25))
        do_box_plot(axarr[2], F, 'F', (.99, 1.25))
        do_box_plot(axarr[3], T, 'T', (-1.0, 1.0))
        do_box_plot(axarr[4], eval1_err_per, 'eval1_err_per', (0,8))
        do_box_plot(axarr[5], eval2_err_per, 'eval2_err_per', (0,8))
        do_box_plot(axarr[6], eval3_err_per, 'eval3_err_per', (0,8))
        do_box_plot(axarr[7], E12, 'E12', (0, 90))
        do_box_plot(axarr[8], E13, 'E13', (0, 90))
        do_box_plot(axarr[9], E23, 'E23', (0, 90))
        do_box_plot(axarr[10], sdper, 'stddev %', None)
        #do_box_plot(axarr[8], QF, 'QF', None)



        pyplot.tight_layout()

        fig1.suptitle("meas_err: %.3f, evals: %.2f,%.2f,%.2f, P: %.2f, I offset: %d, method: %s" %
                      (measerr, evals[0], evals[1], evals[2], max( evals[2], evals[0]) / min( evals[2], evals[0]), d, method))

        pdf_pages.savefig(fig1)
        pdf_pages.savefig(fig2)

        Pmedians.append(np.median(P))
        Tmedians.append(np.median(T))
        Lmedians.append(np.median(L))
        Fmedians.append(np.median(F))
        E12medians.append(np.median(E12))
        E13medians.append(np.median(E13))
        E23medians.append(np.median(E23))
        sdpermedians.append(np.median(sdper))
        QFmedians.append(np.median(QF))
        eval1_err_per_medians.append(np.median(eval1_err_per))
        eval2_err_per_medians.append(np.median(eval2_err_per))
        eval3_err_per_medians.append(np.median(eval3_err_per))


        print d
        Ds.append(d)


    fig3, (axu, axd) = pyplot.subplots(2, 1)
    l = []
    l.append(axu.plot(Ds, Pmedians, color='blue', marker='+', label='P'))
    l.append(axu.plot(Ds, Lmedians, color='springgreen', marker='+', label='L'))
    l.append(axu.plot(Ds, Fmedians, color='forestgreen', marker='+', label='F'))
    axu2 = axu.twinx()
    l.append(axu2.plot(Ds, Tmedians, color='peru', marker='+', label='T'))
    axu.set_ylim((0.99, 1.25))
    axu2.set_ylim((-1.05, 1.05))

    l.append(axd.plot(Ds, E12medians, 'g+-', label=r'$\varepsilon_{12}$'))
    l.append(axd.plot(Ds, E13medians, 'gx-', label=r'$\varepsilon_{13}$'))
    l.append(axd.plot(Ds, E23medians, 'g*-', label=r'$\varepsilon_{23}$'))
    axd2 = axd.twinx()
    l.append(axd2.plot(Ds, sdpermedians, 'bx-', label=r'$\sigma (\%)$'))
    l.append(axd2.plot(Ds, eval1_err_per_medians, 'r+-', label=r'$\Delta \lambda_1 (\%)$'))
    l.append(axd2.plot(Ds, eval2_err_per_medians, 'rx-', label=r'$\Delta \lambda_2 (\%)$'))
    l.append(axd2.plot(Ds, eval3_err_per_medians, 'r*-', label=r'$\Delta \lambda_3 (\%)$'))
    axd.set_ylim((0.0, 90.0))
    axd.set_ylabel('degree')
    axd2.set_ylim((0.0, 2.5))
    axd2.set_ylabel('%')


    # make legends
    axd.legend(loc='center left', bbox_to_anchor=(1.1, 0.7), fancybox=True, shadow=True, ncol=1)
    axd2.legend(loc='center left', bbox_to_anchor=(1.1, 0.1), fancybox=True, shadow=True, ncol=1)
    axu.legend(loc='center left', bbox_to_anchor=(1.1, 0.7), fancybox=True, shadow=True, ncol=1)
    axu2.legend(loc='center left', bbox_to_anchor=(1.1, 0.1), fancybox=True, shadow=True)

    # Shrink all x axes by 20%
    for ax in (axu, axu2, axd, axd2):
        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

    pdf_pages.savefig(fig3)
    pdf_pages.close()

if __name__ == '__main__':
    test()