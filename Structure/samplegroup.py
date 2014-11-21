__author__ = 'mike'
import logging
import csv

from RockPy import Sample
import RockPy.Functions.general
import numpy as np

RockPy.Functions.general.create_logger('RockPy')


class SampleGroup(object):
    def __init__(self, sample_list=None, sample_file=None, **options):
        self.log = logging.getLogger('RockPy.' + type(self).__name__)
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

    @property
    def slist(self):
        out = [self.samples[i] for i in sorted(self.samples.keys())]
        return out

    @property
    def mtypes(self):
        out = []

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

    def average_mtype(self, mtype):
        try:
            self.log.debug('AVERAGING: << %s >>' % type)
            measurements = self.mtype_dict[mtype]
            print measurements[0].tdict
        except KeyError:
            self.log.error('CANT find mtype: << %s >>' % type)

    def _mlist_to_tdict(self, mlist):
        """
        takes a list of measurements looks for common ttypes
        """
        ttypes = sorted(list(set([m.ttypes for m in mlist])))
        return {ttype: [m for m in mlist if ttype in m.ttypes] for ttype in ttypes}

    def export_cryomag(self):
        raise NotImplemented()

    def _get_sample(self, sname=None, mtype=None, ttype=None, tval=None):
        """
        Primary search function for all parameters

        """
        if tval is None:
            t_value = np.nan
        else:
            t_value = tval

        if sname:
            try:
                out = [self.samples[sname]]
            except KeyError:
                raise KeyError('RockPy.sample_group does not contain sample << %s >>' % sname)
        else:
            out = self.sample_list
            if len(out) == 0:
                raise KeyError('RockPy.sample_group does not contain any samples')
                return

        if mtype:
            out = [s for s in out if mtype in s.mtypes]
            if len(out) == 0:
                raise KeyError('RockPy.sample_group does not contain sample with mtype: << %s >>' % mtype)
                return
        if ttype:
            out = [s for s in out if ttype in s.ttypes]
            if len(out) == 0:
                raise KeyError('RockPy.sample_group does not contain sample with ttype: << %s >>' % ttype)
                return

            if tval:
                out = [s for s in out if tval in s.ttype_tval_dict[ttype]]
                if len(out) == 0:
                    raise KeyError('RockPy.sample_group does not contain sample with (ttype, tval) pair: << %s, %.2f >>' %(ttype ,t_value))
                    return
        if len(out) == 0:
            self.log.error('UNABLE to find sample with << %s, %s, %s, %.2f >>' % (sname, mtype, ttype, t_value))
        return out