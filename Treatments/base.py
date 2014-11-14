__author__ = 'mike'
import logging

from RockPy.Functions.general import create_logger
from RockPy.Structure.data import RockPyData


class Generic(object):
    create_logger('RockPy.TREATMENT')

    def __init__(self, ttype, value, unit, comment=None):
        self.log = logging.getLogger('RockPy.TREATMENT.' + type(self).__name__)
        self.log.info('CREATING treatment << %s >>' % ttype)
        self.ttype = ttype.lower()
        self.data = RockPyData(column_names=ttype, data=value, units = unit)
        self.comment = comment

    def add_value(self, type, value, unit=None):
        self.data.append_columns(column_names=type)
        self.data[type] = value

    def __repr__(self):
        return '<RockPy.Treatments> %s, %.2f, [%s]' %(self.ttype, self.data[self.ttype].v, self.data[self.ttype].u)