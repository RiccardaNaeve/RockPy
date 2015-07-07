__author__ = 'wack'

'''
Tutorial to demonstrate functions and plots of directional (x,y,z) data
'''

import RockPy
from RockPy.Structure.sample import Sample
from RockPy.VisualizeV3 import Figure
from os.path import join

af_file = join(RockPy.test_data_path, 'MUCSUSH_af_test.af')

s = Sample("WURM")
afd = s.add_measurement(machine='sushibar', mtype='afdemag', mfile=af_file)


# do plotting stuff
fig = Figure()
h1 = fig.add_visual(visual='stereo', name='mystereo', plt_input=s)
#h1.remove_feature(features=['stereodir_lines'])

fig.show()
