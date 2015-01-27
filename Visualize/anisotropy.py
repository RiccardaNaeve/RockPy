__author__ = 'wack'


from RockPy.Visualize.stereo import Stereo
import RockPy.Measurements.anisotropy
from RockPy.Functions.general import MirrorDirectionToNegativeInclination


class Anisotropy(Stereo):
    """
    visualize anisotropy tensors on stereo net
    square: maximum direction, triangle: intermediate direction, circle: minimum direction
    plot always on lower hemisphere
    """
    _required = ['anisotropy']

    def initialize_visual(self):
        super(Anisotropy, self).initialize_visual()
        self._required = RockPy.Measurements.anisotropy.Anisotropy
        self.standard_features.append(self.feature_eigenvectors)  # plot eigenvectors by default

    def feature_eigenvectors(self, m_obj, **plt_opt):
        m_obj.calculate_tensor()

        # todo: also called for mean ?!!
        for n, idx in {1: ("D1", "I1"), 2: ("D2", "I2"), 3: ("D3", "I3")}.items():
            # choose symbol based on n
            if n == 1: m = "s"  # square
            elif n == 2: m = "^"  # triangle
            elif n == 3: m = "o"  # circle
            else: raise RuntimeError('feature_eigenvectors n = %s' % str(n))

            d, i = m_obj.results[idx].v[0]
            d, i = MirrorDirectionToNegativeInclination(d, i)
            lines = self.ax.plot(*self.stereomap(d, i), marker=m, markersize = 20, **plt_opt)
            self._add_line_text_dict(m_obj.sample_obj.name, '_'.join(m_obj.ttypes), '_'.join(map(str, m_obj.tvals)), lines)