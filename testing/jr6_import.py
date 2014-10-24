__author__ = 'mike'
from Readin import spinner

def test():
    file = 'test_data/MUCSPN_test.af'

    test = spinner.Jr6(dfile=file, sample_name='328A')
    test.get_data()

if __name__ is '__main__':
    test()