__author__ = 'mike'
import logging
import csv

from RockPy import Sample
import Functions.general


class SampleGroup(object):
    Functions.general.create_logger('RockPy.SAMPLEGROUP')


    def __init__(self, sample_file=None, **options):
        self.log = logging.getLogger('RockPy.SAMPLEGROUP.' + type(self).__name__)
        self.log.info('CRATING new << samplegroup >>')

        # ## initialize
        self.samples = {}
        self.sample_list = []

        if sample_file:
            self.import_multiple_samples(sample_file, **options)
        self._resort_sample_list()

    def import_multiple_samples(self, sample_file, length_unit='mm', mass_unit='mg', **options):
        """
        imports a csv file with sample_names masses and dimensions and creates the sample_objects
        :param sample_file:
        :param length_unit:
        :param mass_unit:
        :return:
        """
        reader_object = csv.reader(open(sample_file), delimiter='\t')
        r_list = [i for i in reader_object]
        header = r_list[0]
        d_dict = {i[0]: {header[j].lower(): float(i[j]) for j in range(1, len(i))} for i in r_list[1:]}
        for sample in d_dict:
            mass = d_dict[sample].get('mass', None)
            height = d_dict[sample].get('height', None)
            diameter = d_dict[sample].get('diameter', None)
            S = Sample(sample, mass=mass, height=height, diameter=diameter, mass_unit=mass_unit,
                       length_unit=length_unit)
            self.samples.update({sample: S})
            self.sample_list.append(S)
        self.sample_list = sorted(self.sample_list)

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

    def _resort_sample_list(self):
        self.sample_list = sorted(self.sample_list)