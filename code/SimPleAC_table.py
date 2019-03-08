from SimPleAC_setup import SimPleAC_setup
from robust.robust import RobustModel
import numpy as np
from gpkit.small_scripts import mag

from math import log10, floor
def round_sig(x, sig=2):
    return round(x, sig-int(floor(log10(abs(x))))-1)

if __name__ == "__main__":
    m, subs = SimPleAC_setup()
    sol = m.localsolve(verbosity=2)

    methods = [{'name': 'Best Pairs', 'twoTerm': True, 'boyd': False, 'simpleModel': False}]
    uncertainty_sets = ['elliptical']

    bm = RobustModel(m, 'box', twoTerm = True, boyd = False, OsimpleModel = False, gamma = 1)
    bsol = bm.robustsolve(verbosity=2)

    em = RobustModel(m, 'elliptical', twoTerm = True, boyd = False, simpleModel = False, gamma = 1)
    esol = em.robustsolve(verbosity=2)

    for i in ['L/D', 'A', 'Re', 'S', 'V', 't_s', 'W_w', 'W_{w_{strc}}', 'W_{w_{surf}}',
              'V_{f_{avail}}', 'V_{f_{fuse}}', 'V_{f_{wing}}']:
        if i in ['L/D', 'Re', 'V']:
            a = [mag(np.mean(s(i))) for s in [sol,bsol,esol]]
        elif i in [ 't_s']:
            a = [mag(np.sum(s(i))) for s in [sol,bsol,esol]]
        else:
            a = [mag(s(i))  for s in [sol,bsol,esol]]
        print ["& " + str(round_sig(j,3)) for j in a]
