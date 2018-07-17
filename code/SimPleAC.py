from gplibrary.SP.SimPleAC.SimPleAC_mission import Mission, SimPleAC
from robust.robust_gp_tools import SameModel
from gpkit import Model, Variable, units
from gpkit.constraints.bounded import Bounded

def removesubs(d, keyList):
    a = dict(d)
    for i in keyList:
        del a[i.key.name]
    return a

a = SimPleAC()
m = Mission(a, 4)
subs = {
    'h_{cruise_m}'   :5000*units('m'),
    'Range_m'        :3000*units('km'),
    'W_{p_m}'        :6250*units('N'),
    'C_m'            :120*units('1/hr'),
    'V_{min_m}'      :25*units('m/s'),
    'T/O factor_m'   :2,
}

# Putting in objectives and associated substitutions
# in a dictionary
objectives = {m['W_{f_m}'] :                      {'added': {}, 'removed': {}},
              m['C_m']*m['t_m'] :                 {'added': {}, 'removed': {}},
              #m['V_{min_m}'] :                    {'added': {}, 'removed': [m['V_{min_m}']]},
              m['W']:                             {'added': {}, 'removed': {}},
              m['A']:                             {'added': {}, 'removed': {}},
              m['W_e']:                           {'added': {}, 'removed': {}},
              m['W']/m['S']:                      {'added': {}, 'removed': {}},
              m['W_{f_m}']*units('1/N')+m['C_m']*m['t_m'] :    {'added': {}, 'removed': {}},
              }
models = {}
solutions = {}

for i in objectives.iterkeys():
    #m = Mission(a, 4)
    #substitutions = {}
    #substitutions.update(subs)
    #substitutions.update(objectives[i]['added'])
    #substitutions = removesubs(substitutions,objectives[i]['removed'])
    m.substitutions.update(subs)
    m = Model(i, Bounded(m))
    models[i] = m
    solutions[i] = m.localsolve(verbosity=2)
