__author__ = 'mike'
import base
import matplotlib.pyplot as plt

class Dunlop(base.Generic):
    def initialize_plot(self):
        super(Dunlop, self).initialize_plot()
        self.plot = self.add_plot(label='dunlop')

    def plotting(self):
        x = range(1,100)
        y = [i**2.3 for i in x]
        ax = self.plots['dunlop'].add_subplot(111)
        ax.plot(x,y)

class Arai(base.Generic):
    def initialize_plot(self):
        super(Arai, self).initialize_plot()
        self.plot = self.add_plot(label='arai')

    def plotting(self):
        x = range(1,100)
        y = [3*i for i in x]

        ax = self.plots['arai'].add_subplot(111)
        ax.plot(x,y)

class Multiple(base.Generic):
    def initialize_plot(self):
        arai = Arai()
        dunlop = Dunlop()
        super(Multiple, self).initialize_plot()
        self.add_fig(arai)
        self.add_fig(dunlop)
        print self.existing_visuals

def test():
    Plot = Multiple()
    print Plot.plots
    Plot.show()


if __name__ == '__main__':
    test()