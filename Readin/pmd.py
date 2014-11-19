__author__ = 'wack'

import base


class PMD(base.Machine):
    def __init__(self):
        super(PMD, self).__init__(dfile=None, sample_name=None)
        self.generate = True