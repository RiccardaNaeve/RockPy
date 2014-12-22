import base
from RockPy.Structure.data import RockPyData

import single_moment

class Nrm(single_moment.generic_moment):

    def __init__(self, sample_obj,
                 mtype, mfile, machine,
                 **options):

        super(Nrm, self).__init__(sample_obj,
                                  mtype, mfile, machine,
                                  **options)
