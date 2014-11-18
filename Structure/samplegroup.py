__author__ = 'mike'
import logging
import csv

from RockPy import Sample
import RockPy.Functions.general


class SampleGroup(object):
    RockPy.Functions.general.create_logger('RockPy.SAMPLEGROUP')


    def __init__(self, sample_file=None, **options):
        self.log = logging.getLogger('RockPy.SAMPLEGROUP.' + type(self).__name__)
        self.log.info('CRATING new << samplegroup >>')

        # ## initialize
        self.samples = {}

        if sample_file:
            self.import_multiple_samples(sample_file, **options)

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
        if sample_name in self.samples:
            self.samples.pop(sample_name)
        return self

    @property
    def sample_list(self):
        out = [self.samples[i] for i in sorted(self.samples.keys())]
        return out

    @property
    def treatment_dict(self):
        """
        returns all treatments and lust of values as dictionaty
        """
        t_dict = {i: {j: self._get_measurements_with_treatment(i, j) for j in self._get_all_treatment_values(i)} for i in
                  self.treatment_types}
        return t_dict

    def _get_all_treatment_values(self, ttype):
        return sorted(list(set([n.value for j in self.sample_list for i in j.measurements for n in i.treatments
                                if n.ttype == ttype])))

    def _get_measurements_with_treatment(self, ttype, tvalue):
        out = [m
               for sample in self.sample_list
               for m in sample.get_measurements_with_treatment(ttype)
               for t in m.treatments
               if t.value == tvalue]
        return out

    @property
    def treatment_types(self):
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

    # todo export

    def export_cryomag(self):
        raise NotImplemented()