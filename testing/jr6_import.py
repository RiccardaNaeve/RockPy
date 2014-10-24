__author__ = 'mike'
from Readin import spinner

file = 'test_data/MUCSPN_test.af'

test = spinner.Jr6(dfile=file, sample_name='328A')
test.get_data()