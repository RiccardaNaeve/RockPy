__author__ = 'mike'
import base
from copy import deepcopy
import numpy as np

class Rem_Prime(base.Measurement):
    _standard_parameter = {'rem_prime': {'b_min': 0, 'b_max': 90, 'component': 'mag',
                                         'interpolate': True, 'smoothing':0}}

    def __init__(self, sample_obj,
                 machine='combined', mfile=None, mtype='rem_prime',
                 af1=None, af2=None,
                 **options):
        """
        :param sample_obj:
        :param mtype:
        :param mfile:
        :param machine:
        :param mdata: when mdata is set, this will be directly used as measurement data without formatting from file
        :param options:
        :return:
        """
        self.af1 = af1
        self.af2 = af2

        data = {'af1': af1.data, 'af2': af2.data}
        super(Rem_Prime, self).__init__(sample_obj=sample_obj, mtype=mtype, mfile=mfile, machine=machine, mdata=data)


    def result_rem_prime(self, component='mag', b_min=0, b_max=90, interpolate=True, smoothing=0, recalc=False):
        parameter = {'component': component,
                     'b_min': b_min,
                     'b_max': b_max,
                     'interpolate': interpolate,
                     'smoothing': smoothing,
        }
        self.calc_result(parameter, recalc)
        return self.results['rem_prime']

    def calculate_rem_prime(self, **parameter):
        """
        :param parameter:
        """
        b_min = parameter.get('b_min', Rem_Prime._standard_parameter['rem_prime']['b_min'])
        b_max = parameter.get('b_max', Rem_Prime._standard_parameter['rem_prime']['b_max'])
        component = parameter.get('component', Rem_Prime._standard_parameter['rem_prime']['component'])
        interpolate = parameter.get('interpolate', Rem_Prime._standard_parameter['rem_prime']['interpolate'])
        smoothing = parameter.get('smoothing', Rem_Prime._standard_parameter['rem_prime']['smoothing'])

        af1 = deepcopy(self.data['af1']['data'])
        af2 = deepcopy(self.data['af2']['data'])

        # truncate to within steps
        ### AF1
        idx = [i for i, v in enumerate(af1['field'].v) if b_min <= v <= b_max]
        if len(idx) != len(af1['field'].v):
            af1 = af1.filter_idx(idx)
        ### AF2
        idx = [i for i, v in enumerate(af2['field'].v) if b_min <= v <= b_max]
        if len(idx) != len(af2['field'].v):
            af2 = af2.filter_idx(idx)

        # find same fields
        b1 = set(af1['field'].v)
        b2 = set(af2['field'].v)

        if not b1 == b2:
            equal_fields = sorted(list(b1 & b1))
            not_in_b1 = b1 - b2
            not_in_b2 = b2 - b1
            if interpolate:
                if not_in_b1:
                    af1 = af1.interpolate(new_variables=equal_fields)
                if not_in_b2:
                    af2 = af2.interpolate(new_variables=equal_fields)
            else:
                if not_in_b1:
                    idx = [i for i, v in enumerate(af1['field'].v) if v not in equal_fields]
                    af1 = af1.filter_idx(idx, invert=True)
                if not_in_b2:
                    idx = [i for i, v in enumerate(af2['field'].v) if v not in equal_fields]
                    af2 = af2.filter_idx(idx, invert=True)

        daf1 = af1.derivative(component, 'field', smoothing=smoothing)
        daf2 = af2.derivative(component, 'field', smoothing=smoothing)

        ratios = af1 / af2

        import matplotlib.pyplot as plt
        plt.plot(ratios['field'].v, ratios['x'].v)
        plt.plot(ratios['field'].v, ratios['y'].v)
        plt.plot(ratios['field'].v, ratios['z'].v)
        plt.plot(ratios['field'].v, np.mean(ratios[('x', 'y', 'z')].v, axis=1))
        plt.show()