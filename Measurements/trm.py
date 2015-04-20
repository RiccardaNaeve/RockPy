__author__ = 'mike'
import single_moment
from RockPy.Structure.data import RockPyData


class Trm(single_moment.generic_moment):
    def __init__(self, sample_obj,
                 mtype, mfile, machine,
                 **options):

        super(Trm, self).__init__(sample_obj,
                                  mtype, mfile, machine,
                                  **options)

    def format_cryomag(self):
        super(Trm, self).format_cryomag()
        self._raw_data['data'].rename_column('step', 'temp')
