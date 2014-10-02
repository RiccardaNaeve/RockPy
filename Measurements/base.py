__author__ = 'volk'
import logging
import numpy as np
import Functions.general
import Readin.machines as machines
import Readin
from Structure.rockpydata import rockpydata

class Measurement(object):
    Functions.general.create_logger('RockPy.MEASUREMENT')
    def __init__(self, sample_obj,
                 mtype, mfile, machine,
                 **options):

        self.log = logging.getLogger('RockPy.MEASUREMENT.' + type(self).__name__)

        self.implemented = {
            'generic': {'mass': None,
                        'height': None,
                        'diameter': None,
            },
            'vftb': {'hys': machines.Vftb,
                     'backfield': machines.Vftb,
                     'thermocurve': machines.Vftb,
                     'irm': machines.Vftb,
            },
            'vsm': {'hys': machines.Vsm,
            },
            'cryomag': {'thellier': machines.cryo_nl,
            },
            'microsense': {'hys': Readin.microsense.MicroSense}
        }

        ''' initialize parameters '''
        self.raw_data = None # returned data from Readin.machines()
        self.treatment = None

        ''' initial state '''
        self.is_raw_data = None # returned data from Readin.machines()
        self.initial_state = None

        if machine in self.implemented:
            if mtype.lower() in self.implemented[machine]:
                self.log.debug('FOUND\t measurement type: << %s >>' % mtype.lower())
                self.mtype = mtype.lower()
                self.sample_obj = sample_obj
                self.mfile = mfile
                self.machine = machine.lower()

                if self.machine and self.mfile:
                    self.import_data()
                else:
                    self.log.debug('NO machine or mfile passed -> no raw_data will be generated')
            else:
                self.log.error('UNKNOWN\t measurement type: << %s >>' % mtype)
        else:
            self.log.error('UNKNOWN\t machine << %s >>' % self.machine)

        self.result_methods = [i[7:] for i in dir(self) if i.startswith('result_') if not i.endswith('generic')]  # search for implemented results methods
        self.results = rockpydata(
            column_names=self.result_methods)  # dynamic entry creation for all available result methods


    def import_data(self, rtn_raw_data=None, **options):


        self.log.info(' IMPORTING << %s , %s >> data' % (self.machine, self.mtype))

        machine = options.get('machine', self.machine)
        mtype = options.get('mtype', self.mtype)
        mfile = options.get('mfile', self.mfile)
        raw_data = self.implemented[machine][mtype](mfile, self.sample_obj.name)
        if raw_data is None:
            self.log.error('IMPORTING\t did not transfer data - CHECK sample name and data file')
            return
        else:
            if rtn_raw_data:
                self.log.info(' RETURNING raw_data for << %s , %s >> data' % (machine, mtype))
                return raw_data
            else:
                self.raw_data = raw_data


    def set_initial_state(self,
                          mtype, mfile, machine,  # standard
                          **options):

        initial_state = options.get('initial_variable', 0.0)
        self.log.info(' ADDING  initial state to measurement << %s >> data' % self.mtype)
        self.is_raw_data = self.import_data(machine=machine, mfile=mfile, mtype=mtype, rtn_raw_data=True)
        components = ['x', 'y', 'z', 'm']
        self.initial_state = np.array([self.is_raw_data[i] for i in components]).T
        self.initial_state = np.c_[initial_state, self.initial_state]
        self.__dict__.update({mtype: self.initial_state})


        # def add_treatment(self, ttype, options=None):
        # self.ttype = ttype.lower()
        #     self.log.info('ADDING\t treatment to measurement << %s >>' % self.ttype)
        #
        #     implemented = {
        #         'pressure': treatments.Pressure,
        #     }
        #
        #     if ttype.lower() in implemented:
        #         self.treatment = implemented[ttype.lower()](self.sample_obj, self, options)
        #     else:
        #         self.log.error('UNKNOWN\t treatment type << %s >> is not know or not implemented' % ttype)

        # def normalize(self, dtype, norm, value=1, **options):
        # implemented = {
        #         # 'mass': self.sample_obj.mass_kg,
        #         # 'value': value,
        #         # 'nrm': getattr(self, 'nrm', None),
        #         # 'trm': getattr(self, 'trm', None),
        #         # 'irm': getattr(self, 'irm', None),
        #         # 'arm': getattr(self, 'arm', None),
        #         # 'th': getattr(self, 'th', None),
        #         # 'pt': getattr(self, 'pt', None),
        #         # 'ptrm': getattr(self, 'ptrm', None),
        #         # 'initial_state': getattr(self, 'initial_state', None),
        #         # 'm': np.array([getattr(self, 'm', None)[0], getattr(self, 'm', None)[0], getattr(self, 'm', None)[0],
        #         #                getattr(self, 'm', None)[0]]),
        #         # 'x': getattr(self, 'x', None)[0],
        #         # 'y': getattr(self, 'y', None)[0],
        #         # 'z': getattr(self, 'z', None)[0],
        #         # 'ms': getattr(self, 'ms', None)[0],
        #     }
        #
        #     try:
        #         norm_factor = implemented[norm.lower()]
        #     except KeyError:
        #         self.log.error('NORMALIZATION type << %s >> not found' % (norm))
        #         return
        #
        #     if norm_factor is None:
        #         self.log.error('NORMALIZATION type << %s >> not found' % (norm))
        #         return
        #
        #     data = getattr(self, dtype)
        #
        #     try:
        #         self.log.info(' Normalizing datatype << %s >> by << %s [ %s ]>>' % (dtype, norm, np.array_str(norm_factor)))
        #         out = data
        #         out[:, 1:] = data[:, 1:] / norm_factor[:, 1:]
        #         return out
        #     except IndexError:
        #         self.log.info(' Normalizing datatype << %s >> by << %s [ %s ]>>' % (dtype, norm, np.array_str(norm_factor)))
        #         out = data
        #         out[:, 1:] = data[:, 1:] / norm_factor
        #         return out
        #
        #     except KeyError:
        #         self.log.error('CANT normalize by data-type << %s >>' % dtype)
        #         self.log.warning('RETURNING NON NORMALIZED data-type << %s >>' % dtype)
        #         return data