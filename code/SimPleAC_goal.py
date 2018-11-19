# This script implements a goal programming approach with SimPleAC

from SimPleAC_setup import SimPleAC_setup
from gpkit import units, Model, Variable, Monomial
from gpkit.constraints.bounded import Bounded
from gpkit.small_scripts import mag

from robust.robust import RobustModel
from robust.simulations.simulate import generate_model_properties
from robust.robust_gp_tools import RobustGPTools
from robust.simulations.simulate import simulate_robust_model

import numpy as np

import matplotlib.pyplot as plt

if __name__ == "__main__":
    # Setting up problem
    m, subs = SimPleAC_setup()
    number_of_time_average_solves = 10
    number_of_iterations = 200
    sol, _, _, directly_uncertain_vars_subs = generate_model_properties(m, number_of_time_average_solves,
                                                                        number_of_iterations)  # solving the SimPleAC
    Gamma = Variable('\\Gamma', '-', 'Uncertainty bound', fix = True)
    solBound = Variable('1+\\delta', '-', 'Acceptable optimal solution bound', fix = True)
    origcost = m.cost

    # Robust models setup
    linearization_tolerance = 1e-3
    min_num_of_linear_sections = 3
    max_num_of_linear_sections = 99
    verbosity = 0
    nominal_solution = sol
    methods = [{'name': 'Best Pairs', 'twoTerm': True, 'boyd': False, 'simpleModel': False},
               {'name': 'Linear. Perts.', 'twoTerm': False, 'boyd': False, 'simpleModel': False},
               {'name': 'Simple Cons.', 'twoTerm': False, 'boyd': False, 'simpleModel': True},
               {'name': 'Two Term', 'twoTerm': False, 'boyd': True, 'simpleModel': False}]
    method = methods[0]

    # Solution using standard method of changing Gamma
    nGammas = 15
    gammasGammas = np.linspace(0.85, 1.35, nGammas)
    costsGammas = np.zeros(nGammas)
    poFGammas = np.zeros(nGammas)
    hotstart = sol
    for i in range(nGammas):
        rm, rmsol, rmsoltime, simulation_results = simulate_robust_model(m, method, 'elliptical', gammasGammas[i],
                                                                         directly_uncertain_vars_subs,
                                                                         number_of_iterations, linearization_tolerance,
                                                                         min_num_of_linear_sections,
                                                                         max_num_of_linear_sections, verbosity,
                                                                         nominal_solution,
                                                                         number_of_time_average_solves)
        costsGammas[i] = mag(rmsol(origcost))
        poFGammas[i] = simulation_results[0]

    # Goal programming (risk minimization) setup
    mGoal = Model(1 / Gamma, [m, origcost <= Monomial(sol(origcost)) * solBound, Gamma <= 1e30, solBound <= 1e30],
                  m.substitutions)
    mGoal.substitutions.update({'1+\\delta': 1 + 1e-2})
    nominal_solution = mGoal.localsolve()
    ndeltas = nGammas
    deltas = np.linspace(0.001, 2.2, ndeltas)
    gammasGoal = np.zeros(ndeltas)
    costsGoal = np.zeros(ndeltas)
    poFGoal = np.zeros(ndeltas)
    hotstart = sol

    # Solution using goal programming
    for i in range(ndeltas):
        mGoal.substitutions.update({'1+\\delta': 1 + deltas[i]})
        rm, rmsol, rmsoltime, simulation_results = simulate_robust_model(mGoal, method, 'elliptical', Gamma,
                                                                         directly_uncertain_vars_subs,
                                                                         number_of_iterations, linearization_tolerance,
                                                                         min_num_of_linear_sections,
                                                                         max_num_of_linear_sections, verbosity,
                                                                         nominal_solution,
                                                                         number_of_time_average_solves)
        gammasGoal[i] = mag(rmsol('\\Gamma'))
        costsGoal[i] = mag(rmsol(origcost))
        poFGoal[i] = simulation_results[0]

    #
    # Results
    plt.rc('text', usetex=True)
    plt.rc('font', family='serif')

    plt.figure()
    plt.plot(gammasGammas, costsGammas)
    plt.plot(gammasGoal, costsGoal)
    plt.xlabel("Size of uncertainty set, $\Gamma$")
    plt.ylabel("Normalized fuel burn")
    plt.show()

    plt.figure()
    plt.plot(gammasGammas, poFGammas)
    plt.plot(gammasGoal, poFGoal)
    plt.xlabel("Size of uncertainty set, $\Gamma$")
    plt.ylabel("Probability of failure")
    plt.show()
