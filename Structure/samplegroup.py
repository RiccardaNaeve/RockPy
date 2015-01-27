__author__ = 'mike'
import logging
import csv
from RockPy.Structure.data import RockPyData
from RockPy.Structure.data import condense
from RockPy import Sample
import RockPy.Functions.general
import numpy as np
import copy


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

        if sample_file:
            self.import_multiple_samples(sample_file, **options)

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
        self.samples.update(self._sdict_from_slist(s_list=s_list))

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
        s_list = RockPy.Functions.general._to_list(s_list)

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

    def export_cryomag(self):
        raise NotImplemented()

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


    def mean_sample(self, reference=None,
                    rtype='mag', vval=None,
                    norm_method='max',
                    interpolate=True):

        #create new sample_obj
        mean_sample = Sample(name='mean ' + self.name)
        mean_sample.is_mean = True #set is_mean flag

        for mtype in self.mtypes:
            for ttype in self.mtype_ttype_dict[mtype]:
                for tval in self.ttype_tval_dict[ttype]:
                    measurements = self.get_measurements(mtype=mtype, ttype=ttype, tval=tval)
                    if reference or vval:
                        measurements = [m.normalize(reference=reference, rtype=rtype,
                                                    vval=vval, norm_method=norm_method)
                                        for m in measurements
                                        if m.mtype not in ['diameter', 'height', 'mass']]
                    mean_sample.measurements.extend(measurements)
                    if mtype not in ['diameter', 'height', 'mass']:
                        print mtype
                        M = mean_sample.mean_measurement(mtype=mtype, ttype=ttype, tval=tval)
                        print M
                        # mean_sample.mean_measurements.append(M)
        return mean_sample

    def average_sample(self, reference='nrm', name='mean_sample_group',
                       rtype='mag', vval=None, norm_method='max', interpolate=True):

        average_sample = Sample(name='mean ' + self.name)
        average_sample.is_mean = True

        for mtype in ['diameter', 'height', 'mass']:
            for ttype in self.mtype_ttype_dict[mtype]:
                for tval in self.ttype_tval_dict[ttype]:
                    measurements = self.get_measurements(mtype=mtype, ttype=ttype, tval=tval)
                    M = average_sample.mean_measurement_from_list(measurements)
                    average_sample.measurements.append(M)

        for mtype in self.mtypes:
            if mtype not in ['diameter', 'height', 'mass']:
                for ttype in self.mtype_ttype_dict[mtype]:
                    for tval in self.ttype_tval_dict[ttype]:
                        measurements = self.get_measurements(mtype=mtype, ttype=ttype, tval=tval)
                        measurements = [m.normalize(reference=reference, rtype=rtype,
                                                    vval=vval, norm_method=norm_method)
                                        for m in measurements]
                        M = average_sample.mean_measurement_from_list(measurements, interpolate=interpolate)
                        print average_sample.get_mean_results(mlist=measurements)

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


def _to_list(oneormoreitems):
    """
    convert argument to tuple of elements
    :param oneormoreitems: single number or string or list of numbers or strings
    :return: tuple of elements
    """
    return oneormoreitems if hasattr(oneormoreitems, '__iter__') else [oneormoreitems]