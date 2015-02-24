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
        axes.set_ylim(ylim)
        pyplot.setp(axes.get_xticklabels(), visible=False)
        axes.set_xlabel(label)
        axes.set_xlim((0.9, 1.1))


    # create samples

    samples = []
    for i in range(100):
        s = Sample(name=str(i))
        m = s.add_simulation(mtype='anisotropy', evals=(1.01, 1.01, 0.99),
                                mdirs=[[225.0, 0.0], [135.0, 0.0], [90.0, 45.0],
                                       [90.0, -45.0], [0.0, -45.0], [0.0, 45.0]],
                                measerr=0.001)

        samples.append(s)


    """
    # add measurement, read from file
    #M1 = sample1.add_measurement(mtype='anisotropy', mfile=ani_file2, machine='ani')
    M3 = sample2.add_simulation(mtype='anisotropy', evals=(1.5, 1.5, 0.3),
                                mdirs=[[225.0, 0.0], [135.0, 0.0], [90.0, 45.0],
                                       [90.0, -45.0], [0.0, -45.0], [0.0, 45.0]])
    M4 = sample3.add_simulation(mtype='anisotropy', evals=(1.5, 1.3, 0.3),
                                mdirs=[[225.0, 0.0], [135.0, 0.0], [90.0, 45.0],
                                       [90.0, -45.0], [0.0, -45.0], [0.0, 45.0]])
    #M4 = sample2.add_simulation(mtype='anisotropy', evals=(1.1, 1.5, 1.3),
    #                            mdirs=[[225.0, 0.0], [135.0, 0.0], [90.0, 45.0],
    #                                   [90.0, -45.0], [0.0, -45.0], [0.0, 45.0]])

    # print "M._data", M._data



    #M1.calculate_tensor()
    #M3.calculate_tensor()
    #M4.calculate_tensor()

    #M1.calc_all()  # broken

    #print M1.results
    #print M3.results
    #print M4.results
    """
    sg = RockPy.SampleGroup(sample_list=samples)
    study = RockPy.Study(samplegroups=sg)

    pdf_pages = PdfPages('out_oblate_sushi__101_099_099_0_001err.pdf')


    startoffset = 7

    for s in samples:
        s.measurements[0]._data['data']['D'] = s.measurements[0]._data['data']['D'].v + startoffset-1

    for d in range(10):
        for s in samples:
            #modify reference directions
            #add to inclination
            #m._data['data']['I'] = m._data['data']['I'].v + 2
            #add to declination
            s.measurements[0]._data['data']['D'] = s.measurements[0]._data['data']['D'].v + 1

        aniplt = RockPy.Visualize.anisotropy.Anisotropy(study, plt_primary="samples", plt_secondary=None)

        # get figure
        fig1 = aniplt.figs[aniplt.name][0]

        L, F, T, P, E12, E13, E23 = [], [], [], [], [], [], []

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

        #print T
        #box_ax = fig.add_axes([0.9,0.6,0.08,0.3])
        #box_ax.boxplot([T, P])

        fig2, axarr = pyplot.subplots(1, 7)
        do_box_plot(axarr[0], T, 'T', (-1, 1))
        do_box_plot(axarr[1], L, 'L', (.9, 2))
        do_box_plot(axarr[2], F, 'F', (.9, 2))
        do_box_plot(axarr[3], P, 'P', (.9, 2))
        do_box_plot(axarr[4], E12, 'E12', (0, 90))
        do_box_plot(axarr[5], E13, 'E13', (0, 90))
        do_box_plot(axarr[6], E23, 'E23', (0, 90))


        pyplot.tight_layout()

        #pyplot.show()

        #fig1.savefig('stereo.pdf')
        #fig2.savefig('stats.pdf')
        fig1.suptitle("sushi geomatery, meas_err: 0.001, evals: 1.01,1.01,0.99, D offset: %d" % (d+startoffset))

        pdf_pages.savefig(fig1)
        pdf_pages.savefig(fig2)

        print d+startoffset

    pdf_pages.close()


if __name__ == '__main__':
    test()