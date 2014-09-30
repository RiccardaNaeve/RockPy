__author__ = 'volk'
import logging


class Machine(object):
    def __init__(self, dfile, sample_obj):
        self.log = logging.getLogger('RockPy.READIN.' + type(self).__name__)
        self.sample_obj = sample_obj
        self.reader_object = open(dfile)

        # ## initialize
        self.raw_data = None
        self.data = None

    def header(self):
        header = []
        return header

    def float_list(self):
        list = ['x', 'y', 'z', 'm']
        return float

    @property
    def out(self):
        return self.data