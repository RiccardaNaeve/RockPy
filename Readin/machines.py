__author__ = 'volk'
import logging
import time

import numpy as np


def cryo_nl(file, sample, *args, **options):
    log = logging.getLogger('RockPy.READIN.CRYO_NL')
    log.info('IMPORTING\t cryomag file: << %s >>' % file)

    floats = ['x', 'y', 'z', 'm', 'sm', 'a95', 'dc', 'ic', 'dg', 'ig', 'ds', 'is']
    data_f = open(file)
    data = [i.strip('\n\r').split('\t') for i in data_f.readlines()]

    header = ['name', 'coreaz', 'coredip', 'bedaz', 'beddip',
              'vol', 'weight', 'step', 'type', 'comment',
              'time', 'mode', 'x', 'y', 'z',
              'M', 'sM', 'a95', 'Dc', 'Ic', 'Dg', 'Ig', 'Ds', 'Is']

    sample_data = np.array([i for i in data[2:-1] if i[0] == sample or sample in i[9] if i[11] == 'results'])
    out = {header[i].lower(): sample_data[:, i] for i in range(len(header))}

    for i in floats:
        out[i] = map(float, out[i])

    out['step'] = map(int, out['step'])

    def time_conv(t):
        return time.strptime(t, "%y-%m-%d %H:%M:%S")

    out['time'] = map(time_conv, out['time'])
    return out




def Vftb(file, *args, **options):
    '''
    read in routine for vftb files

    header: 1:field [T]	    2:mag  [Am^2]	    3:temp [C]
            4:time [s]  	5:std dev [%]   	6:suscep [emu / g / Oe]

    '''
    log = logging.getLogger('RockPy.READIN.vftb')
    log.info('IMPORTING\t VFTB file: << %s >>' % file)
    reader_object = open(file)
    out = [i.strip('\r\n').split('\t') for i in reader_object.readlines()]

    mass = float(out[0][1].split()[1])
    # out = np.array(out[4:])
    idx1 = [i for i in range(len(out)) if '' in out[i]]
    idx2 = [i for i in range(len(out)) if 'Set 2:' in out[i]]
    idx3 = [i for i in range(len(out)) if ' field / Oe' in out[i]]
    idx = idx1 + idx2 + idx3
    out = [['0.' if j == 'n/a' else j for j in i] for i in out]
    out = [out[i] for i in range(len(out)) if i not in idx]

    # out = [[np.nan if v is 'n/a' else v for v in i] for i in out]
    out = np.array([map(float, i) for i in out[2:]])
    header = {"field": [0, float], "moment": [1, float], "temp": [2, float], "time": [3, float], "std_dev": [4, float],
              "suscep / emu / g / Oe": [5, float],
    }

    out = np.array(out)

    out[:, 0] *= 0.0001  # recalculate to T
    out[:, 1] *= mass / 1E3  # de-normalize of mass

    units = ['T', 'Am^2', 'C', 's', '%', 'emu/g/Oe']

    return out


# def vsm_forc(file, sample=None):
# log = logging.getLogger('RockPy.READIN.vsm_forc')
# log.info('IMPORTING\t VSM file: << %s >>' % file)
#
#     file = open(file, 'rU')
#     reader_object = file.readlines()
#     header = readMicroMagHeader(reader_object)  # get header
#     raw_out = [i for i in reader_object][header['meta']['numberoflines']:]  # without header
#
#     #### header part
#     data_header = [i.split('\n')[0] for i in raw_out if not i.startswith('+') and not i.startswith('-') and not
# i.split() == []][:-1]
#     aux = [i for i in data_header[-3:]]
#     h_len = len(aux[0]) / len(aux[-1].split())+1
#     splits = np.array([[i[x:x + h_len] for x in range(0, len(i), h_len)] for i in aux ]).T
#     splits = ["".join(i) for i in splits]
#     splits = [' '.join(j.split()) for j in splits]
#
#     out = [i for i in raw_out if i.startswith('+') or i.startswith('-') or i.split() == []]
#     out_data = []
#     aux = []
#     for i in out:
#         if len(i) != 1:
#             if i.strip() != '':
#                 d = i.strip('\n').split(',')
#                 try:
#                     d = [float(i) for i in d]
#                     aux.append(d)
#                 except:
#                     log.debug('%s' % d)
#                     if 'Adjusted' in d[0].split():
#                         adj = True
#                     pass
#         else:
#             out_data.append(np.array(aux))
#             aux = []
#     out_data = np.array(out_data)
#     out = {splits[i]: np.array([j[:, i] for j in out_data]) for i in range(len(splits))}
#     log.info('RETURNING data << %s >> ' %(' - '.join(out.keys())))
#     out.update(header)
#     return out

# def vsm(file, sample=None):
#     log = logging.getLogger('RockPy.READIN.vsm')
#     log.info('IMPORTING\t VSM file: << %s >>' % file)
#     file = open(file, 'rU')
#     reader_object = file.readlines()
#     header = readMicroMagHeader(reader_object)  # get header
#     out = [i for i in reader_object][header['meta']['numberoflines']:]  # without header
#     aux = []
#     out_data = []
#     linecount = 0
#     adj = False
#
#     for i in out:
#         if len(i) != 1:
#             if i.strip() != '':
#                 d = i.strip('\n').split(',')
#                 try:
#                     d = [float(i) for i in d]
#                     aux.append(d)
#                 except:
#                     log.debug('%s' % d)
#                     if 'Adjusted' in d[0].split():
#                         adj = True
#                     pass
#         else:
#             out_data.append(aux)
#             aux = []
#     segments = np.array(out_data[0])
#
#     if adj:
#         header['adjusted'] = True
#     out_data = np.array(out_data[1:])
#     return segments, out_data, header
