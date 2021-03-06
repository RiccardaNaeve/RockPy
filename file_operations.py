__author__ = 'mike'
import os
import os.path
from os.path import expanduser, join
from collections import defaultdict
import numpyson
import numpy as np
from pint import UnitRegistry
import RockPy
import cPickle
import RockPy.core

ureg = UnitRegistry()
default_folder = join(expanduser("~"), 'Desktop', 'RockPy')


def save(smthg, file_name, folder=None):
    if not folder:
        folder = default_folder
    with open(join(folder, file_name), 'wb+') as f:
        # dump = numpyson.dumps(smthg)
        dump = cPickle.dumps(smthg)
        f.write(dump)
        f.close()


def load(file_name, folder=None):
    # print 'loading: %s' %join(folder, file_name)
    if not folder:
        folder = default_folder
    with open(join(folder, file_name), 'rb') as f:
        # out = numpyson.loads(f.read())
        out = cPickle.loads(f.read())
    return out


def add_unit(value, unit):
    out = str(value) + '[' + unit + ']'
    return out


def get_fname_from_info(sample_group='', sample_name='',
                       mtype='', machine='',
                       mass='', mass_unit='',
                       height='', height_unit='',
                       diameter='', diameter_unit='',
                       series=list(), svals=[], sunits=[],
                       std=None,
                       idx=None,
                       **options):
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
    :param series:
    :param svals:
    :param sunits:
    :param STD:
    :param idx:
    :return:
    """

    if idx is None:
        idx = '%03i' % (np.random.randint(999, size=1)[0])
    else:
        idx = '%03i' % idx

    # check that series, svals, sunits are lists
    series = RockPy.core.to_list(series)
    svals = RockPy.core.to_list(svals)
    svals = [str(i).replace('.', ',') for i in svals] # replace '.' so no conflict with file ending
    sunits = RockPy.core.to_list(sunits)

    sample = '_'.join([sample_group, sample_name, mtype.upper(), machine.upper()])

    if not height_unit and diameter_unit:
        height_unit = diameter_unit
    elif height_unit and not diameter_unit:
        diameter_unit = height_unit

    sample_info = '_'.join(
        [add_unit(str(mass).replace('.', ','), mass_unit),
         add_unit(str(diameter).replace('.', ','), diameter_unit),
         add_unit(str(height).replace('.', ','), height_unit),
         ])

    params = ';'.join(
        ['_'.join(map(str, [series[i], svals[i], sunits[i]])) for i in range(len(series))])

    if options:
        opt = ';'.join(['_'.join([k, str(v)]) for k, v in sorted(options.iteritems())])
    else:
        opt = ''
    out = '#'.join([sample, sample_info, params, 'STD%03i' %std, opt])
    out += '.%s' % idx
    return out


def get_info_from_fname(path=None):
    """
    extracts the file information out of the filename

    Parameters
    ----------
       fname: str
          file name
       folder: str
          only the folder name of the stored data
       path:
          complete path, with folder/fname. Will be split into the two
    """

    # todo IMPORTANT change get_info_from_fname and aget_fname_fro_info to accept the exact same things.
    # change add_measurement accordingly
    folder = os.path.split(path)[0]
    fname = os.path.split(path)[1]

    mfile = fname

    index = fname.split('.')[-1]
    fname = fname.split('.')[:-1][0]

    rest = fname.split('#')

    sample = rest[0].split('_')
    sample_info = [i.strip(']').split('[') for i in rest[1].split('_')]

    parameter = rest[2]

    try:
        STD = [int(i.lower().strip('std')) for i in rest if 'std' in i.lower()][0]
    except IndexError:
        STD = None

    try:
        options = [i.split('_') for i in rest[4].split('.')[0].split(';')]
        options = {i[0]: i[1] for i in options}
    except IndexError:
        options = None
    # convert mass to float
    try:
        sample_info[0][0] = sample_info[0][0].replace(',', '.')
        sample_info[0][0] = float(sample_info[0][0])
    except ValueError:
        pass

    # convert height to float
    try:
        sample_info[1][0] = sample_info[1][0].replace(',', '.')
        sample_info[1][0] = float(sample_info[1][0])
    except ValueError:
        pass

    # convert diameter to float
    try:
        sample_info[2][0] = sample_info[2][0].replace(',', '.')
        sample_info[2][0] = float(sample_info[2][0])
    except ValueError:
        pass
    if sample_info[1][1] and sample_info[2][1]:
        if sample_info[1][1] != sample_info[2][1]:
            sample_info[1][0] = sample_info[1][0] * getattr(ureg, sample_info[2][1]).to(
                getattr(ureg, sample_info[1][1])).magnitude

    sample[2] = sample[2].upper() #convert to upper for ease of checking
    sample[3] = sample[3].upper() #convert to upper for ease of checking

    abbrev = {'HYS': 'hys',
              'COE': 'backfield',
              'RMP': 'thermocurve',
              'TT': 'thellier',
              'TRM': 'trm',
              'AF': 'afdemag',
              'ARM': 'ARM',
              'IRM': 'IRM',
              'CRY': 'cryomag',
              'SUSH': 'sushibar',
              'VSM':'VSM',
              'FORC':'forc',
              'VISC':'viscosity',
              }

    rev_abbrev = {v: k for k, v in abbrev.iteritems()}

    try:
        abbrev[sample[2]]
    except KeyError:
        raise KeyError('%s not implemented yet' % sample[2])
        return

    out = {
        'sample_group': sample[0],
        'name': sample[1],
        'mtype': abbrev[sample[2]],
        'machine': abbrev[sample[3]],
        'mfile': join(folder, mfile),
        'series': parameter,
        'std': STD,
        'idx': int(index)
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
    if options:
        out.update(options)

    return out


def import_folderOLD(folder, name='study', study=None):
    """
    imports a whole folder creating a study, sample_groups and samples
    """
    if not study:
        study = RockPy.Study(name=name)
    # get all files in directory
    files = [i for i in os.listdir(folder) if not i == '.DS_Store' if not i.startswith('#')]

    for f in files:
        d = RockPy.get_info_from_fname(f, folder)
        if 'IS' in d and d['IS']:
            pass
        if not d['sample_group'] in study.samplegroup_names:
            sg = RockPy.SampleGroup(name=d['sample_group'])
            study.add_samplegroup(sg)
        else:
            sg = study.gdict[d['sample_group']]
        if not d['name'] in sg.sample_names:
            s = RockPy.Sample(**d)
            sg.add_samples(s)
        else:
            s = sg.get_samples(snames=d['name'])[0]
        m = s.add_measurement(**d)

        if 'ISindex'in d:
            idx = [(i, f) for i, f in enumerate(files) if d['ISindex'] in f.split('.')[-1] if 'IS_True' in f] #initial_state index
            if len(idx) >1:
                print 'more than one initial state found not adding any'
            else:
                initial = RockPy.get_info_from_fname(files[idx[0]], folder)
                del files[idx[0]]
                m.set_initial_state(**initial)


    # print study
    # print study.samplegroups
    # print sg
    # print sg.samples
    # print s
    return study


def import_folder(folder, name='study', study=None):
    if not study:
        study = RockPy.Study(name=name)

    files = [i for i in os.listdir(folder) if not i == '.DS_Store' if not i.startswith('#')]
    samples = defaultdict(list)

    for i in files:
        d = RockPy.get_info_from_fname(join(folder, i))
        samples[d['name']].append(d)

    for s in samples:
        sgroup_name = samples[s][0]['sample_group']
        if not sgroup_name in study.samplegroup_names:
            sg = RockPy.SampleGroup(name=samples[s][0]['sample_group'])
            study.add_samplegroup(sg)
        sg = study[sgroup_name]
        if not s in study.sdict:
            smpl = RockPy.Sample(**samples[s][0])
            sg.add_samples(smpl)
        for m in samples[s]:
            measurement = smpl.add_measurement(**m)
            if 'ISindex' in m:
                initial = get_IS(m, samples[s])
                measurement.set_initial_state(**initial)
                samples[s].remove(initial)
            if 'IS' in m and m['IS'] == True:
                continue
    return study