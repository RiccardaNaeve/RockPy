__author__ = 'volk'
import logging
import numpy as np
import Functions.general
import Readin.machines as machines
import Readin
from Structure.rockpydata import rockpydata
import inspect

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

        # data formatting
        if callable(getattr(self, 'format_' + machine)):
            self.log.debug('FORMATTING raw data from << %s >>' % self.machine)
            getattr(self, 'format_' + machine)()
        else:
            self.log.error(
                'FORMATTING raw data from << %s >> not possible, probably not implemented, yet.' % self.machine)

        self.result_methods = [i[7:] for i in dir(self) if i.startswith('result_') if not i.endswith('generic')]  # search for implemented results methods
        self.results = rockpydata(
            column_names=self.result_methods)  # dynamic entry creation for all available result methods
        self.calculation_parameters = {i[10:]: None for i in dir(self) if i.startswith('calculate_') if
                                       not i.endswith('generic')}
        self.standard_parameters = {i[10:]: None for i in dir(self) if i.startswith('calculate_') if
                                    not i.endswith('generic')}

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

    @property
    def generic(self):
        '''
        helper function that returns the value for a given statistical method. If result not available will calculate
        it with standard parameters
        '''
        return self.result_generic()


    def result_generic(self, **parameter):
        '''
        Generic for for result implementation. Every calculation of result should be in the self.results data structure
        before calculation.
        It should then be tested if a value for it exists, and if not it should be created by calling
        _calculate_result_(result_name).

        '''
        # NAMING! no '_' allowed after result
        if self.results['generic'] is None:
            self.calculate_generic(**parameter)
        return self.results['generic']


    def calculate_generic(self, **parameter):
        '''
        actual calculation of the result

        :return:
        '''

        self.results['generic'] = 0

    def calc_generic(self, **parameter):
        '''
        helper function
        actual calculation of the result

        :return:
        '''

        self.results['generic'] = 0

    def calc_result(self, parameter, recalc, force_caller=None):
        '''
        Helper function:
        Calls any calculate_* function, but checks first:
            1. does this calculation method exist
            2. has it been calculated before
               |- NO : calculate the result
               |- YES: are given parameters equal to previous calculation parameters
                  |- NO : calculate result with new parameters
                  |- YES: return previous result
        :param parameter: dict
                        dictionary with parameters needed for calculation
        :param caller: calling function name without calculate_
        :param force_caller: not dynamically retrieved caller name.
        :return:
        '''

        if force_caller is not None:
            caller = force_caller
        else:
            caller = '_'.join(inspect.stack()[1][3].split('_')[1:])

        if callable(getattr(self, 'calculate_' + caller)):  # check if calculation function exists
            parameter = self.compare_parameters(caller, parameter)  # checks for None and replaces it with standard
            if self.results[caller] is None or self.results[
                caller] == 0.000 or recalc:  # if results dont exist or force recalc
                self.log.debug('CANNOT find result << %s >> -> calculating' % (caller))
                getattr(self, 'calculate_' + caller)(**parameter)  # calling calculation method
            else:
                self.log.debug('FOUND previous << %s >> parameters' % (caller))
                if self.check_parameters(caller, parameter):  # are parameters equal to previous parameters
                    self.log.debug('RESULT parameters different from previous calculation -> recalculating')
                    getattr(self, 'calculate_' + caller)(**parameter)  # recalculating if parameters different
                else:
                    self.log.debug('RESULT parameters equal to previous calculation')
        else:
            self.log.error(
                'CALCULATION of << %s >> not possible, probably not implemented, yet.' % caller)

    def compare_parameters(self, caller, parameter):
        '''
        checks if given parameter[key] is None and replaces it with standard parameter

        :param caller: str
                     name of calling function ('result_generic' should be given as 'result')
        :param parameter:
        :return:
        '''

        # caller = inspect.stack()[1][3].split('_')[-1]

        for i, v in parameter.iteritems():
            if v is None:
                if self.calculation_parameters[caller]:
                    parameter[i] = self.calculation_parameters[caller][i]
                else:
                    parameter[i] = self.standard_parameters[caller][i]
        return parameter

    def check_parameters(self, caller, parameter):
        '''
        Checks if previous calculation used the same parameters, if yes returns the previous calculation
        if no calculates with new parameters
        :param caller: str
                     name of calling function ('result_generic' should be given as 'result')
        :param parameter:
        :return:
        '''

        if self.calculation_parameters[caller]:
            a = [parameter[i] for i in self.calculation_parameters[caller]]
            b = [self.calculation_parameters[caller][i] for i in self.calculation_parameters[caller]]
            if a != b:
                return True
            else:
                return False
        else:
            return True