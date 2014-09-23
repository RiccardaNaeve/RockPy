__author__ = 'volk'
import logging
import numpy as np


def vftb(file, *args, **options):
    '''
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
    aux = []
    out_aux = []

    # out = [[np.nan if v is 'n/a' else v for v in i] for i in out]
    out = np.array([map(float, i) for i in out[2:]])
    header = {"field": [0, float], "moment": [1, float], "temp": [2, float], "time": [3, float], "std_dev": [4, float],
              "suscep / emu / g / Oe": [5, float],
    }

    out_aux = {}
    for column in header:
        aux = {column.lower(): np.array([header[column][1](i[header[column][0]]) for i in out])}
        out_aux.update(aux)

    # out = {column.lower(): np.array([header[column][1](i[header[column][0]]) for i in out]) for column in
    # header}

    out = out_aux
    out['moment'] *= mass / 1E3
    out['field'] *= 0.0001
    return out

