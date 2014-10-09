__author__ = 'mike'
import base


class Generic(base.Machine):
    def __init__(self):
        super(Generic, self).__init__(dfile=None, sample_obj=None)

    def out_Mass(self):
        pass

    def out_Length(self):
        pass