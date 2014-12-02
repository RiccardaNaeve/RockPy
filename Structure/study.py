__author__ = 'wack'


class Study(object):
    """
    comprises data of a whole study
    i.e. container for samplegroups
    """

    def __init__(self, samplegroups = None):
        """
        constructor
        :param samplegroups: one or several samplegroups that form the study
        :return:
        """
        self.sampleroups = samplegroups