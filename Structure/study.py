import numpy as np
import logging

import RockPy
from copy import deepcopy
RockPy.Functions.general.create_logger(__name__)
log = logging.getLogger(__name__)


class Study(object):
    """
    comprises data of a whole study
    i.e. container for samplegroups
    """

    def __init__(self, samplegroups=None, name=None):
        """
        constructor
        :param samplegroups: one or several samplegroups that form the study
        :return:
        """
        #self.log = log  # logging.getLogger('RockPy.' + type(self).__name__)
        self.name = name
        self._samplegroups = []
        self._all_samplegroup = None

        self.add_samplegroup(samplegroups)

    def __getitem__(self, item):
        """
        study['all'] returns a sample_group with all samples of all samplegroups

        for group in study: iterates over all samplegroups, excluding 'all'

        """
        if item in self.gdict:
            return self.gdict[item]
        try:
            return self.samplegroups[item]
        except KeyError:
            raise KeyError('Study has no SampleGroup << %s >>' %item)


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
    def samplegroup_names(self):
        out = [i.name for i in self.no_all_samplegroups]
        return out

    @property
    def no_all_samplegroups(self):
        return self._samplegroups

    @property
    def samples(self):
        out = []
        for sg in self._samplegroups:
            out.extend(sg.slist)
        return out

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
        if samplegroup is not None:
            samplegroup = self._check_samplegroup_list(samplegroup)
            self._samplegroups.extend(samplegroup)
            self.all_group()
            return samplegroup

    def get_samples(self, snames=None, mtypes=None, ttypes=None, tvals=None, tval_range=None):
        """
        Primary search function for all parameters
        """
        out = self._all_samplegroup.get_samples(snames = snames, mtypes=mtypes, ttypes=ttypes, tvals=tvals, tval_range=tval_range)
        return out

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
                log.error('MIXED lists not allowed or no Sample/SampleGroup instance found')
                return None
        if isinstance(samplegroup, RockPy.Sample):
            samplegroup = [RockPy.SampleGroup(sample_list=samplegroup)]
        if isinstance(samplegroup, RockPy.SampleGroup):
            samplegroup = [samplegroup]
        return samplegroup

    def __add__(self, other):
        self._samplegroups.extend(other._samplegroups)
        return self

    def all_group(self):
        out = RockPy.SampleGroup(name='all')
        for i in self._samplegroups:
            out.add_samples(i.slist)
        self._all_samplegroup = out
        return out

    @property
    def all_samplegroup(self):
        # if not hasattr(self, '_all_samplegroup'):
        self.all_group()
        out = self._all_samplegroup
        return out

    @property
    def mtypes(self):
        """
        looks through all samplegroups and return measurement types
        """
        return sorted(list(set([i for j in self.samplegroups for i in j.mtypes])))

    def info(self):
        from prettytable import PrettyTable
        for sg in self._samplegroups:
            print sg
            print ''.join(['-' for i in range(20)])
            out = PrettyTable(['Sample Name', 'Measurements', 'Treatments', 'Initial State'])
            out.align['Measurements']='l'
            out.align[ 'Treatments']='l'
            out.align[ 'Initial State']='l'
            for s in sg:
                measurements = '|'.join([m.mtype for m in s.filtered_data if m.mtype not in ['mass', 'diameter', 'height']])
                ttypes = '|'.join([ ' '.join([t.ttype, str(t.value), t.unit])  for m in s.filtered_data for t in m.treatments
                            if m.mtype not in ['mass', 'diameter', 'height']])
                initial = '|'.join([m.initial_state.mtype if m.initial_state is not None else '-' for m in s.filtered_data
                                    if m.mtype not in ['mass', 'diameter', 'height']])
                out.add_row([s.name, measurements, ttypes, initial])
            print out