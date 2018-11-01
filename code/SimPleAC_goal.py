# This script implements a goal programming approach with SimPleAC

from SimPleAC_setup import SimPleAC_setup
from gpkit import units, Model, Variable, Monomial
from gpkit.constraints.bounded import Bounded
from gpkit.small_scripts import mag

from robust.robust import RobustModel
from robust.simulations.simulate import generate_model_properties
from robust.robust_gp_tools import RobustGPTools

import numpy as np

import matplotlib.pyplot as plt

if __name__ == "__main__":
    m, subs = SimPleAC_setup()
    sol , _, _, directly_uncertain_vars_subs = generate_model_properties(m, 1, 1)  # solving the SimPleAC
    Gamma = Variable('\\Gamma','-','Uncertainty bound')
    solBound = Variable('1+\\delta', '-', 'Acceptable optimal solution bound')
    origcost = m.cost
    m = Model(1/Gamma, [m, origcost <= Monomial(sol(origcost))*solBound, Gamma <= 1e30, solBound <= 1e30], m.substitutions)
    ndeltas = 11
    deltas = np.linspace(2./ndeltas,2.,ndeltas)
    gammas = np.zeros(ndeltas)
    costs = np.zeros(ndeltas)
    hotstart = sol
    for i in range(ndeltas):
        m.substitutions.update({'1+\\delta':1+deltas[i]})
        rm = RobustModel(m, 'elliptical', twoTerm=False, gamma=Gamma, x0=hotstart)
        rmsol = rm.robustsolve(verbosity=2)  # solve the robust model
        gammas[i] = 1/mag(rmsol('\\Gamma'))
        costs[i] = mag(rmsol(origcost))
        hotstart = rmsol

    plt.plot(gammas,costs)

