__author__ = 'Mike'
import logging
import numpy as np
import matplotlib.pyplot as plt
from math import degrees, radians
from math import sin, cos, tan, asin, atan2


def create_logger(name):
    log = logging.getLogger(name=name)
    log.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s: %(levelname)-10s %(name)-20s %(message)s')
    # fh = logging.FileHandler('RPV3.log')
    # fh.setFormatter(formatter)
    # ch = logging.FileHandler('RPV3.log')
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    ch.setFormatter(formatter)
    # log.addHandler(fh)
    log.addHandler(ch)

    return ch#, fh


def differentiate(data_list, diff=1, smoothing=1, norm=False, check=False):
    """
    caclulates a smoothed (if smoothing > 1) derivative of the data

    :param data_list: ndarray - 2D array with xy[:,0] = x_data, xy[:,1] = y_data
    :param diff: int - the derivative to be calculated f' -> diff=1; f'' -> diff=2
          default = 1
    :param smoothing: int - smoothing factor
    :param norm:
    :param check:
    :return:
    """
    log = logging.getLogger('RockPy.FUNCTIONS.general.diff')
    log.info('DIFFERENTIATING\t data << %i derivative - smoothing: %i >>' % (diff, smoothing))
    data_list = np.array(data_list)
    # getting X, Y data
    X = data_list[:, 0]
    Y = data_list[:, 1]

    # ''' test with X^3'''
    # X = np.linspace(-10,10,1000)
    # Y = X**3
    # Y2 = 3*X**2
    # Y3 = 6*X

    # # derivative
    for i in range(diff):
        deri = [[X[i], (Y[i + smoothing] - Y[i - smoothing]) / (X[i + smoothing] - X[i - smoothing])] for i in
                range(smoothing, len(Y) - smoothing)]
        deri = np.array(deri)
        X = deri[:, 0]
        Y = deri[:, 1]
    MAX = max(abs(deri[:, 1]))

    if norm:
        deri[:, 1] /= MAX
    if check:
        if norm:
            plt.plot(data_list[:, 0], data_list[:, 1] / max(data_list[:, 1]))
        if not norm:
            plt.plot(data_list[:, 0], data_list[:, 1])
        plt.plot(deri[:, 0], deri[:, 1])
        plt.show()

    return deri


def rotate(xyz, axis='x', degree=0, *args):
    """


    :rtype : object
    :param x:
    :param y:
    :param z:
    :param axis:
    :param degree:
    :return:
    """
    a = radians(degree)

    RX = [[1, 0, 0],
          [0, cos(a), -sin(a)],
          [0, sin(a), cos(a)]]

    RY = [[cos(a), 0, sin(a)],
          [0, 1, 0],
          [-sin(a), 0, cos(a)]]

    RZ = [[cos(a), -sin(a), 0],
          [sin(a), cos(a), 0],
          [0, 0, 1]]

    if axis.lower() == 'x':
        out = np.dot(xyz, RX)
    if axis.lower() == 'y':
        out = np.dot(xyz, RY)
    if axis.lower() == 'z':
        out = np.dot(xyz, RZ)

    return out

def abs_min_max(list):
    list = [i for i in list if not i == np.nan or not i == inf]
    min_idx = np.argmin(np.fabs(list))
    print min_idx
    max_idx = np.argmax(np.fabs(list))
    return list[min_idx], list[max_idx]

def _to_list(oneormoreitems):
    """
    convert argument to tuple of elements
    :param oneormoreitems: single number or string or list of numbers or strings
    :return: tuple of elements
    """
    return oneormoreitems if hasattr(oneormoreitems, '__iter__') else [oneormoreitems]

def XYZ2DIL( XYZ):
    """
    convert XYZ to dec, inc, length
    :param XYZ:
    :return:
    """
    DIL = []
    L = np.linalg.norm( XYZ)
    #L=sqrt(XYZ[0]**2+XYZ[1]**2+XYZ[2]**2) # calculate resultant vector length
    D = degrees(atan2(XYZ[1],XYZ[0]))  # calculate declination taking care of correct quadrants (atan2)
    if D < 0: D = D+360. # put declination between 0 and 360.
    if D > 360.: D = D-360.
    DIL.append(D)  # append declination to Dir list
    I = degrees(asin(XYZ[2]/L))  # calculate inclination (converting to degrees)
    DIL.append(I)  # append inclination to Dir list
    DIL.append(L)  # append vector length to Dir list
    return DIL

def DIL2XYZ( DIL):
    """
    Convert a tuple of D,I,L components to a tuple of x,y,z.
    :param DIL:
    :return:
    """
    (D, I, L) = DIL
    H = L*cos(radians(I))
    X = H*cos(radians(D))
    Y = H*sin(radians(D))
    Z = H*tan(radians(I))
    return (X, Y, Z)

def MirrorDirectionToNegativeInclination( dec, inc):
    if inc > 0:
        return (dec + 180) % 360, -inc
    else:
        return dec, inc

def MirrorDirectionToPositiveInclination( dec, inc):
    if inc < 0:
        return (dec + 180) % 360, -inc
    else:
        return dec, inc

def MirrorVectorToNegativeInclination( x,y,z):
    if z > 0: return -x,-y,-z
    else: return x,y,z

def MirrorVectorToPositiveInclination( x,y,z):
    if z < 0: return -x, -y, -z
    else: return x,y,z


def Proj_A_on_B_scalar( A, B):
    """

    :param A: vector which will be projected on vector B
    :param B: vector defining the direction
    :return: scalar value of the projection A on B
    """
    return np.dot(A, B) / np.linalg.norm(B)