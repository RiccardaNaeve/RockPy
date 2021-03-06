__author__ = 'volk'
import logging
import gc

class Machine(object):
    log = logging.getLogger('RockPy.READIN')
    def split_tab(self, line):
        return line.split('\t')

    def __init__(self, dfile, sample_name):
        Machine.log.info('IMPORTING << %s , %s >> file: << %s >>' % (sample_name, type(self).__name__, dfile))
        self.sample_name = sample_name
        self.file_name = dfile

        # ## initialize
        self.raw_data = None
        self.data = None

    def simple_import(self):
        """
        simple wrapper that opens file and uses file.readlines to import and removes newline marks
        :return:
        """
        with open(self.file_name) as f:
            out = f.readlines()

        out = map(str.rstrip, out)
        gc.collect()
        return out

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
        if self.data is not None:
            return True
        else:
            return False
