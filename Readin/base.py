__author__ = 'volk'
import logging


class Machine(object):
    log = logging.getLogger('RockPy.READIN')

    def __init__(self, dfile, sample_name):
        Machine.log.info('IMPORTING << %s , %s >> file: << %s >>' % (sample_name, type(self).__name__, dfile))
        self.sample_name = sample_name
        self.file_name = dfile

        # ## initialize
        self.raw_data = None
        self.data = None

    # def __getstate__(self):
    #     pass
    #
    # def __setstate__(self, state):
    #     pass

    @property
    def file_header(self):
        header = []
        return header

    @property
    def float_list(self):
        list = ['x', 'y', 'z', 'm']
        return float

    @property
    def has_data(self):
        if self._check_data_exists():
            return True
        else:
            return False

    def _check_data_exists(self):
        """
        Needed as a check for data import in Sample.add_measurement. if it returns False, the measurement will not be created.


        :return: bool
        """
        if self.data:
            return True
        else:
            return False
