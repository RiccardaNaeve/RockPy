__author__ = 'volk'
import matplotlib.pyplot as plt
import numpy as np

import base
from RockPy.Structure.data import RockPyData


class ThermoCurve(base.Measurement):
    def __init__(self, sample_obj,
                 mtype, mfile, machine,
                 **options):
        self._data = {'up_temp': None,
                      'down_temp': None}

        super(ThermoCurve, self).__init__(sample_obj, mtype, mfile, machine)


    def format_vftb(self):
        data = self.machine_data.out_thermocurve()
        header = self.machine_data.header
        if len(data) > 2:
            print('LENGTH of machine.out_thermocurve =! 2. Assuming data[0] = heating data[1] = cooling')
            # self.log.warning('LENGTH of machine.out_thermocurve =! 2. Assuming data[0] = heating data[1] = cooling')
        if len(data) > 1:
            self._raw_data ['up_temp'] = RockPyData(column_names=header, data=data[0])
            self._raw_data ['down_temp'] = RockPyData(column_names=header, data=data[1])
        else:
            print('LENGTH of machine.out_thermocurve < 2.')
            # self.log.error('LENGTH of machine.out_thermocurve < 2.')

    def format_vsm(self):
        data = self.machine_data.out
        header = self.machine_data.header
        segments = self.machine_data.segment_info
        aux = np.array([j for i in data for j in i])  # combine all data arrays
        a = np.array([(i, v) for i, v in enumerate(np.diff(aux, axis=0)[:, 0])])

        sign = np.sign(np.diff(aux, axis=0)[:, 1])

        threshold = 3
        zero_crossings = [i+1 for i in xrange(len(a[:, 1]) - 1)
                if a[i, 1] > 0 > a[i + 1, 1] and a[i, 1] > 0 > a[i + 2, 1]
                or a[i, 1] < 0 < a[i + 1, 1] and a[i, 1] < 0 < a[i + 2, 1]]
        zero_crossings = [0] + zero_crossings  # start with zero index
        zero_crossings += [len(aux)] # append last index

        ut = 0  # running number warming
        dt = 0  # running number cooling

        for i, v in enumerate(zero_crossings):
            if v < zero_crossings[-1]:  # prevents index Error
                if sum(a[v:zero_crossings[i + 1], 1]) < 0:  # cooling
                    name = 'cool%02i' % (ut)
                    ut += 1
                else:
                    name = 'warm%02i' % (dt)
                    dt += 1
                data = aux[v:zero_crossings[i + 1] + 1]
                rpd = RockPyData(column_names=header, data=data)
                rpd.rename_column('temperature', 'temp')
                rpd.rename_column('moment', 'mag')
                self._data.update({name: rpd})

    def delete_segment(self, segment):
        self._data.pop(segment)

    @property
    def ut(self):
        """
        returns a RPdata with all warming data
        """
        out = None
        for i in self._data:
            if 'warm' in i:
                if not out:
                    out = self._data[i]
                else:
                    out = out.append_rows(self._data[i])
        return out

    @property
    def dt(self):
        """
        returns a RPdata with all cooling data
        """
        out = None
        for i in self._data:
            if 'cool' in i:
                if not out:
                    out = self._data[i]
                else:
                    out = out.append_rows(self._data[i])
        return out

    def plt_thermocurve(self):
        import RockPy.Visualize.demag

        plot = RockPy.Visualize.demag.ThermoCurve(self)
        plot.show()