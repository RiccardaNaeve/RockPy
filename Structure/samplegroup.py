__author__ = 'mike'
import logging
import csv
from RockPy.Structure.data import RockPyData
from RockPy.Structure.data import condense
from RockPy import Sample
import RockPy.Functions.general
import numpy as np
import copy
import itertools
from pprint import pprint
from profilehooks import profile

RockPy.Functions.general.create_logger(__name__)


class SampleGroup(object):
    """
    Container for Samples, has special calculation methods
    """
    log = logging.getLogger(__name__)

    count = 0

    def __init__(self, name=None, sample_list=None, sample_file=None, **options):
        SampleGroup.count += 1

        SampleGroup.log.info('CRATING new << samplegroup >>')

        # ## initialize
        if name is None:
            name = 'SampleGroup %04i' % (self.count)

        self.name = name
        self.samples = {}
        self.results = None

        self.color = None


        if sample_file:
            self.import_multiple_samples(sample_file, **options)

        self._info_dict = self.__create_info_dict()

        if sample_list:
            self.add_samples(sample_list)



    def __repr__(self):
        # return super(SampleGroup, self).__repr__()
        return "<RockPy.SampleGroup - << %s - %i samples >> >" % (self.name, len(self.sample_names))

    def __getitem__(self, item):
        if item in self.samples:
            return self.samples[item]
        try:
            return self.sample_list[item]
        except KeyError:
            raise KeyError('SampleGroup has no Sample << %s >>' % item)


    def import_multiple_samples(self, sample_file, length_unit='mm', mass_unit='mg', **options):
        """
        imports a csv file with sample_names masses and dimensions and creates the sample_objects
        :param sample_file:
        :param length_unit:
        :param mass_unit:
        :return:
        """
        reader_object = csv.reader(open(sample_file), delimiter='\t')
        r_list = [i for i in reader_object if not '#' in i]
        header = r_list[0]
        d_dict = {i[0]: {header[j].lower(): float(i[j]) for j in range(1, len(i))} for i in r_list[1:]}
        for sample in d_dict:
            mass = d_dict[sample].get('mass', None)
            height = d_dict[sample].get('height', None)
            diameter = d_dict[sample].get('diameter', None)
            S = Sample(sample, mass=mass, height=height, diameter=diameter, mass_unit=mass_unit,
                       length_unit=length_unit)
            self.samples.update({sample: S})

    def pop_sample(self, sample_name):
        """
        remove samples from sample_group will take str(sample_name), list(sample_name)
        """
        if not isinstance(sample_name, list):
            sample_name = [sample_name]
        for sample in sample_name:
            if sample in self.samples:
                self.samples.pop(sample)
        return self


    # ### DATA properties
    @property
    def sample_list(self):
        return self.slist

    @property
    def sample_names(self):
        return sorted(self.samples.keys())

    def add_samples(self, s_list):
        """
        Adds a sample to the sample dictionary and adds the sample_group to sample.sample_groups

        Parameters
        ----------
           s_list: single item or list
              single items get transformed to list

        Note
        ----
           Uses _item_to_list for list conversion
        """

        s_list = _to_list(s_list)
        self.samples.update(self._sdict_from_slist(s_list=s_list))

        for s in s_list:
            s.sgroups.append(self)
            self.add_s2_info_dict(s)

    def remove_samples(self, s_list):
        """
        Removes a sample from the sgroup.samples dictionary and removes the sgroup from sample.sgroups

        Parameters
        ----------
           s_list: single item or list
              single items get transformed to list

        Note
        ----
           Uses _item_to_list for list conversion
        """

        s_list = _to_list(s_list)
        for s in s_list:
            self.sdict[s].sgroups.remove(self)
            self.samples.pop(s)

    # ## components of container
    # lists
    @property
    def slist(self):
        out = [self.samples[i] for i in sorted(self.samples.keys())]
        return out

    @property
    def sdict(self):
        return {s.name: s for s in self.sample_list}

    @property
    def mtypes(self):
        out = [sample.mtypes for sample in self.sample_list]
        return self.__sort_list_set(out)

    @property
    def ttypes(self):
        out = []
        for sample in self.sample_list:
            out.extend(sample.ttypes)
        return self.__sort_list_set(out)

    @property
    def tvals(self):
        out = []
        for sample in self.sample_list:
            out.extend(sample.tvals)
        return self.__sort_list_set(out)

    # measurement: samples
    @property
    def mtype_sdict(self):
        out = {mtype: self.get_samples(mtypes=mtype) for mtype in self.mtypes}
        return out

    # mtype: ttypes
    @property
    def mtype_ttype_dict(self):
        """
        returns a list of tratment types within a certain measurement type
        """
        out = {}
        for mtype in self.mtypes:
            aux = []
            for s in self.get_samples(mtypes=mtype):
                for t in s.mtype_tdict[mtype]:
                    aux.extend([t.ttype])
            out.update({mtype: self.__sort_list_set(aux)})
        return out


    # mtype: tvals
    @property
    def mtype_tvals_dict(self):
        """
        returns a list of tratment types within a certain measurement type
        """
        out = {}
        for mtype in self.mtypes:
            aux = []
            for s in self.get_samples(mtypes=mtype):
                for t in s.mtype_tdict[mtype]:
                    aux.extend([t.value])
            out.update({mtype: self.__sort_list_set(aux)})
        return out

    @property
    def ttype_tval_dict(self):
        ttype_tval_dict = {i: self._get_all_treatment_values(i) for i in self.ttypes}
        return ttype_tval_dict

    @property
    def mtype_dict(self):
        m_dict = {i: [m for s in self.sample_list for m in s.get_measurements(i)] for i in self.mtypes}
        return m_dict

    def _get_all_treatment_values(self, ttype):
        return sorted(list(set([n.value for j in self.sample_list for i in j.measurements for n in i.treatments
                                if n.ttype == ttype])))

    @property
    def mtypes(self):
        """
        looks through all samples and returns measurement types
        """
        return sorted(list(set([i.mtype for j in self.sample_list for i in j.measurements])))

    @property
    def ttypes(self):
        """
        looks through all samples and returns measurement types
        """
        return sorted(list(set([t for sample in self.sample_list for t in sample.ttypes])))

    def ttype_results(self, **parameter):
        if not self.results:
            self.results = self.calc_all(**parameter)
        ttypes = [i for i in self.results.column_names if 'ttype' in i]
        out = {i.split()[1]: {round(j, 2): None for j in self.results[i].v} for i in ttypes}

        for ttype in out:
            for tval in out[ttype]:
                key = 'ttype ' + ttype
                idx = np.where(self.results[key].v == tval)[0]
                out[ttype][tval] = self.results.filter_idx(idx)
        return out

    def _sdict_from_slist(self, s_list):
        """
        creates a dictionary with s.name:s for each sample in a list of samples

        Parameters
        ----------
           s_list: sample or list
        Returns
        -------
           dict
              dictionary with {sample.name : sample} for each sample in s_list

        Note
        ----
           uses _to_list for item -> list conversion
        """
        s_list = _to_list(s_list)

        out = {s.name: s for s in s_list}
        return out


    def calc_all(self, **parameter):
        for sample in self.sample_list:
            label = sample.name
            sample.calc_all(**parameter)
            results = sample.results
            if self.results is None:
                self.results = RockPyData(column_names=results.column_names,
                                          data=results.data, row_names=[label for i in results.data])
            else:
                rpdata = RockPyData(column_names=results.column_names,
                                    data=results.data, row_names=[label for i in results.data])
                self.results = self.results.append_rows(rpdata)
        return self.results

    def average_results(self, **parameter):
        """
        makes averages of all calculations for all samples in group. Only samples with same treatments are averaged

        prams: parameter are calculation parameters, has to be a dictionary
        """
        substfunc = parameter.pop('substfunc', 'mean')
        out = None
        ttype_results = self.ttype_results(**parameter)
        for ttype in ttype_results:
            for tval in sorted(ttype_results[ttype].keys()):
                aux = ttype_results[ttype][tval]
                aux.define_alias('variable', 'ttype ' + ttype)
                aux = condense(aux, substfunc=substfunc)
                if out == None:
                    out = {ttype: aux}
                else:
                    out[ttype] = out[ttype].append_rows(aux)
        return out


    def __add__(self, other):
        self_copy = SampleGroup(sample_list=self.sample_list)
        self_copy.samples.update(other.samples)
        return self_copy

    def _mlist_to_tdict(self, mlist):
        """
        takes a list of measurements looks for common ttypes
        """
        ttypes = sorted(list(set([m.ttypes for m in mlist])))
        return {ttype: [m for m in mlist if ttype in m.ttypes] for ttype in ttypes}

    def get_measurements(self, sname=None, mtype=None, ttype=None, tval=None, tval_range=None):
        """
        Wrapper, for finding measurements, calls get_samples first and sample.get_measurements
        """
        samples = self.get_samples(sname, mtype, ttype, tval, tval_range)
        out = []
        for sample in samples:
            try:
                out.extend(sample.get_measurements(mtype, ttype, tval, tval_range, filtered=True))
            except TypeError:
                pass
        return out


    def delete_measurements(self, sname=None, mtype=None, ttype=None, tval=None, tval_range=None):
        """
        deletes measurements according to criteria
        """
        samples = self.get_samples(snames=sname, mtypes=mtype, ttypes=ttype, tvals=tval,
                                   tval_range=tval_range)  # search for samples with measurement fitting criteria
        for sample in samples:
            sample.delete_measurements(mtype=mtype, ttype=ttype, tval=tval,
                                       tval_range=tval_range)  # individually delete measurements from samples

    def get_samples(self, snames=None, mtypes=None, ttypes=None, tvals=None, tval_range=None):
        """
        Primary search function for all parameters
        """
        if tvals is None:
            t_value = np.nan
        else:
            t_value = tvals

        out = []

        if snames:
            snames = _to_list(snames)
            for s in snames:
                try:
                    out.append(self.samples[s])
                except KeyError:
                    raise KeyError('RockPy.sample_group does not contain sample << %s >>' % s)
            if len(out) == 0:
                raise KeyError('RockPy.sample_group does not contain any samples')
                return

        else:
            out = self.sample_list

        if mtypes:
            mtypes = _to_list(mtypes)
            out = [s for s in out for mtype in mtypes if mtype in s.mtypes]

        if len(out) == 0:
            raise KeyError('RockPy.sample_group does not contain sample with mtypes: << %s >>' % mtypes)
            return

        if ttypes:
            ttypes = _to_list(ttypes)
            out = [s for s in out for ttype in ttypes if ttype in s.ttypes]
            if len(out) == 0:
                raise KeyError('RockPy.sample_group does not contain sample with ttypes: << %s >>' % ttypes)
                return

        if tvals:
            tvals = _to_list(tvals)
            out = [s for s in out for tval in tvals for ttype in ttypes if tval in s.ttype_tval_dict[ttype]]
            if len(out) == 0:
                self.log.error(
                    'RockPy.sample_group does not contain sample with (ttypes, tvals) pair: << %s, %s >>' % (
                        str(ttypes), str(t_value)))
                return []

        if tval_range:
            if not isinstance(tval_range, list):
                tval_range = [0, tval_range]
            else:
                if len(tval_range) == 1:
                    tval_range = [0] + tval_range

            out = [s for s in out for tv in s.ttype_tval_dict[ttype] for ttype in ttypes
                   if tv <= max(tval_range)
                   if tv >= min(tval_range)]

            if len(out) == 0:
                raise KeyError(
                    'RockPy.sample_group does not contain sample with (ttypes, tval_range) pair: << %s, %.2f >>' % (
                        ttypes, t_value))
                return

        if len(out) == 0:
            SampleGroup.log.error(
                'UNABLE to find sample with << %s, %s, %s, %.2f >>' % (snames, mtypes, ttypes, t_value))

        return out


    def mean_sample(self,
                    reference=None,
                    rtype='mag', dtye='mag', vval=None,
                    norm_method='max',
                    interpolate=True,
                    substfunc='mean'):

        # create new sample_obj
        mean_sample = Sample(name='mean ' + self.name)

        for mtype in self.info_dict['mtype_ttype_tval']:
            if not mtype in ['mass', 'diameter', 'height', 'volume', 'x_len', 'y_len', 'z_len']:
                for ttype in self.info_dict['mtype_ttype_tval'][mtype]:
                    for tval in self.info_dict['mtype_ttype_tval'][mtype][ttype]:
                        samples = self.info_dict['mtype_ttype_tval'][mtype][ttype][tval]
                        measurements = []
                        for s in samples:
                            measurements.extend(s.get_measurements(mtype=mtype, ttype=ttype, tval=tval))

                    if reference or vval:
                        measurements = [m.normalizeNEW(reference=reference, rtype=rtype,
                                                    vval=vval, norm_method=norm_method)
                                        for m in measurements
                                        if m.mtype not in ['diameter', 'height', 'mass']]

                    mean_sample.measurements.extend(measurements)

                    if mtype not in ['diameter', 'height', 'mass']:
                        # calculating the mean of all measurements
                        M = mean_sample.mean_measurement(mtype=mtype, ttype=ttype, tval=tval, substfunc=substfunc)
                        if reference or vval:
                            M.is_normalized = True
                            M.norm = [reference, rtype, vval, norm_method, np.nan]

                        mean_sample.mean_measurements.append(M)

        mean_sample.is_mean = True  #set is_mean flag after all measuerements are created
        return mean_sample

    def average_sample(self, name=None,
                       reference='data',
                       rtype='mag', dtype = 'mag',
                       vval=None, norm_method='max',
                       interpolate=True):
        """
        Averages all samples and returns a sample with an average measurement for all measurements in all samples.
        
        Parameters
        ----------
           name: str
              Name of the samplegroup. *default:* mean_*sample_group_name*
           reference: str
              used for normalize
           rtype:
           vval: 
           norm_method: 
           interpolate: bool
              it True all measurements are interpolated to equal variables and then normalized
        :return:
        """

        if not name:
            name = 'mean ' + self.name

        average_sample = Sample(name=name)
        average_sample.is_mean = True

        for mtype in ['diameter', 'height', 'mass', 'volume']:
            try:
                for ttype in self.mtype_ttype_dict[mtype]:
                    for tval in self.ttype_tval_dict[ttype]:
                        measurements = self.get_measurements(mtype=mtype, ttype=ttype, tval=tval)
                        M = average_sample.mean_measurement_from_list(measurements)
                        average_sample.measurements.append(M)
            except:
                self.log.info('NO %s found' %(mtype))
                
        for mtype in self.mtypes:
            if mtype not in ['diameter', 'height', 'mass', 'volume']:
                for ttype in self.mtype_ttype_dict[mtype]:
                    for tval in self.ttype_tval_dict[ttype]:
                        measurements = self.get_measurements(mtype=mtype, ttype=ttype, tval=tval)
                        measurements = [m.normalize(reference=reference, rtype=rtype, dtype=dtype,
                                                    vval=vval, norm_method=norm_method)
                                        for m in measurements]
                        M = average_sample.mean_measurement_from_list(measurements, interpolate=interpolate)
                        # print average_sample.get_mean_results(mlist=measurements)
                        average_sample.measurements.append(M)

        return average_sample

    def __get_variable_list(self, rpdata_list):
        out = []
        for rp in rpdata_list:
            out.extend(rp['variable'].v)
        return self.__sort_list_set(out)


    def __sort_list_set(self, values):
        """
        returns a sorted list of non duplicate values
        :param values:
        :return:
        """
        return sorted(list(set(values)))

    ''' INFODICT '''

    def __create_info_dict(self):
        """
        creates all info dictionaries

        Returns
        -------
           dict
              Dictionary with a permutation of sample ,type, ttype and tval.
        """
        d = ['mtype', 'ttype', 'tval']
        keys = ['_'.join(i) for n in range(5) for i in itertools.permutations(d, n) if not len(i) == 0]
        out = {i: {} for i in keys}
        return out

    # @profile()
    def add_s2_info_dict(self, s):
        """
        Adds a sample to the infodict.

        Parameters
        ----------
           s: RockPySample
              The sample that should be added to the dictionary
        """

        keys = self.info_dict.keys() # all possible keys

        for key in keys:
            # split keys into levels
            split_keys = key.split('_')
            for i, level in enumerate(split_keys):
                # i == level number, n == maximal level
                # if i == n _> last level -> list instead of dict
                n = len(split_keys) - 1

                #level 0
                for e0 in s.info_dict[key]:
                    # if only 1 level
                    if i == n == 0:
                        # create key with empty list
                        self._info_dict[key].setdefault(e0, list())
                        # add sample if not already in list
                        if not s in self._info_dict[key][e0]:
                            self._info_dict[key][e0].append(s)
                        continue
                    else:
                        # if not last entry generate key: dict() pair
                        self._info_dict[key].setdefault(e0, dict())

                    # level 1
                    for e1 in s.info_dict[key][e0]:
                        if i == n == 1:
                            self._info_dict[key][e0].setdefault(e1, list())
                            if not s in self._info_dict[key][e0][e1]:
                                self._info_dict[key][e0][e1].append(s)
                            continue
                        elif i > 0:
                            self._info_dict[key][e0].setdefault(e1, dict())

                            #level 2
                            for e2 in s.info_dict[key][e0][e1]:
                                if i == n == 2:
                                    self._info_dict[key][e0][e1].setdefault(e2, list())
                                    if not s in self._info_dict[key][e0][e1][e2]:
                                        self._info_dict[key][e0][e1][e2].append(s)
                                    continue
                                elif i > 1:
                                    self._info_dict[key][e0][e1].setdefault(e2, dict())

    def recalc_info_dict(self):
        """
        Recalculates the info_dictionary with information of all samples and their corresponding measurements

        """
        map(self.add_s2_info_dict, self.samples)

    @property
    def info_dict(self):
        """
        Property for easy access of info_dict. If '_info_dict' has not been created, it will create one.
        """
        if not hasattr(self, '_info_dict'):
            self._info_dict = self.__create_info_dict()
            self.recalc_info_dict()
        return self._info_dict


def _to_list(oneormoreitems):
    """
    convert argument to tuple of elements
    :param oneormoreitems: single number or string or list of numbers or strings
    :return: tuple of elements
    """
    return oneormoreitems if hasattr(oneormoreitems, '__iter__') else [oneormoreitems]


def test():
    import RockPy.Tutorials.sample_group

    sg = RockPy.Tutorials.sample_group.get_hys_coe_irm_rmp_sample_group(load=True)
    # print sg.info_dict['sample_mtype_ttype']
    # print sg.info_dict.keys()
    # pprint(sg.info_dict)


if __name__ == '__main__':
    test()
