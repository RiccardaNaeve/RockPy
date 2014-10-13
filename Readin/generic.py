__author__ = 'mike'
import base


class Generic(base.Machine):
    def __init__(self):
        super(Generic, self).__init__(dfile=None, sample_obj=None)
        self.generate = True

    def out_mass(self):
        pass

    def out_length(self):
        pass