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
log = logging.getLogger(__name__)


class SampleGroup(object):
    """
    Container for Samples, has special calculation methods
    """

    count = 0

    def __init__(self, name=None, sample_list=None, sample_file=None, **options):
        SampleGroup.count += 1

        self.log = log  # logging.getLogger('RockPy.' + type(self).__name__)
        self.log.info('CRATING new << samplegroup >>')

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

    def __getitem__(self, item):
        if item in self.samples:
            return self.samples[item]
        try:
            return self.sample_list[item].name
        except KeyError:
            raise KeyError('SampleGroup has no Sample << %s >>' %item)

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

    # ## components of container
    # lists
    @property
    def slist(self):
        out = [self.samples[i] for i in sorted(self.samples.keys())]
        return out

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
        return sorted(list(set(out)))

    # ## sample-stage
    @property
    def sname_mdict(self):
        out = {s.name: s.mtype_mdict for s in self.slist}
        return out

    @property
    def sname_tdict(self):
        out = {s.name: s.ttype_dict for s in self.slist}
        return out

    @property
    def sname_tvals(self):
        out = {s.name: s.tvals for s in self.slist}
        return out

    @property
    def sname_mtype_ttype_tval_mdict(self):
        out = {s.name: s.mtype_ttype_tval_mdict for s in self.slist}
        return out

    # ## measurement stage

    # measurement: samples
    @property
    def mtype_sdict(self):
        out = {mtype: self.get_samples(mtype=mtype) for mtype in self.mtypes}
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
            for s in self.get_samples(mtype=mtype):
                for t in s.mtype_tdict[mtype]:
                    aux.extend([t.ttype])
            out.update({mtype: self.__sort_list_set(aux)})
        return out

    @property
    def mtype_ttype_mdict(self):
        """
        returns a list of tratment types within a certain measurement type
        """
        out = {}
        for mtype in self.mtypes:
            for s in self.get_samples(mtype=mtype):
                for t in s.mtype_ttype_dict[mtype]:
                    aux = {t: s.mtype_ttype_mdict[mtype][t]}
            out.update({mtype: aux})
        return out

    @property
    def mtype_ttype_sdict(self):
        """
        returns a list of tratment types within a certain measurement type
        """
        out = {}
        for mtype in self.mtypes:
            for s in self.get_samples(mtype=mtype):
                for t in s.mtype_ttype_dict[mtype]:
                    aux = {t: self.get_samples(mtype=mtype, ttype=t)}
            out.update({mtype: aux})
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
            for s in self.get_samples(mtype=mtype):
                for t in s.mtype_tdict[mtype]:
                    aux.extend([t.value])
            out.update({mtype: self.__sort_list_set(aux)})
        return out

    @property
    def sample_names(self):
        return sorted(self.samples.keys())

    @property
    def treatment_dict(self):
        """
        returns all treatments and lust of values as dictionaty
        """
        t_dict = {i: {j: self._get_measurements_with_treatment(i, j) for j in self._get_all_treatment_values(i)} for i
                  in
                  self.treatment_types}
        return t_dict

    @property
    def ttype_dict(self):
        """
        returns all treatments and lust of values as dictionaty
        """
        t_dict = {i: {j: self._get_measurements_with_treatment(i, j) for j in self._get_all_treatment_values(i)} for i
                  in
                  self.ttypes}
        return t_dict

    @property
    def sample_mtype_ttype_dict(self):
        """
        generates a dictionary with sample: measurement: treatment: treatment_value: measurement(sample, mtype, ttype, tval)
        """
        out = {name: object.mtype_ttype_tval_mdict for name, object in self.samples.iteritems()}
        return out

    @property
    def mtype_sample_dict(self):
        out = {mtype: {sample.name: {ttype: {tval: sample.get_measurements(ttype=ttype, tval=tval, mtype=mtype)
                                             for tval in sample.ttype_tval_dict[ttype]}
                                     for ttype in sample.ttype_tval_dict}
                       for sample in self.get_samples(mtype=mtype)}
               for mtype in self.mtypes}
        return out

    @property
    def mtype_ttype_sample_dict(self):
        out = {mtype: {ttype: {sample.name: {tval: sample.get_measurements(ttype=ttype, tval=tval, mtype=mtype)
                                             for tval in sample.ttype_tval_dict[ttype]}
                               for sample in self.get_samples(mtype=mtype, ttype=ttype)}
                       for ttype in self.ttypes}
               for mtype in self.mtypes}
        return out

    @property
    def mtype_ttype_tval_mdict(self):
        out = {mtype: {ttype: {tval: self.get_measurements(ttype=ttype, tval=tval, mtype=mtype)
                               for tval in self.ttype_dict[ttype]
        }
                       for ttype in self.mtype_ttype_mdict[mtype]}
               for mtype in self.mtypes}
        return out

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

    def ttype_results(self, parameter):
        if not self.results:
            self.calc_all(**parameter)
        ttypes = [i for i in self.results.column_names if 'ttype' in i]
        out = {i.split()[1]: {round(j, 2): None for j in self.results[i].v} for i in ttypes}

        for ttype in out:
            for tval in out[ttype]:
                key = 'ttype ' + ttype
                idx = np.where(self.results[key].v == tval)[0]
                out[ttype][tval] = self.results.filter_idx(idx)
        return out

    def _get_measurements_with_treatment(self, ttype, tvalue):
        out = [m
               for sample in self.sample_list
               for m in sample.get_measurements_with_treatment(ttype)
               for t in m.treatments
               if t.value == tvalue]
        return out

    def _sdict_from_slist(self, s_list):
        if not type(s_list) is list:
            s_list = [s_list]
        out = {s.name: s for s in s_list}
        return out

    def add_samples(self, s_list):
        self.samples.update(self._sdict_from_slist(s_list=s_list))

    @property
    def treatment_types(self):  # todo delete
        treatments = list(set([n.ttype for j in self.sample_list for i in j.measurements for n in i.treatments]))
        return sorted(treatments)


    def calc_all(self, **parameter):
        self.results = None
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

    def average_results(self, parameter):
        """
        makes averages of all calculations for all samples in group. Only samples with same treatments are averaged

        prams: parameter are calculation parameters, has to be a dictionary
        """
        substfunc = parameter.pop('substfunc', 'mean')
        out = None
        ttype_results = self.ttype_results(parameter=parameter)
        for ttype in ttype_results:
            for tval in sorted(ttype_results[ttype].keys()):
                aux = ttype_results[ttype][tval]
                aux.define_alias('variable', 'ttype ' + ttype)
                aux = aux.eliminate_duplicate_variable_rows(substfunc=substfunc)
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
                out.extend(sample.get_measurements(mtype, ttype, tval, tval_range))
            except TypeError:
                pass
        return out

    def get_samples(self, sname=None, mtype=None, ttype=None, tval=None, tval_range=None):
        """
        Primary search function for all parameters

        """
        if tval is None:
            t_value = np.nan
        else:
            t_value = tval

        if sname:
            if isinstance(sname, str):
                try:
                    out = [self.samples[sname]]
                except KeyError:
                    raise KeyError('RockPy.sample_group does not contain sample << %s >>' % sname)
            if isinstance(sname, list):
                out = []
                for s in sname:
                    try:
                        out.append(self.samples[s])
                    except KeyError:
                        raise KeyError('RockPy.sample_group does not contain sample << %s >>' % s)
        else:
            out = self.sample_list
            if len(out) == 0:
                raise KeyError('RockPy.sample_group does not contain any samples')
                return

        if mtype:
            if isinstance(mtype, list):
                out = [s for s in out for mt in mtype if mt in s.mtypes]
            else:
                out = [s for s in out if mtype in s.mtypes]
            if len(out) == 0:
                raise KeyError('RockPy.sample_group does not contain sample with mtype: << %s >>' % mtype)
                return
        if ttype:
            if isinstance(ttype, list):
                out = [s for s in out for tt in ttype if tt in s.ttypes]
            else:
                out = [s for s in out if ttype in s.ttypes]
            if len(out) == 0:
                raise KeyError('RockPy.sample_group does not contain sample with ttype: << %s >>' % ttype)
                return

            if tval:
                if isinstance(tval, list):
                    out = [s for s in out for tv in tval if tv in s.ttype_tval_dict[ttype]]
                else:
                    out = [s for s in out if tval in s.ttype_tval_dict[ttype]]
                if len(out) == 0:
                    raise KeyError(
                        'RockPy.sample_group does not contain sample with (ttype, tval) pair: << %s, %.2f >>' % (
                            ttype, t_value))
                    return

            if tval_range:
                if not isinstance(tval_range, list):
                    tval_range = [0, tval_range]
                else:
                    if len(tval_range) == 1:
                        tval_range = [0] + tval_range

                out = [s for s in out for tv in s.ttype_tval_dict[ttype]
                       if tv <= max(tval_range)
                       if tv >= min(tval_range)]
                if len(out) == 0:
                    raise KeyError(
                        'RockPy.sample_group does not contain sample with (ttype, tval_range) pair: << %s, %.2f >>' % (
                            ttype, t_value))
                    return

        if len(out) == 0:
            self.log.error('UNABLE to find sample with << %s, %s, %s, %.2f >>' % (sname, mtype, ttype, t_value))

        return out

    def get_average_mtype_sample(self, mtype, reference, name='average_sample_group',
                                 rtype='mag', vval=None, norm_method='max'):

        average_sample = Sample(name=name)
        dict = self.mtype_ttype_tval_mdict
        data = {}
        is_data = {}

        for ttype in dict[mtype]:  # cycle through treatments
            data[ttype] = {}
            is_data[ttype] = {}
            for tval in dict[mtype][ttype]:  #cycle through treatment values
                data[ttype][tval] = {}
                is_data[ttype][tval] = {}
                for measurement in dict[mtype][ttype][
                    tval]:  #cycle through all measurements & samples (all measurements with ttype = ttype & mtype = mtype)
                    m = measurement.normalize(reference=reference, rtype=rtype, vval=vval,
                                              norm_method=norm_method)  # normalize each individual measurement
                    if measurement.initial_state:  # initial states have to be normalized, too
                        m_is = measurement.initial_state.normalize(reference=reference, rtype=rtype, vval=vval,
                                                                   norm_method=norm_method)  # normalize each individual measurement
                    # the data has to be ordered according to the data type (e.g. down_field
                    for d in m.data:  # some measurements have multiple data sets, like hysteresis
                        if not d in data[ttype][tval]:
                            data[ttype][tval][d] = []
                        data[ttype][tval][d].append(m.data[d])  # store corresponding dataset in dictionary
                    for d in m_is.data:
                        if not d in is_data[ttype][tval]:
                            is_data[ttype][tval][d] = []
                        is_data[ttype][tval][d].append(m_is.data[d])  # store corresponding dataset in dictionary

        for ttype in data:  # cycle throu different treatment types
            for tval in data[ttype]:  # cycle through the values
                average_data = {}  # initialize the average data dictionary
                for dtype in data[ttype][tval]:  # average the data types
                    var_list = self.__get_variable_list(data[ttype][tval][dtype])  # get variable lists
                    if len(var_list) > 1:
                        aux = [m.interpolate(var_list) for m in data[ttype][tval][dtype]]
                    else:
                        aux = [m for m in data[ttype][tval][dtype]]
                    rp_data = condense(aux)
                    rp_data = rp_data.sort('variable')
                    average_data.update({dtype: rp_data})
                measurement = dict[mtype][ttype][tval][0]  # set the average to be the first measurement
                average_measurement = measurement
                for dtype in average_data:
                    average_measurement._data[dtype] = average_data[dtype]
                average_sample.measurements.append(average_measurement)

        # ### setting average initial states
        for ttype in is_data:
            for tval in is_data[ttype]:
                m = average_sample.get_measurements(mtype=mtype, ttype=ttype, tval=tval)
                for dtype in m_is.data:
                    aux = [m for m in is_data[ttype][tval][dtype]]
                    m_is._data[dtype] = condense(aux)
                m.initial_state = m_is
                if hasattr(m, 'reset_data'):
                    m.reset_data()
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