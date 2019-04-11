from SimPleAC_setup import SimPleAC_setup
from gpkit import units
from robust.robust import RobustModel
import numpy as np
from gpkit.small_scripts import mag

from SimPleAC_draw import SimPleAC_draw

from math import log10, floor

def round_sig(x, sig=2):
    return round(x, sig-int(floor(log10(abs(x))))-1)

if __name__ == "__main__":
    m, subs = SimPleAC_setup()
    m.cost = m['W_{f_m}']#+m['C_m']*m['t_m']*units('N')
    sol = m.localsolve(verbosity=2)

    methods = [{'name': 'Best Pairs', 'twoTerm': True, 'boyd': False, 'simpleModel': False}]
    uncertainty_sets = ['elliptical']

    rm = RobustModel(m, 'elliptical', twoTerm = True, boyd = False, simpleModel = False, gamma = 0)
    rsol = rm.robustsolve(verbosity=2)


    bm = RobustModel(m, 'box', twoTerm = True, boyd = False, simpleModel = False, gamma = 1)
    bsol = bm.robustsolve(verbosity=2)

    em = RobustModel(m, 'elliptical', twoTerm = True, boyd = False, simpleModel = False, gamma = 1)
    esol = em.robustsolve(verbosity=2)

    try:
        soltab = [sol, rsol, bsol, esol]
    except:
        soltab = [sol, bsol, esol]

    for i in ['L/D', 'A', 'Re', 'S', 'V', 't_s', 'W_w', 'W_{w_{strc}}', 'W_{w_{surf}}',
              'V_{f_{avail}}', 'V_{f_{fuse}}', 'V_{f_{wing}}']:
        print i + " "
        if i in ['L/D', 'Re', 'V']:
            a = [mag(np.mean(s(i))) for s in soltab]
        elif i in [ 't_s']:
            a = [mag(np.sum(s(i))) for s in soltab]
        else:
            a = [mag(s(i))  for s in soltab]
        print ["& " + str(round_sig(j,3)) for j in a]
    print ['cost']
    for i in soltab:
        print i['cost']

    for i in soltab:
        SimPleAC_draw(i)
