__author__ = 'mike'
import os
from os.path import expanduser, join
import numpyson
import numpy as np
from pint import UnitRegistry
import RockPy

ureg = UnitRegistry()

default_folder = join(expanduser("~"), 'Desktop', 'RockPy')


def save(smthg, file_name, folder=None):
    if not folder:
        folder = default_folder
    with open(join(folder, file_name), 'wb') as f:
        dump = numpyson.dumps(smthg)
        f.write(dump)
        f.close()


def load(file_name, folder=None):
    # print 'loading: %s' %join(folder, file_name)
    if not folder:
        folder = default_folder
    with open(join(folder, file_name), 'rb') as f:
        out = numpyson.loads(f.read())
    return out


def add_unit(value, unit):
    out = str(value) + '[' + unit + ']'
    return out


def generate_file_name(sample_group='', sample_name='',
                       mtype='', machine='',
                       mass='', mass_unit='',
                       height='', height_unit='',
                       diameter='', diameter_unit='',
                       parameter=list(), parameter_values=[], parameter_units=[],
                       standard_measurement='',
                       index='',
):
    """
    generates a name according to the RockPy specific naming scheme.
    :param sample_group:
    :param sample_name:
    :param mtype:
    :param machine:
    :param mass:
    :param mass_unit:
    :param height:
    :param height_unit:
    :param diameter:
    :param diameter_unit:
    :param parameter:
    :param parameter_values:
    :param parameter_units:
    :param standard_measurement:
    :param index:
    :return:
    """
    if not index:
        index = '%03i' % (np.random.randint(999, size=1)[0])

    sample = '_'.join([sample_group, sample_name, mtype.upper(), machine.upper()])
    sample_info = '_'.join(
        [add_unit(mass, mass_unit), add_unit(height, height_unit), add_unit(diameter, diameter_unit)])
    # print ['_'.join(map(str, [parameter[i],parameter_values[i], parameter_units[i]])) for i in range(len(parameter))]
    params = ';'.join(
        ['_'.join(map(str, [parameter[i], parameter_values[i], parameter_units[i]])) for i in range(len(parameter))])

    out = '#'.join([sample, sample_info, params, standard_measurement])
    out += '.%03i' %int(index)
    return out


def extract_info_from_filename(fname, data_dir):
    # print fname
    index = int(fname[-3:])

    rest = fname[:-4]
    rest = fname.split('#')

    sample = rest[0].split('_')
    sample_info = [i.strip(']').split('[') for i in rest[1].split('_')]
    parameter = rest[2]

    STD = [i for i in rest if 'std' in i.lower()]

    # convert mass to float
    try:
        sample_info[0][0] = float(sample_info[0][0])
    except ValueError:
        pass

    # convert height to float
    try:
        sample_info[1][0] = float(sample_info[1][0])
    except ValueError:
        pass

    # convert diameter to float
    try:
        sample_info[2][0] = float(sample_info[2][0])
    except ValueError:
        pass

    if sample_info[1][1] and sample_info[2][1]:
        if sample_info[1][1] != sample_info[2][1]:
            sample_info[1][0] = sample_info[1][0] * getattr(ureg, sample_info[2][1]).to(
                getattr(ureg, sample_info[1][1])).magnitude

    abbrev = {'HYS': 'hysteresis',
              'COE': 'backfield',
              'RMP': 'thermocurve',
              'TT': 'thellier',
              'CRY': 'cryomag',
              'SUSH': 'sushibar'}

    try:
        abbrev[sample[2]]
    except KeyError:
        print '%s not implemented yet' % sample[2]
        return
    out = {
        'sample_group': sample[0],
        'name': sample[1],
        'mtype': abbrev[sample[2]],
        'machine': abbrev[sample[3]],
        'mfile': join(data_dir, fname),
        'treatments': parameter,
        'STD': STD,
        'idx': index
    }

    if sample_info[0][0]:
        out.update({'mass': sample_info[0][0],
                    'mass_unit': sample_info[0][1]})
    if sample_info[1][0]:
        out.update({'diameter': sample_info[1][0],
                    'length_unit': sample_info[1][1]})
    if sample_info[2][0]:
        out.update({'height': sample_info[2][0],
                    'length_unit': sample_info[1][1]})

    return out

def import_folder(folder, name = 'study', study=None):
    """
    imports a whole folder creating a study, sample_groups and samples
    """
    if not study:
        study = RockPy.Study(name=name)
    #get all files in directory
    files = [i for i in os.listdir(folder) if not i == '.DS_Store' if not i.startswith('#')]

    for f in files:


        d = RockPy.extract_info_from_filename(f, folder)

        if not d['sample_group'] in study.samplegroup_names:
            sg = RockPy.SampleGroup(name=d['sample_group'])
            study.add_samplegroup(sg)
        else:
            sg = study.gdict[d['sample_group']]
        if not d['name'] in sg.sample_names:
            s = RockPy.Sample(**d)
            sg.add_samples(s)
        else:
            s = sg.get_samples(snames = d['name'])[0]
        m = s.add_measurement(**d)

    # print study
    # print study.samplegroups
    # print sg
    # print sg.samples
    # print s
    return study