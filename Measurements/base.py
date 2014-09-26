__author__ = 'volk'
import logging
import numpy as np
import Functions.general
import Readin.machines as machines


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
            }
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


# class Measurement_old(object):
# def __init__(self, sample_obj, mtype, mfile, machine, log=None, **options):
#
#         if not log:
#             self.log = logging.getLogger('RockPy.MEASUREMENT')
#         else:
#             self.log = logging.getLogger(log)
#
#         implemented = ['af-demag', 'af', 'parm-spectra',
#                        'hys', 'irm', 'coe', 'rmp',
#                        'forc',
#                        'palint', 'thellier', 'pseudo-thellier',
#                        'zfc', 'fc',
#                        'visc',
#         ]
#         self.normalization = {}
#
#         self.raw_data = None
#
#         ''' initial state '''
#         self.is_raw_data = None
#         self.initial_state = None
#
#         if mtype.lower() in implemented:
#             self.log.debug('FOUND\t measurement type: << %s >>' % mtype.lower())
#             self.mtype = mtype.lower()
#             self.sample_obj = sample_obj
#             self.mfile = mfile
#
#             if machine:
#                 self.machine = machine.lower()
#             else:
#                 self.machine = None
#
#             if self.machine and self.mfile:
#                 self.import_data()
#             else:
#                 self.log.warning('NO machine or mfile passed -> no raw_data will be generated')
#         else:
#             self.log.error('UNKNOWN\t measurement type: << %s >>' % mtype)
#             return None
#
#         self.treatment = None
#
#     def import_data(self, rtn_raw_data=None, **options):
#         implemented = {'sushibar': {'af-demag': machines.sushibar,
#                                     'af': machines.sushibar,
#                                     'parm-spectra': machines.sushibar,
#                                     'nrm': machines.sushibar,  # externally applied magnetization
#                                     'trm': machines.sushibar,  # externally applied magnetization
#                                     'irm': machines.sushibar,  # externally applied magnetization
#                                     'arm': machines.sushibar,  # externally applied magnetization
#         },
#                        'vsm': {'hys': machines.vsm,
#                                'irm': machines.vsm,
#                                'coe': machines.vsm,
#                                'visc': machines.vsm,
#                                'forc': machines.vsm_forc},
#                        'cryo_nl': {'palint': machines.cryo_nl2},
#                        'mpms': {'zfc': machines.mpms,
#                                 'fc': machines.mpms, },
#                        'simulation': {'palint': machines.simulation,
#                        },
#                        'vftb': {'hys': machines.vftb,
#                                 'coe': machines.vftb,
#                                 'rmp': machines.vftb}}
#
#         self.log.info(' IMPORTING << %s , %s >> data' % (self.machine, self.mtype))
#
#         machine = options.get('machine', self.machine)
#         mtype = options.get('mtype', self.mtype)
#         mfile = options.get('mfile', self.mfile)
#
#         if machine in implemented:
#             if mtype in implemented[machine]:
#                 raw_data = implemented[machine][mtype](mfile, self.sample_obj.name)
#                 if raw_data is None:
#                     self.log.error('IMPORTING\t did not transfer data - CHECK sample name and data file')
#                     return
#                 else:
#                     if rtn_raw_data:
#                         self.log.info(' RETURNING raw_data for << %s , %s >> data' % (machine, mtype))
#                         return raw_data
#                     else:
#                         self.raw_data = raw_data
#             else:
#                 self.log.error('IMPORTING UNKNOWN\t measurement type << %s >>' % self.mtype)
#         else:
#             self.log.error('UNKNOWN\t machine << %s >>' % self.machine)
#
#
#     def add_initial_state(self,  # todo change to set
#                           mtype, mfile, machine,  # standard
#                           **options):
#         initial_state = options.get('initial_variable', 0.0)
#         self.log.info(' ADDING  initial state to measurement << %s >> data' % self.mtype)
#         self.is_raw_data = self.import_data(machine=machine, mfile=mfile, mtype=mtype, rtn_raw_data=True)
#         components = ['x', 'y', 'z', 'm']
#         self.initial_state = np.array([self.is_raw_data[i] for i in components]).T
#         self.initial_state = np.c_[initial_state, self.initial_state]
#         self.__dict__.update({mtype: self.initial_state})
#
#
#     def add_treatment(self, ttype, options=None):
#         self.ttype = ttype.lower()
#         self.log.info('ADDING\t treatment to measurement << %s >>' % self.ttype)
#
#         implemented = {
#             'pressure': treatments.Pressure,
#         }
#
#         if ttype.lower() in implemented:
#             self.treatment = implemented[ttype.lower()](self.sample_obj, self, options)
#         else:
#             self.log.error('UNKNOWN\t treatment type << %s >> is not know or not implemented' % ttype)
#
#
#     def interpolate(self, what, x_new=None, derivative=0):
#         """
#         from scipy.interpolate.splev(x, tck, der=0, ext=0):
#            Evaluate a B-spline or its derivatives.
#
#            Given the knots and coefficients of a B-spline representation, evaluate the value of the smoothing polynomial
#            and its derivatives. This is a wrapper around the FORTRAN routines splev and splder of FITPACK.
#
#         :param what:
#         :param x_new:
#         :param derivative : int
#                           The order of derivative of the spline to compute (must be less than or equal to k).
#         :return:
#         """
#         self.log.info('INTERPOLATIN << %s >> using splev (Scipy)' % what)
#         xy = np.sort(getattr(self, what), axis=0)
#         mtype = getattr(self, 'mtype')
#
#         if mtype == 'coe':
#             xy = np.array([[-i[0], i[1]] for i in xy])
#             xy = xy[::-1]
#         x = xy[:, 0]
#         y = xy[:, 1]
#
#         if x_new is None:
#             x_new = np.linspace(min(x), max(x), 5000)
#
#         fc = splrep(x, y, s=0)
#         y_new = interpolate.splev(x_new, fc, der=derivative)
#
#         out = np.array([[x_new[i], y_new[i]] for i in range(len(x_new))])
#
#         if mtype == 'coe':
#             out = np.array([[-i[0], i[1]] for i in out])
#         self.log.debug('INTERPOLATION READY')
#         if derivative > 0:
#             self.log.info('RETURNING derivative << %i >>' % derivative)
#         return out
#
#     def calculate_derivative(self, what, interpolate_first=False, **options):
#         """
#         Calculates the derivative of a certain attribute of the class
#
#         :param what : str
#                     attribute name
#         :param interpolate_first : bool
#                                  wether the data is to be interpolated and the derivative of this is returned
#         :param options : dict
#                        options
#         :return: ndarray
#         """
#         diff = options.get('diff', 1)
#         smoothing = options.get('smoothing', 1)
#         norm = options.get('norm', True)
#
#         if interpolate_first:
#             out = self.interpolate(what=what, derivative=diff)
#         else:
#             data = getattr(self, what, None)
#             out = Functions.general.differentiate(data, diff=diff, smoothing=smoothing, norm=norm)
#         return out
#
#     def normalize(self, dtype, norm, value=1, **options):
#         implemented = {
#             'mass': self.sample_obj.mass_kg,
#             'value': value,
#             'nrm': getattr(self, 'nrm', None),
#             'trm': getattr(self, 'trm', None),
#             'irm': getattr(self, 'irm', None),
#             'arm': getattr(self, 'arm', None),
#             'th': getattr(self, 'th', None),
#             'pt': getattr(self, 'pt', None),
#             'ptrm': getattr(self, 'ptrm', None),
#             'initial_state': getattr(self, 'initial_state', None),
#             'm': np.array([getattr(self, 'm', None)[0], getattr(self, 'm', None)[0], getattr(self, 'm', None)[0],
#                            getattr(self, 'm', None)[0]]),
#             'x': getattr(self, 'x', None)[0],
#             'y': getattr(self, 'y', None)[0],
#             'z': getattr(self, 'z', None)[0],
#             'ms': getattr(self, 'ms', None)[0],
#         }
#
#         try:
#             norm_factor = implemented[norm.lower()]
#         except KeyError:
#             self.log.error('NORMALIZATION type << %s >> not found' % (norm))
#             return
#
#         if norm_factor is None:
#             self.log.error('NORMALIZATION type << %s >> not found' % (norm))
#             return
#
#         data = getattr(self, dtype)
#
#         try:
#             self.log.info(' Normalizing datatype << %s >> by << %s [ %s ]>>' % (dtype, norm, np.array_str(norm_factor)))
#             out = data
#             out[:, 1:] = data[:, 1:] / norm_factor[:, 1:]
#             return out
#         except IndexError:
#             self.log.info(' Normalizing datatype << %s >> by << %s [ %s ]>>' % (dtype, norm, np.array_str(norm_factor)))
#             out = data
#             out[:, 1:] = data[:, 1:] / norm_factor
#             return out
#
#         except KeyError:
#             self.log.error('CANT normalize by data-type << %s >>' % dtype)
#             self.log.warning('RETURNING NON NORMALIZED data-type << %s >>' % dtype)
#             return data
