from SimPleAC_setup import SimPleAC_setup
from gpkit import units, Model
from gpkit.constraints.bounded import Bounded
from gpkit.small_scripts import mag

# for radar charts
from radar import *

def removesubs(d, keyList):
    a = dict(d)
    for i in keyList:
        del a[i.key.name]
    return a

if __name__ == "__main__":
    m, subs = SimPleAC_setup()
    # Putting in objectives and associated substitutions
    # in a dictionary
    objectives = {m['W_{f_m}'] :                      {'name': 'Total fuel', 'added': {}, 'removed': {}},
                  m['C_m']*m['t_m'] :                 {'name': 'Time cost', 'added': {}, 'removed': {}},
                  #m['V_{min_m}'] :                    {'added': {}, 'removed': [m['V_{min_m}']]},
                  m['W']:                             {'name': 'Takeoff weight', 'added': {}, 'removed': {}},
                  m['A']:                             {'name': 'Aspect ratio', 'added': {}, 'removed': {}},
                  m['W_e']:                           {'name': 'Engine weight', 'added': {}, 'removed': {}},
                  m['W']/m['S']:                      {'name': 'Wing loading', 'added': {}, 'removed': {}},
                  m['W_{f_m}']+m['C_m']*m['t_m']*units('N') : {'name': 'Total cost', 'added': {}, 'removed': {}},
                  }
    models = {}
    solutions = {}

    # Adding minimizer to make sure all objectives are 'tight' at optima
    minimizer=10**-15
    for i in objectives.iterkeys():
        if i.unitstr() == 'N':
            minimizer = minimizer*i

     # Solving the optimization problems
    for i in objectives.iterkeys():
        m.substitutions.update(subs)
        try:
            m = Model(i+minimizer/minimizer.units*i.units, Bounded(m))
        except:
            m = Model(i+minimizer/minimizer.units, Bounded(m))
        models[i] = m
        solutions[i] = m.localsolve(verbosity=0)

    # Generating data amenable to radar plotting
    data =[]
    data.append([objectives[j]['name'] for j in objectives.iterkeys()])

    maxesindata = np.zeros(len(objectives))
    for i in objectives.iterkeys():
        case = objectives[i]['name']
        caseData = []
        count = 0
        for j in objectives.iterkeys():
            caseData.append(mag(solutions[i](j)))
            if mag(solutions[i](j)) >= maxesindata[count]:
                maxesindata[count] = mag(solutions[i](j))
            count +=1
        data.append((case, [caseData]))

    # Plotting
    N = len(solutions)
    theta = radar_factory(N, frame='polygon')
    spoke_labels = data.pop(0)

    fig, axes = plt.subplots(figsize=(7,7), nrows=4, ncols=2,
                             subplot_kw=dict(projection='radar'))
    fig.subplots_adjust(wspace=0.25, hspace=0.20, top=0.85, bottom=0.05)

    colors = ['b', 'r', 'g', 'm', 'y', 'c', 'o']

    for ax, (title, case_data) in zip(axes.flatten(), data):
        #ax.set_rgrids([0.2, 0.4, 0.6, 0.8])
        ax.set_title(title, weight='bold', size='medium', position=(0.5, 1.1),
                     horizontalalignment='center', verticalalignment='center')
        for d, color in zip(case_data, colors):
            print d/maxesindata
            ax.plot(theta, d/maxesindata, color=color)
            ax.fill(theta, d/maxesindata, facecolor=color, alpha=0.25)
        ax.set_varlabels(spoke_labels)

    # add legend relative to top-left plot
    ax = axes[0, 0]
    labels = spoke_labels
    legend = ax.legend(labels, loc=(0.9, .95),
                       labelspacing=0.1, fontsize='small')

    # fig.text(0.5, 0.965, '5-Factor Solution Profiles Across Four Scenarios',
    #          horizontalalignment='center', color='black', weight='bold',
    #          size='large')

    plt.show()
    plt.savefig('savefigs/radar.png')
