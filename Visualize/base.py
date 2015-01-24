__author__ = 'volk'import loggingimport osimport sysimport inspectimport copyimport numpy as npimport matplotlib.pyplot as pltfrom matplotlib.lines import Line2Dfrom matplotlib import gridspecfrom matplotlib.backends.backend_pdf import PdfPagesimport RockPyimport RockPy.Functionsimport RockPy.Measurements.basefrom RockPy.Functions.general import _to_listfrom copy import deepcopyimport Features.genericfrom pprint import pprintclass Generic(object):    """    You can either give a sample, a samplegroup or a whole study into a plot.    The standard behaviour of a plot is as follows:    Definitions:    ============        Visual:  upper most level        Plot:  a visual can contain one or more figures, e.g. hysteresis + thermocurve.                 These are plotted in different windows/pages in a pdf        Subplot: Contained in a Figure. A Figure can have more than one subplot BUT ALWAYS HAS ONE.                 Subplots are independent of eachother.        dataseries:    a Subplot contains one or more dataseries. e.g.:                    - the evolution of two parameters with a variable                    - a hysteresis with included backfield plot                    - measurements of different samples    Study    =====    assuming you pass a study into a plot:        This will plot a mean for each sample_group        e.g. useful for lots of groups        colors = Sample_groups        lines = treatments    Sample_Group    ============    passing a sample_group into a plot:       This will plot all samples in sample_group and the average    Sample    ======    passing a sample in to a plot:       This will plot the sample and all the measurements       open question:       - do we need a average measurement function or is this done through sample groups    OPEN QUESTIONS    ==============    """    logger = logging.getLogger('RockPy.VISUALIZE')    _required = []    @classmethod    def inheritors(cls):        subclasses = set()        work = [cls]        while work:            parent = work.pop()            for child in parent.__subclasses__():                if child not in subclasses:                    subclasses.add(child)                    work.append(child)        return subclasses    def __init__(self, plot_samples=None,                 reference=None, rtype='mag', vval=None, norm_method='max',                 fig_opt=dict(),                 cfilter=dict(),  # filtering conditions                 **options):        # Generic.logger = logging.getLogger('RockPy.VISUALIZE.' + type(self).__name__)        self.tex = options.pop('tex', False)        self.options = options        # # normalization_parameters for normalization of measurement        self.name = type(self).__name__.lower()        self.existing_visuals = {i.__name__: i for i in Generic.inheritors()}        self._required = type(            self)._required  # required measurements in a figure needs to be stored in instance for multiple plots generation        self.input = plot_samples        self.input_type = type(plot_samples)        self._hierarchy = self.input_type        self.study = self._to_study(plot_samples)        self.norm = dict(reference=reference, rtype=rtype, vval=vval, norm_method=norm_method)        # self.color_source = options.pop('color_source', self.get_source[self.input_type])        # self.marker_source = options.pop('marker_source', self.get_source[self.input_type])        # self.ls_source = options.pop('linestyle_source', 'treatment')        self._visuals = {}  # visual contains ... plots        self._figs = []        self._fig_opt = fig_opt        self.standard_features = []  # standard features added to figure        self.single_features = []  # standard features added to figure, only plotted once        self.features = {i[0][8:]: i[1] for i in inspect.getmembers(self, predicate=inspect.ismethod) if                         i[0].startswith('feature_')}        self.line_dict = {}        self.text_dict = {}        self.initialize_visual()        self.set_labels()        self.plotted_primary = []        self.plotted_secondary = []        self.plotting(samples=self.get_plot_samples())        if 'show' in options:            self.show()    ''' NEEDED BY ALL VISULIZATIONS '''    def initialize_visual(self):  #        # MANDATORY        """        :return:        """        pass    def plotting(self, samples, **plt_opt):        # pprint(self.__dict__)        primary = samples[0]        secondary = samples[1]        splt_opt = deepcopy(plt_opt)        """ PRIMARY """        for feature in self.standard_features:            for s in primary:                # look for measurements                for visual, mtype in self.required.iteritems():                    measurements = s.get_measurements(mtype=mtype)                    for m in measurements:                        feature(m_obj=m, **plt_opt)                        self.plotted_primary.append(m)            for s in secondary:                # look for measurements                splt_opt.update({'alpha': 0.5, 'linestyle':':'})                for visual, mtype in self.required.iteritems():                    measurements = s.get_measurements(mtype=mtype)                    for m in measurements:                        feature(m_obj=m, **splt_opt)                        self.plotted_secondary.append(m)        for feature in self.single_features:            feature()        pprint(self.line_dict)    ''' END OF MANDATORY '''    # ## plotting style related    @property    def get_source(self):        out = {RockPy.Study: 'samplegroup',               RockPy.SampleGroup: 'sample',               RockPy.Sample: 'measurement',               RockPy.Measurements.base.Measurement: 'measurement'        }        return out    ''' PLOTTING REQUIREMENTS '''    @property    def required(self):        if isinstance(type(self)._required, dict):            return type(self)._required        else:            return {self.name: type(self)._required}    @property    def require_list(self):        return [j for i in self.required for j in self.required[i]]    def get_samples_meet_requirements(self, sg):        out = [sample for sample in sg.sample_list if sample.meets_requirements(self.require_list)]        return out    ''' FIGURE REALTED '''    @property    def visuals(self):        if self._visuals:            return self._visuals        else:            return {self.name.lower(): self}    @property    def figs(self):        out = {name: visual._figs for name, visual in self.visuals.iteritems()}        return out    @property    def subplots(self):        pass    def add_plot(self, name=None, plot=None, **plot_opt):        if not plot:            plot, gs = self._create_fig(**plot_opt)            if not name:                name = type(self).__name__.lower()                if name in self._visuals:                    name += '%02i' % len(self.visuals.keys())            self.gs = gs            self._figs.append(plot)            self._visuals.update({name: self})        else:            self._visuals.update({plot.name: plot})            self._required.update(plot.required)    def add_subplot(self, name=None):        if name is None:            name = self.name        self.gs = gridspec.GridSpec(1, 2)        for ax in self.figs[name][0].as_list():            ax.set_position(self.gs[0])        self.figs[name][0].add_subplot(self.gs[1])    def _create_fig(self, **fig_opt):        fig = plt.figure(**fig_opt)        gs = gridspec.GridSpec(1, 1)        ax1 = fig.add_subplot(gs[0])        return fig, gs    ''' SAMPLE RELATED '''    def _to_study(self, slist):        """        converts list of measurements/samples/sample_groups -> study        if list of sample_groups -> self.input_type = RockPy.Study        if list of samples -> self.input_type = RockPy.Sample_Group        if list of measurements -> self.input_type = RockPy.Sample        if single measurement -> self.input_type = RockPy.Measurements.base.Measurement        """        if not slist:            return None        out = None        if not isinstance(slist, list):  # check if list            if isinstance(slist, RockPy.Study):  # if study keep study                out = slist            if not isinstance(slist, RockPy.Study):                if isinstance(slist, RockPy.SampleGroup) or isinstance(slist, RockPy.Sample):                    Generic.logger.debug('CONVERTING %s -> RockPy.Study(%s)' % (type(slist), type(slist)))                    out = RockPy.Study(slist)                if type(slist) in RockPy.Measurements.base.Measurement.inheritors():                    Generic.logger.debug(                        'CONVERTING %s -> RockPy.Sample -> RockPy.Study(Sample(%s))' % (type(slist), type(slist)))                    s = RockPy.Sample(name=self.name)                    s.measurements.append(slist)                    self.input_type = RockPy.Measurements.base.Measurement                    out = RockPy.Study(s)        if isinstance(slist, list):            if all(isinstance(item, RockPy.SampleGroup) for item in slist):                Generic.logger.debug('CONVERTING %s(%s) -> RockPy.Study(%s(%s))' % (                    type(slist), type(slist[0]), type(slist), type(slist[0])))                # self.input_type = RockPy.Study                out = RockPy.Study(slist)            if all(isinstance(item, RockPy.Sample) for item in slist):                Generic.logger.debug('CONVERTING %s(%s) -> RockPy.Study(%s(%s))' % (                    type(slist), type(slist[0]), type(slist), type(slist[0])))                # self.input_type = RockPy.SampleGroup                out = RockPy.Study(slist)            if all(type(item) in RockPy.Measurements.base.Measurement.inheritors() for item in slist):                Generic.logger.debug(                    'CONVERTING %s -> RockPy.Sample -> RockPy.Study(Sample(%s))' % (type(slist), type(slist)))                # self.input_type = RockPy.Sample                s = RockPy.Sample(name=self.name)                s.measurements = slist                out = RockPy.Study(s)        return out    def _to_sample_list(self, slist):        out = None        if isinstance(slist, RockPy.Study):            out = slist.samples        if isinstance(slist, RockPy.SampleGroup):            out = slist.sample_list        if isinstance(slist, RockPy.Sample):            out = [slist]        if isinstance(slist, list):            if all(isinstance(item, RockPy.SampleGroup) for item in slist):                out = sum(slist).sample_list            if all(isinstance(item, RockPy.Sample) for item in slist):                out = slist        return out    def plot_measurements(self):        pass    def make_plots(self):        for i in self.visuals:            self.visuals[i].plotting('test')    def show(self):        # for label, figs in self.figs.iteritems():        # for fig in figs:        # axes = fig.gca()        # axes.set_title(label)        plt.tight_layout()        plt.show()    def save(self, folder=None, name=None):        # rc('text', usetex=True)        if folder is None:            from os.path import expanduser            folder = expanduser("~") + '/Desktop/'        if name is None:            name = self.name        if not '.pdf' in name:            name += '.pdf'        loc = folder + name        with PdfPages(loc) as pdf:            for fig in self.figs:                pdf.savefig()    ''' Add smth. to plot '''    def add_all_samples(self, **plt_opt):        samples = [s for s in self.study.all_samplegroup if s.meets_requirements(self.require_list)]        plt_opt.update({'alpha': 0.5, 'linestyle': ''})        self.plotting(samples=samples, **plt_opt)    def add_grid(self, visuals):        visuals = _to_list(visuals)        for plot in visuals:            if plot in self.visuals:                for fig in self.figs[plot]:                    fig.gca().grid()    def set_labels(self, xlabel=None, ylabel=None):        """        sets the xlabel/ylabel for all visuals. uses default if not specified        """        if not xlabel:            try:                xlabel = self.xlabel            except AttributeError:                xlabel = 'x-axis'        if not ylabel:            try:                ylabel = self.ylabel            except AttributeError:                ylabel = 'y-axis'        for plot in self.visuals:            for fig in self.figs[plot]:                fig.gca().set_xlabel(xlabel)                fig.gca().set_ylabel(ylabel)    def set_xlim(self, limits):        for plot in self.visuals:            for fig in self.figs[plot]:                fig.gca().set_xlim(limits)    def set_ylim(self, limits):        for plot in self.visuals:            for fig in self.figs[plot]:                fig.gca().set_ylim(limits)    def set_limits(self, xlim=None, ylim=None):        if xlim:            self.set_xlim(xlim)        if ylim:            self.set_xlim(ylim)    def set_title(self, title):        for plot in self.visuals:            for fig in self.figs[plot]:                fig.gca().set_title(title)    ''' GET FUNCTIONS '''    def get_plot_samples(self):        """        selects samples to be plotted according to the input data type.        study:            standard plot = sample_group means        sample_group:            standard plot = sample means        sample:            standard plot = measurement means        :return:        """        if self.input_type == RockPy.Study:            '''            First the study mean is plotted, then the group_means, with alpha = 0.5            '''            primary = self.study_mean()  # primary #rename study_mean            secondary = self.group_means()  # primary #rename study_mean        if self.input_type == RockPy.SampleGroup:            '''            first the group mean is plotted, then the samples_means            '''            primary = self.group_means()            secondary = self.sample_means()        if self.input_type == RockPy.Sample:            primary = self.sample_means()            secondary = [self.input]        if self.input_type == RockPy.Measurements.base.Measurement:            sample = deepcopy(self.input.sample_obj)            sample.measurements = [m for m in sample.measurements if m.m_idx == self.input.m_idx]            primary = [sample]            secondary = None        if self.input_type == list:            if all(isinstance(item, RockPy.Sample) for item in self.input):                primary = self.input        return primary, secondary    def plot_study_mean(self):        pass  # todo rewrite    def plot_group_mean(self):        pass  # todo rewrite    def plot_sample_mean(self):        pass  # todo rewrite    def _change_visible(self, text_or_line, lines):        caller = inspect.stack()[1][3][8:]        tol = {'line': self.line_dict,               'text': self.text_dict}        if not text_or_line in tol:  # check if text_or_line valid            tol_dict = tol[text_or_line]            if caller in tol_dict:                self.features[caller]()            else:                tols = tol_dict[caller]                for line in tols:                    bool = line.get_visible()                    line.set_visible(not bool)    def _add_line_text_dict(self, sample, ttype, tval, lines, texts=None):        caller = inspect.stack()[1][3][8:]        ''' line dict '''        if not caller in self.line_dict:            self.line_dict[caller] = {}                if not sample in self.line_dict[caller]:            self.line_dict[caller][sample] = {}                if not ttype in self.line_dict[caller][sample]:            self.line_dict[caller][sample][ttype] = {}                if not tval in self.line_dict[caller][sample][ttype]:            self.line_dict[caller][sample][ttype][tval] = []        self.line_dict[caller][sample][ttype][tval].append(lines)        ''' text dict '''        if not caller in self.text_dict:            self.text_dict[caller] = {}                if not sample in self.text_dict[caller]:            self.text_dict[caller][sample] = {}                if not ttype in self.text_dict[caller][sample]:            self.text_dict[caller][sample][ttype] = {}                if not tval in self.text_dict[caller][sample][ttype]:            self.text_dict[caller][sample][ttype][tval] = []                self.text_dict[caller][sample][ttype][tval].append(lines)    ''' functions for plotting '''    def study_mean(self):        """        calculates the sample_group mean for each sample group. Returns a list of samples, with the mean for each sample_group        :return:        """        samples = []        for sg in self.input:            sample = RockPy.Sample(name=sg.name + ' mean')            for visual, required in self.required.iteritems():                for mtype in required:                    # only take samples that meet all requirements of plot                    samples_met = [s for s in sg.sample_list if s.meets_requirements(self.require_list)]                    for ttype in sg.ttypes:                        for tval in sg.tvals:                            measurements = [m for s in samples_met for m in                                            s.get_measurements(mtype=mtype, ttype=ttype, tval=tval)]                            if len(measurements) == 0:                                break                            m = sample.mean_measurement_from_list(measurements)                            m.sample_obj = sample                            sample.measurements.append(m)            samples.append(sample)        return samples    def group_means(self):        raise NotImplementedError    def sample_means(self):        """        calculates the mean for all measurements grouped by ttype/ tval        :return: list(RockPy.Sample)        """        out = []        for s in self.study.samples:            sample = RockPy.Sample(name='mean ' + s.name)            sample.is_mean = True            for req in self.require_list:                for ttype in s.ttypes:                    for tval in s.tvals:                        mean_m = s.mean_measurement(mtype=req, ttype=ttype, tval=tval)                        mean_m.sample_obj = sample                        sample.mean_measurements.append(mean_m)            out.append(sample)        return out    ''' additional functions '''    def create_heat_color_map(self, value_list, reverse=False):        """        takes a list of values and creates a list of colors from blue to red (or reversed if reverse = True)        :param value_list:        :param reverse:        :return:        """        r = np.linspace(0, 255, len(value_list)).astype('int')        r = [hex(i)[2:-1].zfill(2) for i in r]        # r = [i.encode('hex') for i in r]        b = r[::-1]        out = ['#%2s' % r[i] + '00' + '%2s' % b[i] for i in range(len(value_list))]        if reverse:            out = out[::-1]        return out    ''' Features '''    def feature_grid(self, **plt_opt):        for visuals in self.figs:            for figure in self.figs[visuals]:                ax = figure.gca()                lines = Features.generic.grid(ax, **plt_opt)                self._add_line_text_dict('none','none', 'none', lines)