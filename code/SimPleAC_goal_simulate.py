# This script implements a goal programming approach with SimPleAC

from SimPleAC_setup import SimPleAC_setup
from gpkit import units, Model, Variable, Monomial
from gpkit.constraints.bounded import Bounded
from gpkit.small_scripts import mag

from robust.robust import RobustModel
from robust.simulations.simulate import generate_model_properties
from robust.robust_gp_tools import RobustGPTools
from robust.simulations.simulate import simulate_robust_model
import robust.simulations.simulate as simulate
from robust.simulations.simulate import plot_gamma_result_PoFandCost
from robust.simulations.simulate import filter_gamma_result_dict

import numpy as np

import matplotlib.pyplot as plt

from SimPleAC_save import save_obj, load_obj
import cPickle as pickle

if __name__ == "__main__":
    model, subs = SimPleAC_setup()
    number_of_time_average_solves = 3
    number_of_iterations = 100
    nominal_solution, nominal_solve_time, nominal_number_of_constraints, directly_uncertain_vars_subs = \
        simulate.generate_model_properties(model, number_of_time_average_solves, number_of_iterations,'normal')

    model_name = 'SimPleAC'
    nGammas = 11
    gammas = np.linspace(0.0,1.0,nGammas)
    min_num_of_linear_sections = 3
    max_num_of_linear_sections = 99
    linearization_tolerance = 1e-4
    verbosity = 1

    methods = [{'name': 'Best Pairs', 'twoTerm': True, 'boyd': False, 'simpleModel': False}]
    uncertainty_sets = ['elliptical']

    # Goal programming (risk minimization) setup
    ndeltas = nGammas
    deltas = np.linspace(0.0, 1.0, ndeltas)
    hotstart = nominal_solution

    # Solution using goal programming
    delta = {}
    delta['solutions'], delta['solve_times'], delta['simulation_results'], \
    delta['number_of_constraints'] = simulate.variable_goal_results(
                                             model, methods, deltas, number_of_iterations,
                                             min_num_of_linear_sections,
                                             max_num_of_linear_sections, verbosity, linearization_tolerance,
                                             number_of_time_average_solves,
                                             uncertainty_sets, nominal_solution, directly_uncertain_vars_subs, parallel=False)


    # # Saving goal programmingresults
    for i,v in delta['solutions'].iteritems():
        v.save('goalResults/'+ str(i))
    save_obj(delta['solve_times'], 'deltasolve_times', 'goalResults')
    save_obj(delta['simulation_results'], 'deltasimulation_results', 'goalResults')
    save_obj(delta['number_of_constraints'], 'deltanumber_of_constraints', 'goalResults')
