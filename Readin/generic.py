__author__ = 'mike'
import base


class Generic(base.Machine):
    def __init__(self):
        super(Generic, self).__init__(dfile=None, sample_name=None)
        self.generate = True

class Synthetic(base.Machine):
    pass