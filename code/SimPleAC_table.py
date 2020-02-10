from __future__ import print_function
from builtins import str
from SimPleAC_setup import SimPleAC_setup
from gpkit import Model, units
from robust.robust import RobustModel
import numpy as np
from gpkit.small_scripts import mag
from robust.robust import RobustGPTools

from SimPleAC_draw import SimPleAC_draw

from math import log10, floor

def round_sig(x, sig=2):
    return round(x, sig-int(floor(log10(abs(x))))-1)

if __name__ == "__main__":
    m, subs = SimPleAC_setup()
    m.cost = m['W_{f_m}']#+m['C_m']*m['t_m']*units('N')
    # m.cost = m['W_e']
    sol = m.localsolve(verbosity=2)

    methods = [{'name': 'Best Pairs', 'twoTerm': True, 'boyd': False, 'simpleModel': False}]
    uncertainty_sets = ['elliptical']
    gamma = 1
    margin_subs = {k: v + np.sign(mag(sol['sensitivities']['constants'][k.key]))*k.key.pr * v / 100.0
                                     for k, v in m.substitutions.items()
                                     if k in m.varkeys and RobustGPTools.is_directly_uncertain(k)}

   # Model with margins
    mm = Model(m.cost, m, subs)
    mm.substitutions.update(margin_subs)
    msol = mm.localsolve(verbosity=2)

    # Model with box uncertainty
    bm = RobustModel(m, 'box', twoTerm = True, boyd = False, simpleModel = False, gamma = gamma)
    bsol = bm.robustsolve(verbosity=2)

    # Model with elliptical uncertainty
    em = RobustModel(m, 'elliptical', twoTerm = True, boyd = False, simpleModel = False, gamma = gamma)
    esol = em.robustsolve(verbosity=2)

    try:
        soltab = [sol, msol, bsol, esol]
    except:
        soltab = [sol, bsol, esol]

    for i in ['L/D', 'C_{D_{wpar}}', 'C_{D_{ind}}', 'C_{D_{fuse}}', 'Re', 'V', 't_s', 'A', 'S', '\\tau', 'W_w', 'W_{w_{strc}}', 'W_{w_{surf}}',
              'W_{fuse}','V_{f_{avail}}', 'V_{f_{fuse}}', 'V_{f_{wing}}']:
        print(i + " ")
        if i in ['L/D', 'Re', 'V', 'C_{D_{fuse}}', 'C_{D_{wpar}}', 'C_{D_{ind}}']:
            a = [mag(np.mean(s(i))) for s in soltab]
        elif i in [ 't_s']:
            a = [mag(np.sum(s(i))) for s in soltab]
        else:
            a = [mag(s(i))  for s in soltab]
        print(["& " + str(round_sig(j,3)) for j in a])
    print(['cost'])
    for i in soltab:
        print(i['cost'])

    colors = ['blue', 'orange', 'red', 'green']
    labels = ['nominal', 'margins', 'box', 'elliptical']
    directory = 'savefigs'
    count = 0
    for i in soltab:
        SimPleAC_draw(i, colors[count], directory, labels[count])
        count += 1
