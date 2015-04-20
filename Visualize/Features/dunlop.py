__author__ = 'mike'


def dunlop_data(ax, m_obj, component='mag', **plt_opt):
    marker = plt_opt.pop('marker', 's')
    markersize = plt_opt.pop('markersize', 3)
    linestyle = plt_opt.pop('linestyle', '-')
    colors = ['r', 'g', 'b']
    lines = []
    for i, v in enumerate(['th', 'ptrm', 'sum']):
        x = m_obj.data[v]
        y = m_obj.data[v]
        line = ax.plot(x['temp'].v, y[component].v,
                       marker=marker,
                       linestyle=linestyle,
                       markersize=markersize,
                       zorder=100,
                       label=v,
                       color=colors[i],
                       **plt_opt)
        lines.append(line)
    return lines