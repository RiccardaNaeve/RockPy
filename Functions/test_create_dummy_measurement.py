from unittest import TestCase
import RockPy.Functions.general
__author__ = 'mike'


class TestCreate_dummy_measurement(TestCase):
    def test_create_dummy_measurement(self):
        RockPy.Functions.general.create_dummy_measurement(mtype='thellier', machine='cryomag')