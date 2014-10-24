__author__ = 'volk'
from Structure.project import Sample
from Readin.cryo_mag import CryoMag
import matplotlib.pyplot as plt

# specify data file
cryomag_file = '../test_data/NLCRY_Thellier_test.TT'

# create new Sample
sample = Sample(name='1a')

# Readin of sample data, all other samples will not get processed
CM = CryoMag(cryomag_file, sample)

# raw data of positions can be accessed like
CM.pos2
# raw data of baselines can also be accessed with
CM.baseline

# raw float data can be accessed like this
CM.float_data()
# also for the different positions
CM.float_data(mode='pos1')

# raw sting data like this
CM.str_data()

#calculating the error weighted mean of data
CM.weighted_mean()

# quick plotting of data
CM.plt_data()