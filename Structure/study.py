__author__ = 'wack'
import pickle
import json

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
        self.samplegroups = samplegroups

    def save_to_file(self, folder, name):
        print self.samplegroups.sample_list[0]
        # pickle.dump(self.samplegroups.sample_list[0], open(folder+name+'.rpy', "wb" ))
        print json.dumps(self.samplegroups.sample_list[0])
        #todo