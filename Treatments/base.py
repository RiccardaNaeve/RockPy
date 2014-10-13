__author__ = 'mike'
import logging

import Functions.general
from Structure.rockpydata import RockPyData


class Generic(object):
    Functions.general.create_logger('RockPy.TREATMENT')

    def __init__(self, ttype, value, comment):
        self.log = logging.getLogger('RockPy.TREATMENT.' + type(self).__name__)
        self.log.info('CREATING treatment << %s >>' % ttype)
        self.ttype = ttype
        self.data = RockPyData(column_names=ttype, data=value)
        self.comment = comment

    def add_value(self, type, value, unit=None):
        self.data.append_columns(column_names=type)
        self.data[type] = value