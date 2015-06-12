__author__ = 'mike'
import logging

from RockPy.Functions.general import create_logger
from RockPy.Structure.data import RockPyData


class Generic(object):
    create_logger('RockPy.series')

    def __init__(self, stype, value, unit, comment=None):
        #self.log = logging.getLogger('RockPy.series.' + type(self).__name__)
        #self.log.info('CREATING series << %s >>' % stype)
        self.stype = stype.lower()
        self.value = float(value)
        self.data = RockPyData(column_names=stype, data=value)
        self.unit = unit
        self.comment = comment

    @property
    def label(self):
        return  '%.2f [%s]' %(self.value, self.unit)

    def add_value(self, type, value, unit=None):
        self.data.append_columns(column_names=type)
        self.data[type] = value

    def __repr__(self):
        return '<RockPy.series> %s, %.2f, [%s]' %(self.stype, self.value, self.unit)

    @property
    def v(self):
        return self.value

    @property
    def u(self):
        return self.unit
