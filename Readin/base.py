__author__ = 'volk'
import logging


class Machine(object):
    def __init__(self, dfile, sample_name):
        self.log = logging.getLogger('RockPy.READIN.' + type(self).__name__)
        self.log.info('IMPORTING << %s , %s >> file: << %s >>' % (sample_name, type(self).__name__, dfile))

        self.sample_obj = sample_name
        self.reader_object = open(dfile)

        # ## initialize
        self.raw_data = None
        self.data = None


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
        if self.data:
            return True
        else:
            return False
