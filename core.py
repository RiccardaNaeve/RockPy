import numpy as np
import matplotlib.pyplot as plt
import matplotlib.path as mpath

def _to_list(oneormoreitems):
    """
    convert argument to tuple of elements
    :param oneormoreitems: single number or string or list of numbers or strings
    :return: tuple of elements
    """
    return oneormoreitems if hasattr(oneormoreitems, '__iter__') else [oneormoreitems]

def plt_logo():
    x = np.linspace(-5, 5   )
    y1 = np.tanh(x)
    y2 = np.tanh(x-1)
    y3 = np.tanh(x+1)

    y4, y5 = x*np.sin(np.pi)+np.cos(np.pi)*np.tanh(x), x*np.sin(np.pi)+np.cos(np.pi)*np.tanh(x-1),
    y6, y7 = x*np.sin(np.pi)+np.cos(np.pi)*np.tanh(x), x*np.sin(np.pi)+np.cos(np.pi)*np.tanh(x+1),

    plt.fill_between(x, y1, y2, color = '#009440')
    plt.fill_between(x, y1, y3, color = '#7F7F7F')


    plt.plot(x,y1, 'k')
    plt.plot(x,y2, 'k')
    plt.plot(x,y3, 'k')
    plt.plot(x,y4, 'k', zorder=100)
    plt.plot(x,y5, 'k', zorder=100)
    plt.plot(x,y6, 'k', zorder=100)
    plt.plot(x,y7, 'k', zorder=100)
    plt.fill_between(x, y4, y5, color = '#009440', zorder=100)
    plt.fill_between(x, y6, y7, color = '#7F7F7F', zorder=100)
    fig = plt.gcf()
    # circle1 = plt.Circle((0,0),4,color='w', alpha=0.1)
    # fig.gca().add_artist(circle1)

    c1 = np.sqrt(10 - x**2)
    c2 = -np.sqrt(10 - x**2)

    plt.plot(x,c1, 'k')
    plt.plot(x,c2,'k')
    ax = fig.gca()
    ax.axis('equal')
    ax.set_xlim(-3.3,3.3)
    ax.set_ylim(-3.3,3.3)
    plt.show()

if __name__ == '__main__':
    plt_logo()