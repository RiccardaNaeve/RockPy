__author__ = 'mike'
import base


class Backfield(base.Generic):
    def __init__(self, sample_list, norm='mass',
                 plot='show', folder=None, name='arai plot',
                 plt_opt=None, style='screen',
                 **options):
        super(Backfield, self).__init__(sample_list, norm=None,
                                        plot=plot, folder=folder, name=name,
                                        plt_opt=plt_opt, style=style,
                                        **options)

        self.show()
        self.x_label = 'Field [%s]' % ('T')  # todo get_unit
        self.y_label = 'Magnetic Moment [%s]' % ('Am^2')  # todo get_unit

        if style == 'publication':
            self.setFigLinesBW()

        self.out()

    def show(self):