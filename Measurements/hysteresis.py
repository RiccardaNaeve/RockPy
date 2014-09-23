__author__ = 'volk'
import base
import numpy as np
import Structure.data


class hysteresis(base.measurement):
    def __init__(self, sample_obj,
                 mtype, mfile, machine,
                 **options):
        super(hysteresis, self).__init__(sample_obj, mtype, mfile, machine)

        data_formatting = {'vftb': self.format_vftb}

        # ## initialize
        self.virgin = None
        self.msi = None
        self.up_field = None
        self.down_field = None

        data_formatting[self.machine]()

    def format_vftb(self):
        dfield = np.diff(self.raw_data['field'])

        idx = [i for i in range(len(dfield)) if dfield[i] < 0]
        virgin_idx = range(0, idx[0])
        down_field_idx = idx
        up_field_idx = range(idx[-1], len(dfield))

        field = self.raw_data['field']
        moment = self.raw_data['moment']
        std_dev = self.raw_data['std_dev']

        self.virgin = Structure.data.data(variable=[field[i] for i in virgin_idx], var_unit='Oe',
                                          measurement=[moment[i] for i in virgin_idx], measure_unit='emu',
                                          std_dev=[std_dev[i] for i in virgin_idx])
        self.down_field = Structure.data.data(variable=[field[i] for i in down_field_idx], var_unit='Oe',
                                              measurement=[moment[i] for i in down_field_idx], measure_unit='emu',
                                              std_dev=[std_dev[i] for i in down_field_idx])
        self.up_field = Structure.data.data(variable=[field[i] for i in up_field_idx], var_unit='Oe',
                                            measurement=[moment[i] for i in up_field_idx], measure_unit='emu',
                                            std_dev=[std_dev[i] for i in up_field_idx])

    def format_vsm(self):
        pass