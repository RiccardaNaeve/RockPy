__author__ = 'volk'
from os.path import join
import RockPy
from copy import deepcopy
# thellier output file from cryomag

def test():
    cryomag_file = join(RockPy.test_data_path, 'NLCRY_Thellier_test.TT')

    # creating a sample
    sample = RockPy.Sample(name='1a')

    # adding the measurement to the sample
    M = sample.add_measurement(mtype='thellier', mfile=cryomag_file, machine='cryomag',
                               treatments='Pressure_0.0_GPa')

    print(M._data['nrm']._column_names)
#    for i, v in M._data['nrm'].__dict__.iteritems():
#        print i, v
#        print type( v)
#        RockPy.save(v, 'TTtest.rpy', RockPy.test_data_path)
#        sample = RockPy.load('TTtest.rpy', RockPy.test_data_path)

    a = M._data['nrm']._row_names
    b = deepcopy( M._data['nrm']._column_names)


    print a
    print b

    c = b[1]
    #c = list( b[1])
    print type( c)
    c = 'x'
    print type( c)

    RockPy.save(c, 'TTtest.rpy', RockPy.test_data_path)
    sample = RockPy.load('TTtest.rpy', RockPy.test_data_path)


if __name__ == '__main__':
    test()