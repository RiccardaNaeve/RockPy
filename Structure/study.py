import numpy as np
import logging

import RockPy

RockPy.Functions.general.create_logger(__name__)
log = logging.getLogger(__name__)


class Study(object):
    """
    comprises data of a whole study
    i.e. container for samplegroups
    """

    def __init__(self, name=None, samplegroups=None):
        """
        constructor
        :param samplegroups: one or several samplegroups that form the study
        :return:
        """
        self.log = log  # logging.getLogger('RockPy.' + type(self).__name__)
        self.name = name
        self._samplegroups = []
        self.add_samplegroup(samplegroups)

    def __getitem__(self, item):
        """
        study['all'] returns a sample_group with all samples of all samplegroups

        for group in study: iterates over all samplegroups, excluding 'all'

        """
        if item in self.gdict:
            return self.gdict[item]
        try:
            return self._samplegroups[item]
        except KeyError:
            raise KeyError('Study has no sampleGroup << %s >>' %item)


    @property
    def samplegroups(self):
        """
        returns all sample_groups, if more than one sample group, it will return a sample group with all combined samples, too
        :return:
        """
        if len(self._samplegroups) > 1:
            return [self.all_samplegroup] + self._samplegroups
        else:
            return self._samplegroups

    @property
    def no_all_samplegroups(self):
        return self._samplegroups

    @property
    def samples(self):
        return self.all_samplegroup.sample_list

    @property
    def gdict(self):
        out = {i.name:i for i in self.samplegroups}
        return out


    def add_samplegroup(self, samplegroup):
        """
        Adds a list of sample_groups to the existing sample_group list
        :param samplegroup:
        :return:
        """
        if not samplegroup is None:
            samplegroup = self._check_samplegroup_list(samplegroup)
            self._samplegroups.extend(samplegroup)


    def _check_samplegroup_list(self, samplegroup):
        """
        Checks if samplegroup is a list of samples, a list of sample_groups, a single sample or a single samplegroup
        and converts them to be a list of samplegroups
        :param samplegroup:
        :return:
        """

        # check for list
        if isinstance(samplegroup, list):
            # check for sample_group
            if all(isinstance(item, RockPy.Sample) for item in samplegroup):
                samplegroup = [RockPy.SampleGroup(sample_list=samplegroup)]
            if all(isinstance(item, RockPy.SampleGroup) for item in samplegroup):
                samplegroup = samplegroup
            else:
                self.log.error('MIXED lists not allowed or no Sample/SampleGroup instance found')
                return None
        if isinstance(samplegroup, RockPy.Sample):
            samplegroup = [RockPy.SampleGroup(sample_list=samplegroup)]
        if isinstance(samplegroup, RockPy.SampleGroup):
            samplegroup = [samplegroup]
        return samplegroup


    @property
    def all_samplegroup(self):
        if len(self._samplegroups) > 1:
            out = np.sum(self._samplegroups)
            out.name = 'all'
        else:
            out = self._samplegroups[0]
        return out

    def save_to_file(self, folder, name):
        pass
        # print self.samplegroups.sample_list[0]
        # pickle.dump(self.samplegroups.sample_list[0], open(folder+name+'.rpy', "wb" ))
        # print json.dumps(self.samplegroups.sample_list[0])
        # todo