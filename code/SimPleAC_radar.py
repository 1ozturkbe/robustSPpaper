from __future__ import print_function
from __future__ import division
from builtins import zip
from builtins import str
from builtins import range
from SimPleAC_setup import SimPleAC_setup
from gpkit import units, Model
from gpkit.constraints.bounded import Bounded
from gpkit.small_scripts import mag

# for radar charts
from radar import *
from math import ceil, floor
import numpy as np

from robust.robust import RobustModel
from collections import OrderedDict

from SimPleAC_draw import SimPleAC_draw

def gen_SimPleAC_radar(marray, methods, objectives, keyOrder, baseobj):
    """
    Function to generate radar plots
    :param marray: 2D array of models to run
                   can be nominal or robust models
                   each must have objective costs
                   [:,j] are to be plotted on the same radar plot, for all j
                   [i,:] are the different radar plots, for all i
    :param objectives: the objectives to be plotted on each radar plot
    :return: Solutions array that is size(marray). The radar plots are saved as a figure.
    """
    solutions = [[] for i in range(len(marray))]
    for i in range(len(marray)):
        for j in range(len(marray[i])):
            try:
                solutions[i].append(marray[i][j].localsolve(reltol=1e-4))
            except:
                solutions[i].append(marray[i][j].robustsolve(reltol=1e-4))

    data, maxesindata, minsindata = generate_radar_data(solutions, objectives, keyOrder, baseobj)

    plot_radar_data(solutions, methods, data, maxesindata, minsindata)

    return solutions

def plot_radar_data(solutions, methods, data, maxesindata, minsindata):
    # Plotting
    N = len(solutions)
    theta = radar_factory(N, frame='polygon')
    spoke_labels = data[0]
    fig, axes = plt.subplots(figsize=(N,N), nrows=int(ceil(N/2.)), ncols=2,
                             subplot_kw=dict(projection='radar'))
    fig.subplots_adjust(wspace=0.1, hspace=0.55, top=0.9, bottom=0.05)

    colors = ['b', 'g','r','m', 'y', 'c', 'o']

    for ax, (title, case_data) in zip(axes.flatten(), data[1:]):
        ax.set_title(title, weight='bold', size='medium', position=(0.5, 1.15),
                     horizontalalignment='center', verticalalignment='center')
        ax.tick_params(labelleft=True)
        for d, color in zip(case_data, colors):
            print(d/maxesindata)
            ax.plot(theta, d/maxesindata, color=color)
            ax.fill(theta, d/maxesindata, facecolor=color, alpha=0.25)
        ax.set_varlabels(spoke_labels)

    # add legend relative to top-left plot
    ax = axes[0, 0]
    labels = methods
    legend = ax.legend(labels, loc=(1.25, .925),
                       labelspacing=0.1, fontsize='small')
    plt.show()
    plt.savefig('savefigs/radar.png')

def generate_radar_data(solutions, objectives, keyOrder, baseobj):
        # Generating data amenable to radar plotting
        data =[]
        data.append([objectives[keyOrder[j]]['name'] for j in range(len(keyOrder))])

        maxesindata = np.zeros(len(objectives))
        minsindata = 10.**8*np.ones(len(objectives))
        counti = 0
        for i in range(len(keyOrder)):
            case = objectives[keyOrder[i]]['name']
            caseData = [[] for j in range(len(solutions[counti]))]
            for j in range(len(solutions[counti])):
                countk = 0
                for k in range(len(keyOrder)):
                    caseData[j].append(mag(solutions[counti][j](keyOrder[k])))
                    if mag(solutions[counti][j](keyOrder[k])) >= maxesindata[countk]:
                        maxesindata[countk] = mag(solutions[counti][j](keyOrder[k]))
                    if mag(solutions[counti][j](keyOrder[k])) <= minsindata[countk]:
                        minsindata[countk] = mag(solutions[counti][j](keyOrder[k]))
                    countk +=1
            data.append((case, caseData))
            counti +=1
        return data, maxesindata, minsindata

if __name__ == "__main__":
    m, subs = SimPleAC_setup()
    # Putting in objectives and associated substitutions
    # in a dictionary
    objectives = {m['W_{f_m}']                  : {'name': 'Total fuel', 'added': {}, 'removed': {}},
                  m['W_{f_m}']+m['C_m']*m['t_m']*units('N') : {'name': 'Total cost', 'added': {}, 'removed': {}},
                  m['W']                                    : {'name': 'Takeoff weight', 'added': {}, 'removed': {}},
                  sum(m['D'] / m['L'])                      : {'name': '1/(Cruise L/D)', 'added': {}, 'removed': {}},
                  m['W_e']                                  : {'name': 'Engine weight', 'added': {}, 'removed': {}},
                  m['S']                                    : {'name': 'Wing area', 'added': {}, 'removed': {}},
                                                }
    keyOrder = [m['W_{f_m}'], m['W_{f_m}']+m['C_m']*m['t_m']*units('N'), m['W'],
                sum(m['D'] / m['L']), m['W_e'], m['S']]

    models = {}
    baseobj = m['W_{f_m}']

    # Adding minimizer so all objectives are tight at the optimum
    minimizer = 10**-8*sum(i/i.units if i.units else i for i in objectives.keys())
    # Nominal case must always be first!
    methods = ['nominal','ellipsoidal','box']
    marray = [[] for i in range(len(keyOrder))]
    counti = 0
    for i in range(len(keyOrder)):
        for j in methods:
            try:
                nm = Model(keyOrder[i] + minimizer*keyOrder[i].units, m, m.substitutions)
            except:
                nm = Model(keyOrder[i] + minimizer, m, m.substitutions)
            if j == 'nominal':
                marray[counti].append(nm)
            else:
                nm = RobustModel(nm, j, twoTerm = False, gamma = 1)
                marray[counti].append(nm)
        counti += 1

    solutions = gen_SimPleAC_radar(marray, methods, objectives, keyOrder, baseobj)

    colors = ['blue', 'red', 'green']
    directory = 'savefigs'

    # # Saving data
    [data, maxesindata, minsindata] = generate_radar_data(solutions, objectives, keyOrder, baseobj)
    # Placeholder for plot debugging and proper spoke labeling
    # plot_radar_data(solutions, methods, data, maxesindata, minsindata)
    # spoke_labels = ['       Total fuel',
    # 'Total cost',
    # 'Takeoff weight',
    # '1/(Cruise L/D)              ',
    # 'Engine weight',
    # 'Wing area']

    plotno = 0
    for i in solutions:
        count = 0
        for j in i:
            name = str(plotno) + methods[count]
            SimPleAC_draw(j, colors[count], directory, name)
            count += 1
        plotno += 1











