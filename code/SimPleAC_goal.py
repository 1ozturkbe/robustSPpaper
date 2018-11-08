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
    # Setting up problem
    m, subs = SimPleAC_setup()
    sol , _, _, directly_uncertain_vars_subs = generate_model_properties(m, 1, 1)  # solving the SimPleAC
    Gamma = Variable('\\Gamma','-','Uncertainty bound')
    solBound = Variable('1+\\delta', '-', 'Acceptable optimal solution bound')
    origcost = m.cost

    # Solution using standard method of changing Gamma
    nGammas = 11
    gammasGammas = np.linspace(1./nGammas,1.,nGammas)
    costsGammas = np.zeros(nGammas)
    hotstart = sol
    for i in range(nGammas):
        rm = RobustModel(m,'elliptical',twoTerm = False, gamma = gammasGammas[i], x0 = hotstart)
        rmsol = rm.robustsolve(verbosity=2)
        costsGammas[i] = mag(rmsol(origcost))
        hotstart = rmsol

    # Goal programming (risk minimization) setup
    m = Model(1/Gamma, [m, origcost <= Monomial(sol(origcost))*solBound, Gamma <= 1e30, solBound <= 1e30], m.substitutions)
    ndeltas = nGammas
    deltas = np.linspace(1.5/ndeltas,1.5,ndeltas)
    gammasGoal = np.zeros(ndeltas)
    costsGoal = np.zeros(ndeltas)
    hotstart = sol

    # Solution using goal programming
    for i in range(ndeltas):
        m.substitutions.update({'1+\\delta':1+deltas[i]})
        rm = RobustModel(m, 'elliptical', twoTerm=False, gamma=Gamma, x0=hotstart)
        rmsol = rm.robustsolve(verbosity=2)  # solve the robust model
        gammasGoal[i] = 1/mag(rmsol('\\Gamma'))
        costsGoal[i] = mag(rmsol(origcost))
        hotstart = rmsol

    # Results
    plt.rc('text', usetex=True)
    plt.rc('font', family='serif')

    plt.figure()
    plt.plot(gammasGammas,costsGammas)
    plt.plot(gammasGoal, costsGoal)
    plt.title('Costs with objective minimization and risk minimization')
    plt.xlabel("Size of uncertainty set, $\Gamma$")
    plt.show()

    # Odd results
    plt.figure()
    plt.plot(deltas, gammasGoal)
    plt.xlabel('Percent deviation from nominal optimum')
    plt.ylabel('Size of uncertainty set')
    plt.title('We capture less uncertainty with more deviation from optimum. Not normal.')
    plt.show()


