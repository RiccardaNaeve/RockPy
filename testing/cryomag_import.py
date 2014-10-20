__author__ = 'volk'
from Structure.project import Sample
from Readin.cryomag import CryoMag
# thellier output file from cryomag
import time

start = time.clock()
cryomag_file = 'test_data/NLCRY_Thellier_test.TT'

# creating a sample
sample = Sample(name='1a')

C = CryoMag(dfile=cryomag_file, sample_name=sample.name)
interm = time.clock() - start
print interm