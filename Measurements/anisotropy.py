__author__ = 'wack'

import base
import logging
from math import cos, sin, atan, radians, log, exp, sqrt, degrees
import numpy as np
from RockPy.Functions.general import XYZ2DIL, DIL2XYZ, MirrorDirectionToPositiveInclination
from RockPy.Structure.data import RockPyData
from random import random

class Anisotropy(base.Measurement):
    """
    calculation of anisotropy tensors based on pseudo inverse (least squares fitting) of given data
    """

    logger = logging.getLogger('RockPy.MEASUREMENT.Anisotropy')


    @classmethod
    def simulate(cls, sample_obj, color=None, **parameter):
        """
        return simulated instance of measurement depending on parameters
        """
        # get measurement directions in array of D,I pairs
        mdirs = parameter.get('mdirs', [[0.0, 0.0], [90.0, 0.0], [0.0, 90.0]])
        # get eigenvalues
        evals = list(parameter.get('evals', [1.0, 1.0, 1.0]))
        if len(evals) != 3:
            raise RuntimeError('got %d eigenvalues instead of 3' % len(evals))

        # get random measurement errors
        measerr = parameter.get('measerr', 0)


        # todo: normalize evals to 1?

        R = Anisotropy.createDiagonalTensor(*evals)

        #todo: also implement 1D measurement

        data = RockPyData(column_names=['D', 'I', 'X', 'Y', 'Z'])

        for mdir in mdirs:
            # M = R * H
            errs = [measerr * random() * 2 - measerr for i in (1,2,3)]
            measurement = np.dot(R, DIL2XYZ((mdir[0], mdir[1], 1))) + errs
            data = data.append_rows(np.hstack([np.array(mdir), measurement]))


        data.define_alias('variable', ('D', 'I'))

        mdata = {'data': data}

        return cls(sample_obj, 'anisotropy', mfile=None, mdata=mdata, machine='simulation', color=color, **parameter)



    @staticmethod
    def createDiagonalTensor( ev1, ev2, ev3):
        """
        create a tensor (3x3 matrix) with the 3 given eigenvalues on its diagonal
        :param eigenvalues:
        :return: numpy array as tensor
        """
        return np.array([[ev1, 0, 0], [0, ev2, 0], [0, 0, ev3]])

    @staticmethod
    def makeDesignMatrix(mdirs, xyz):
        """
        create design matrix for anisotropy measurements
        :param mdirs: measurement directions e.g. [[D1,I1],[D2,I2],[D3,I3],[D4,I4]]
        :param xyz: True --> individual components measured (AARM); False: one component measured (AMS) or ARM without GRM
        :return:
        """
        #directions in cartesian coordinates
        XYZ = []
        for i in range(len(mdirs)):
            XYZ.append([cos(radians(mdirs[i][0]))*cos(radians(mdirs[i][1])), sin(radians(mdirs[i][0]))*cos(radians(mdirs[i][1])), sin(radians(mdirs[i][1]))])

        # make design matrix for single components (x,y,z)
        B = np.zeros((len(XYZ) * 3, 6), 'f')

        for i in range(len(XYZ)):
            B[i*3+0][0] = XYZ[i][0]
            B[i*3+0][3] = XYZ[i][1]
            B[i*3+0][5] = XYZ[i][2]

            B[i*3+1][3] = XYZ[i][0]
            B[i*3+1][1] = XYZ[i][1]
            B[i*3+1][4] = XYZ[i][2]

            B[i*3+2][5] = XYZ[i][0]
            B[i*3+2][4] = XYZ[i][1]
            B[i*3+2][2] = XYZ[i][2]

        if xyz == True:
            A = B

        else:
            # make design matrix for directional measurement (same direction as applied field)
            A = np.zeros((len(mdirs), 6), 'f')


            for i in range(len(XYZ)):
                A[i] = XYZ[i][0]*B[i*3+0] + XYZ[i][1]*B[i*3+1] + XYZ[i][2]*B[i*3+2]

        return A

    @staticmethod
    def CalcPseudoInverse(A):
        """
        calculate pseude inverse of matrix A
        :param A: matrix
        :return:
        """

        AT = np.transpose(A)
        ATA = np.dot(AT, A)
        ATAI = np.linalg.inv(ATA)
        B = np.dot(ATAI, AT)

        return B


    @staticmethod
    def CalcEigenValVec(T):
        """
        calculate eigenvalues and eigenvectors from tensor T, sorted by eigenvalues
        :param T: tensor
        :return:
        """
        #get eigenvalues and eigenvectors
        eigvals, eigvec = np.linalg.eig(T)

        #sort by eigenvalues
        #put eigenvalues and and eigenvectors together in one list and sort this one
        valvec = []
        for i in range(len(eigvals)):
            valvec.append([eigvals[i], np.transpose(eigvec)[i].tolist()])

        #sort eigenvalues and eigenvectors by eigenvalues
        valvec.sort(lambda x, y: -cmp(x[0], y[0]))  # sort from large to small

        for i in range(len(valvec)):
            eigvals[i] = valvec[i][0]
            eigvec[i] = valvec[i][1]

        return eigvals, eigvec

    @staticmethod
    def CalcAnisoTensor(A, K):
        """ calculate anisotropy tensor
            input: A: design matrix
                   K: measured values
            return: dictionary
                   R: anisotropy tensor
                   eigvals: eigenvalues as array
                   n_eigvals: normalized eigenvalues as array
                   n_eval1, n_eval2, n_eval3: normalized eigenvalues
                   eigvecs: eigenvectors (sorted by eigenvalues)
                   I1, I2, I3, D1, D2, D3: inclinations and declinations of eigenvectors
                   M: mean magnetization
                   Kf: best fit values for K
                   L: lineation
                   F: foliation
                   P: degree of anisotropy?
                   P1: corrected degree of anisotropy?
                   T: shape parameter
                   U:
                   Q:
                   E:
                   S0: sum of error^2
                   stddev: standard deviation
                   E12: 12 axis of confidence ellipse
                   E23: 23 axis of confidence ellipse
                   E13: 13 axis of confidence ellipes
                   F0: test for anisotropy (Hext 63)
                   F12: test for anisotropy
                   F23: test for anisotropy
                   QF: quality factor
                   """

        aniso_dict = {}
        aniso_dict['msg'] = ''  # put in here any message you want to pass out of this routine

        # calculate pseudo inverse of A
        B = Anisotropy.CalcPseudoInverse(A)

        # calculate elements of anisotropy tensor
        s = np.dot(B, K)

        # construct symmetric anisotropy tensor R (3x3)
        R = np.array([[s[0], s[3], s[5]], [s[3], s[1], s[4]], [s[5], s[4], s[2]]])
        #R = R.reshape(3, 3)
        aniso_dict['R'] = R

        # calculate eigenvalues and eigenvectors = principal axes
        eigvals, eigvecs = Anisotropy.CalcEigenValVec(R)
        aniso_dict['eigvals'] = eigvals
        aniso_dict['eigvecs'] = eigvecs

        # calc inclination and declination of eigenvectors
        (D1, I1, L) = XYZ2DIL(eigvecs[0])
        (D2, I2, L) = XYZ2DIL(eigvecs[1])
        (D3, I3, L) = XYZ2DIL(eigvecs[2])

        # to get consistent plotting, make all inclinations positive
        aniso_dict['D1'], aniso_dict['I1'] = MirrorDirectionToPositiveInclination( D1, I1)
        aniso_dict['D2'], aniso_dict['I2'] = MirrorDirectionToPositiveInclination( D2, I2)
        aniso_dict['D3'], aniso_dict['I3'] = MirrorDirectionToPositiveInclination( D3, I3)


        #calc mean magnetization
        M = (eigvals[0]+eigvals[1]+eigvals[2])/3
        aniso_dict['M'] = M


        #calc normalized eigenvalues k
        k = eigvals / (eigvals[0]+eigvals[1]+eigvals[2])*3
        aniso_dict['n_eigvals'] = k
        aniso_dict['n_eval1'] = k[0]
        aniso_dict['n_eval2'] = k[1]
        aniso_dict['n_eval3'] = k[2]

        #calc some parameters
        L = k[0] / k[1]
        F = k[1] / k[2]
        P = k[0] / k[2]

        aniso_dict['L'] = L
        aniso_dict['F'] = F
        aniso_dict['P'] = P

        n = []
        neg_eigenvalue = False  # check for negative eigenvalues, log will fail
        for kn in k:
            if kn <=0:
                neg_eigenvalue = True
                aniso_dict['msg'] = 'Warning: negative eigenvalue!'
                n.append(None)
            else:
                n.append(log(kn))

        if not neg_eigenvalue:
            navg = (n[0]+n[1]+n[2]) / 3

            P1 = exp(sqrt(2 * ((n[0]-navg)**2+(n[1]-navg)**2+(n[2]-navg)**2)))
            aniso_dict['P1'] = P1

            # calculation of T fails when measurements are isotropic
            c = 2 * n[1] - n[0] - n[2]

            if c == 0.0:
                T = 0  # TODO: check if this makes sense : T = 0, when isotropic
            else:
                T = c / (n[0] - n[2])

            aniso_dict['T'] = T

        else:
            aniso_dict['P1'] = 0  # not possible to calc -> set to 0
            aniso_dict['T'] = 0

        U = (2 * k[1] - k[0] - k[2]) / (k[0] - k[2])
        aniso_dict['U'] = U

        Q = (k[0]-k[1]) / ((k[0]+k[1])/2-k[2])
        aniso_dict['Q'] = Q

        E = k[1]**2 / (k[0] * k[2])
        aniso_dict['E'] = E


        #calculate best fit values of K
        Kf = np.dot(A, s)
        aniso_dict['Kf'] = Kf

        #calculate K - Kf --> errors
        d = K - Kf

        #print "measured   \tfit       \ttensor\n"
        #for c in range( len( K)):
        #    print "%.4f   \t %.4f \t %.4f" % (K[c], Kf[c], d[c])

        #calculate sum of errors^2
        S0 = np.dot(d[0], d[0])
        aniso_dict['S0'] = S0

        #calculate variance
        var = S0 / (len(d)/3)
        # len(d) == 18 for 6 directions (12 measured)
        #calc standard deviation
        stddev = sqrt( var)
        aniso_dict['stddev'] = stddev

        # calculate quality factor
        QF = (P-1) / (stddev / M)
        aniso_dict['QF'] = QF

        # calculate confidence ellipses
        #F = 3.89 --> looked up from tauxe lecture 2005; F-table
        f = sqrt(2 * 3.89)
        E12 = abs(degrees(atan(f * stddev / (2 * (eigvals[1]-eigvals[0])))))
        E23 = abs(degrees(atan(f * stddev / (2 * (eigvals[1]-eigvals[2])))))
        E13 = abs(degrees(atan(f * stddev / (2 * (eigvals[2]-eigvals[0])))))

        aniso_dict['E12'] = E12
        aniso_dict['E23'] = E23
        aniso_dict['E13'] = E13

        #Tests for anisotropy (Hext 63)
        F0  = 0.4 * (eigvals[0]**2+eigvals[1]**2+eigvals[2]**2 - 3 * ((s[0]+s[1]+s[2])/3)**2) / var
        F12 = 0.5 * ((eigvals[0] - eigvals[1]) / stddev)**2
        F23 = 0.5 * ((eigvals[1] - eigvals[2]) / stddev)**2

        aniso_dict['F0'] = F0
        aniso_dict['F12'] = F12
        aniso_dict['F23'] = F23


        return aniso_dict  # return the whole bunch of values


    #def __init__(self, sample_obj, mtype, mfile, machine, **options):
    #    super(Anisotropy, self).__init__(sample_obj, mtype, mfile, machine, **options)


    ''' FORMAT SECTION '''


    def format_ani(self):
        self.header = self.machine_data.header

        mdirs = self.machine_data.mdirs
        measurements = self.machine_data.data

        #do we have scalar or vectorial measurements?
        if len(measurements.flatten()) == len(mdirs):  #scalar
            data = RockPyData(column_names=['D', 'I', 'M'])
        elif len(measurements.flatten()) / len(mdirs) == 3:  #vectorial
            data = RockPyData(column_names=['D', 'I', 'X', 'Y', 'Z'])
        else:
            Anisotropy.logger.error("anisotropy measurements have %d components")
            return

        for idx in range(len(mdirs)):
            data = data.append_rows(np.hstack([np.array(mdirs[idx]), measurements[idx]]))

        data.define_alias('variable', ('D', 'I'))
        self._data['data'] = data


    ''' RESULT SECTION '''

    def result_t11(self, recalc=False):
        self.calc_result(parameter={}, recalc=recalc, force_method='tensor')
    def result_t12_21(self, recalc=False):
        self.calc_result(parameter={}, recalc=recalc, force_method='tensor')
    def result_t13_31(self, recalc=False):
        self.calc_result(parameter={}, recalc=recalc, force_method='tensor')
    def result_t22(self, recalc=False):
        self.calc_result(parameter={}, recalc=recalc, force_method='tensor')
    def result_t23_32(self, recalc=False):
        self.calc_result(parameter={}, recalc=recalc, force_method='tensor')
    def result_t33(self, recalc=False):
        self.calc_result(parameter={}, recalc=recalc, force_method='tensor')
    def result_eval1(self, recalc=False):
        self.calc_result(parameter={}, recalc=recalc, force_method='tensor')
    def result_eval2(self, recalc=False):
        self.calc_result(parameter={}, recalc=recalc, force_method='tensor')
    def result_eval3(self, recalc=False):
        self.calc_result(parameter={}, recalc=recalc, force_method='tensor')
    def result_I1(self, recalc=False):
        self.calc_result(parameter={}, recalc=recalc, force_method='tensor')
    def result_D1(self, recalc=False):
        self.calc_result(parameter={}, recalc=recalc, force_method='tensor')
    def result_I2(self, recalc=False):
        self.calc_result(parameter={}, recalc=recalc, force_method='tensor')
    def result_D2(self, recalc=False):
        self.calc_result(parameter={}, recalc=recalc, force_method='tensor')
    def result_I3(self, recalc=False):
        self.calc_result(parameter={}, recalc=recalc, force_method='tensor')
    def result_D3(self, recalc=False):
        self.calc_result(parameter={}, recalc=recalc, force_method='tensor')
    def result_P(self, recalc=False):
        self.calc_result(parameter={}, recalc=recalc, force_method='tensor')
    def result_P1(self, recalc=False):
        self.calc_result(parameter={}, recalc=recalc, force_method='tensor')
    def result_F(self, recalc=False):
        self.calc_result(parameter={}, recalc=recalc, force_method='tensor')
    def result_L(self, recalc=False):
        self.calc_result(parameter={}, recalc=recalc, force_method='tensor')
    def result_T(self, recalc=False):
        self.calc_result(parameter={}, recalc=recalc, force_method='tensor')
    def result_E12(self, recalc=False):
        self.calc_result(parameter={}, recalc=recalc, force_method='tensor')
    def result_E13(self, recalc=False):
        self.calc_result(parameter={}, recalc=recalc, force_method='tensor')
    def result_E23(self, recalc=False):
        self.calc_result(parameter={}, recalc=recalc, force_method='tensor')
    def result_E(self, recalc=False):
        self.calc_result(parameter={}, recalc=recalc, force_method='tensor')
    def result_Q(self, recalc=False):
        self.calc_result(parameter={}, recalc=recalc, force_method='tensor')
    def result_U(self, recalc=False):
        self.calc_result(parameter={}, recalc=recalc, force_method='tensor')
    def result_F0(self, recalc=False):
        self.calc_result(parameter={}, recalc=recalc, force_method='tensor')
    def result_F12(self, recalc=False):
        self.calc_result(parameter={}, recalc=recalc, force_method='tensor')
    def result_F23(self, recalc=False):
        self.calc_result(parameter={}, recalc=recalc, force_method='tensor')
    def result_stddev(self, recalc=False):
        self.calc_result(parameter={}, recalc=recalc, force_method='tensor')
    def result_QF(self, recalc=False):
        self.calc_result(parameter={}, recalc=recalc, force_method='tensor')


    ''' CALCULATION SECTION '''

    def calculate_tensor(self):
        # calculate design matrix
        mdirs = self._data['data']['D', 'I'].v.tolist()
        dm = Anisotropy.makeDesignMatrix(mdirs, self._data['data'].column_exists('Z'))
        # calculate tensor and all other results
        measurements = self._data['data']['dep_var'].v.flatten().tolist()
        self.aniso_dict = Anisotropy.CalcAnisoTensor(dm, measurements)
        self.results['t11'] = self.aniso_dict['R'][0][0]
        self.results['t12_21'] = self.aniso_dict['R'][0][1]
        self.results['t13_31'] = self.aniso_dict['R'][0][2]
        self.results['t22'] = self.aniso_dict['R'][1][1]
        self.results['t23_32'] = self.aniso_dict['R'][1][2]
        self.results['t33'] = self.aniso_dict['R'][2][2]

        self.results['eval1'] = self.aniso_dict['eigvals'][0]
        self.results['eval2'] = self.aniso_dict['eigvals'][1]
        self.results['eval3'] = self.aniso_dict['eigvals'][2]


        for k in ('I1', 'D1', 'I2', 'D2', 'I3', 'D3', 'P', 'P1', 'F', 'L', 'T', 'E12', 'E13', 'E23', 'E', 'Q', 'U', 'F0', 'F12', 'F23', 'stddev', 'QF'):
            self.results[k] = self.aniso_dict[k]
