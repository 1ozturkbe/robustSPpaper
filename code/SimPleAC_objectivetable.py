import csv
import numpy as np

from gpkit import Model, units
from SimPleAC_setup import SimPleAC_setup
from SimPleAC_radar import generate_radar_data, gen_SimPleAC_radar

def objective_table_csv(objectives, data, keyOrder, baseresult):
    rawdata = [None] * (len(objectives) + 1)
    rawdata[0] = ['Objective'] + [objectives[i]['name'] for i in keyOrder]
    count = 0
    for i in range(len(keyOrder)):
        count += 1
        rawdata[count] = [objectives[keyOrder[i]]['name']] + list(np.around(np.divide(np.array(data[count][1][0]),np.array(baseresult)),decimals=2))
    with open("savefigs/objective_table.csv",'w') as resultFile:
        wr = csv.writer(resultFile, dialect='excel')
        for i in range(len(rawdata)):
            wr.writerow(rawdata[i])

if __name__ == "__main__":
    m, subs = SimPleAC_setup()
    # Putting in objectives and associated substitutions
    # in a dictionary
    objectives = {m['W_{f_m}']                  : {'name': 'Total fuel', 'added': {}, 'removed': {}},
                  m['C_m']*m['t_m']                         : {'name': 'Time cost', 'added': {}, 'removed': {}},
                  m['W_{f_m}']+m['C_m']*m['t_m']*units('N') : {'name': 'Total cost', 'added': {}, 'removed': {}},
                  m['W']                                    : {'name': 'Takeoff weight', 'added': {}, 'removed': {}},
                  1/(m['L'][2]/m['D'][2])                   : {'name': '1/(Cruise L/D)', 'added': {}, 'removed': {}},
                  m['A']                                    : {'name': 'Aspect ratio', 'added': {}, 'removed': {}},
                  m['W_e']                                  : {'name': 'Engine weight', 'added': {}, 'removed': {}},
                  m['W']/m['S']                             : {'name': 'Wing loading', 'added': {}, 'removed': {}},
                              }
    keyOrder = [m['W_{f_m}'], m['C_m']*m['t_m'], m['W_{f_m}']+m['C_m']*m['t_m']*units('N'), m['W'],
                1/(m['L'][2]/m['D'][2]), m['A'], m['W_e'], m['W']/m['S']]

    models = {}
    baseobj = m['W_{f_m}']

    # Adding minimizer so all objectives are tight at the optimum
    minimizer = 10**-6*sum(i/i.units if i.units else i for i in objectives.keys())
    # Nominal case must always be first!
    marray = [[] for i in range(len(keyOrder))]
    for i in range(len(keyOrder)):
        try:
            nm = Model(keyOrder[i] + minimizer*keyOrder[i].units, m, m.substitutions)
        except:
            nm = Model(keyOrder[i] + minimizer, m, m.substitutions)
        marray[i].append(nm)

    # Solving marray
    solutions = gen_SimPleAC_radar(marray, objectives, keyOrder, baseobj)
    # Tabulating data
    [data, maxesindata, minsindata] = generate_radar_data(solutions, objectives, keyOrder, baseobj)
    # Storing in csv
    baseresult = data[1][1][0] # result for fuel burn for comparison
    objective_table_csv(objectives, data, keyOrder, baseresult)


