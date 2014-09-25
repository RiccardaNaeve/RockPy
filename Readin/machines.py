__author__ = 'volk'
import logging
import numpy as np


class Vsm(object):
    def __init__(self, file, sample=None):
        self.log = logging.getLogger('RockPy.READIN.vsm')
        self.log.info('IMPORTING\t VSM file: << %s >>' % file)

        file = open(file, 'rU')
        reader_object = file.readlines()
        self.header = self.readMicroMagHeader(reader_object)  # get header
        self.raw_out = [i for i in reader_object][self.header['meta']['numberoflines']:]  # without header

    @property
    def out(self):
        # ### header part
        data_header = [i.split('\n')[0] for i in self.raw_out if
                       not i.startswith('+') and not i.startswith('-') and not i.split() == []][:-1]
        aux = [i for i in data_header[-3:]]
        h_len = len(aux[0]) / len(aux[-1].split()) + 1
        splits = np.array([[i[x:x + h_len] for x in range(0, len(i), h_len)] for i in aux]).T
        splits = ["".join(i) for i in splits]
        splits = [' '.join(j.split()) for j in splits]

        out = [i for i in self.raw_out if i.startswith('+') or i.startswith('-') or i.split() == []]
        out_data = []
        aux = []
        for i in out:
            if len(i) != 1:
                if i.strip() != '':
                    d = i.strip('\n').split(',')
                    try:
                        d = [float(i) for i in d]
                        aux.append(d)
                    except:
                        self.log.debug('%s' % d)
                        if 'Adjusted' in d[0].split():
                            adj = True
                        pass
            else:
                out_data.append(np.array(aux))
                aux = []
        # out_data = np.array(out_data)
        # out = {splits[i]: np.array([j[:, i] for j in out_data]) for i in range(len(splits))}
        # log.info('RETURNING data << %s >> ' %(' - '.join(out.keys())))
        # out.update(header)
        return out_data[1:]

    def readMicroMagHeader(self, lines):
        sectionstart = False
        sectiontitle = None
        sectioncount = 0
        header = {}
        # section header: CAPITALS, no spaces
        lc = 0
        for l in lines:
            lc += 1
            sl = l.strip()  # take away any leading and trailing whitespaces
            if lc == 1 and not sl.startswith("MicroMag 2900/3900 Data File"):  # check first line
                self.log.error("No valid MicroMag file. Header not found in first line.")
                return None

            if len(sl) == 0:  # empty line
                sectionstart = True
                continue  # go to next line
            if sectionstart:  # previous line was empty
                sectionstart = False
                if sl.isupper():  # we have a capitalized section header
                    # log.INFO('reading header section %s' % sl)
                    sectiontitle = sl
                    header[sectiontitle] = {}  # make new dictionary to gather data fields
                    sectioncount += 1
                    continue  # go to next line
                else:  # no captitalized section header after empty line -> we are probably at the end of the header
                    # verbous.INFO('reading header finished at line %d' % lc)
                    break  # end of header
            if sectiontitle != None:  # we are within a section
                # split key value at fixed character position
                key = sl[:31].strip()
                value = sl[31:].strip(' "')
                if len(key) != 0:
                    header[sectiontitle][key] = value
        header['meta'] = {}
        header['meta']['numberoflines'] = lc - 1  # store header length
        header['meta']['numberofsections'] = sectioncount
        return header


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


# def vsm_forc(file, sample=None):
# log = logging.getLogger('RockPy.READIN.vsm_forc')
#     log.info('IMPORTING\t VSM file: << %s >>' % file)
#
#     file = open(file, 'rU')
#     reader_object = file.readlines()
#     header = readMicroMagHeader(reader_object)  # get header
#     raw_out = [i for i in reader_object][header['meta']['numberoflines']:]  # without header
#
#     #### header part
#     data_header = [i.split('\n')[0] for i in raw_out if not i.startswith('+') and not i.startswith('-') and not i.split() == []][:-1]
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
