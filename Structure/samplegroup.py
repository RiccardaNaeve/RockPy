__author__ = 'mike'
import logging
import csv
from RockPy.Structure.data import condense
from RockPy import Sample
import RockPy.Functions.general
import numpy as np


RockPy.Functions.general.create_logger(__name__)
log = logging.getLogger(__name__)

class SampleGroup(object):
    def __init__(self, sample_list=None, sample_file=None, **options):
        self.log = log #logging.getLogger('RockPy.' + type(self).__name__)
        self.log.info('CRATING new << samplegroup >>')

        # ## initialize
        self.samples = {}

        if sample_file:
            self.import_multiple_samples(sample_file, **options)

        if sample_list:
            self.add_samples(sample_list)


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

    ### components of container
    #lists
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

    ### sample-stage
    @property
    def sname_mdict(self):
        out = {s.name: s.mtype_dict for s in self.slist}
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
        out = {s.name: s.mtype_ttype_tval_dict for s in self.slist}
        return out

    ### measurement stage

    #measurement: samples
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
        return self.samples.keys()

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
        out = {name: object.mtype_ttype_tval_dict for name, object in self.samples.iteritems()}
        return out

    @property
    def mtype_sample_dict(self):
        out = {mtype : {sample.name: {ttype: {tval : sample.get_measurements(ttype=ttype, tval=tval, mtype=mtype)
                                              for tval in sample.ttype_tval_dict[ttype]}
                                 for ttype in sample.ttype_tval_dict}
                        for sample in self.get_samples(mtype=mtype)}
               for mtype in self.mtypes}
        return out

    @property
    def mtype_ttype_sample_dict(self):
        out = {mtype : {ttype: {sample.name: {tval : sample.get_measurements(ttype=ttype, tval=tval, mtype=mtype)
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

    def get_results(self, mtype, **parameter):
        i = 0
        data = []
        for sample in self.sample_list:
            measurements = sample.get_measurements(mtype)
            for measurement in measurements:
                aux = []
                measurement.calc_all(**parameter)
                if i == 0:
                    header = ['sample_name']
                    header = measurement.results.column_names
                aux = [sample.name + '.' + measurement.suffix]
                aux += measurement.results.data
                i += 1
                data.append(aux)
            print(data)
            # self.results = RockPyData(column_names=header, data=data)

    def __add__(self, other):
        self.samples.update(other.samples)
        return self

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
                    raise KeyError('RockPy.sample_group does not contain sample with (ttype, tval) pair: << %s, %.2f >>' %(ttype ,t_value))
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
                    raise KeyError('RockPy.sample_group does not contain sample with (ttype, tval_range) pair: << %s, %.2f >>' %(ttype ,t_value))
                    return



        if len(out) == 0:
            self.log.error('UNABLE to find sample with << %s, %s, %s, %.2f >>' % (sname, mtype, ttype, t_value))

        return out

    def get_average_mtype_sample(self, mtype, reference, name = 'average_sample_group',
                           rtype='mag', vval=None, norm_method='max'):

        average_sample = Sample(name = name)
        dict = self.mtype_ttype_tval_mdict
        data = {}
        for ttype in dict[mtype]: #cycle through treatments
            data[ttype]={}
            for tval in dict[mtype][ttype]: #cycle through treatment values
                data[ttype][tval]={}
                for measurement in dict[mtype][ttype][tval]: #cycle through all measurements & samples (all measurements with ttype = ttype & mtype = mtype)
                    m = measurement.normalize(reference=reference, rtype=rtype, vval=vval, norm_method=norm_method) # normalize each individual measurement
                    for d in m.data: # some measurements have multiple data sets, like hysteresis
                        if not d in data[ttype][tval]:
                            data[ttype][tval][d]=[]
                        data[ttype][tval][d].append(m.data[d]) # store corresponding dataset in dictionary
        # from pprint import pprint
        # pprint(data)

        for ttype in data:
            for tval in data[ttype]:
                average_data = {}
                for dtype in data[ttype][tval]:
                    var_list = self.__get_variable_list(data[ttype][tval][dtype])
                    if len(var_list) > 1:
                        aux = [m.interpolate(var_list) for m in data[ttype][tval][dtype]]
                    else:
                        aux = [m for m in data[ttype][tval][dtype]]
                    aux = condense(aux)
                    aux = aux.sort('temp')
                    average_data.update({dtype:aux})
                measurement = dict[mtype][ttype][tval][0]
                average_measurement = measurement
                average_measurement.data = average_data
                average_sample.measurements.append(average_measurement)
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