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
    number_of_iterations = 150
    nominal_solution, nominal_solve_time, nominal_number_of_constraints, directly_uncertain_vars_subs = \
        simulate.generate_model_properties(model, number_of_time_average_solves, number_of_iterations,'normal')

    model_name = 'SimPleAC'
    nGammas = 16
    gammas = np.linspace(0.8,1.05,nGammas)
    min_num_of_linear_sections = 3
    max_num_of_linear_sections = 99
    linearization_tolerance = 1e-4
    verbosity = 1

    methods = [{'name': 'Best Pairs', 'twoTerm': True, 'boyd': False, 'simpleModel': False}]
    uncertainty_sets = ['elliptical']

    #Solution using standard method of changing Gamma
    gamma = {}
    gamma['solutions'], gamma['solve_times'], gamma['simulation_results'], \
    gamma['number_of_constraints'] = simulate.variable_gamma_results(
                                             model, methods, gammas, number_of_iterations,
                                             min_num_of_linear_sections,
                                             max_num_of_linear_sections, verbosity, linearization_tolerance,
                                             number_of_time_average_solves,
                                             uncertainty_sets, nominal_solution, directly_uncertain_vars_subs, parallel=False)

    # Saving results
    for i,v in gamma['solutions'].iteritems():
        v.save('goalResults/gamma'+ str(i))
    save_obj(gamma['solve_times'], 'gammasolve_times', 'goalResults')
    save_obj(gamma['simulation_results'], 'gammasimulation_results', 'goalResults')
    save_obj(gamma['number_of_constraints'], 'gammanumber_of_constraints', 'goalResults')

    # # Loading results
    # gamma = {}
    # gamma['solutions'] = {}
    # for i in range(nGammas):
    #     gamma['solutions'][gammas[i], methods[0]['name'], uncertainty_sets[0]] = pickle.load(open("goalResults\gamma" +
    #                                                                 str((gammas[i], methods[0]['name'], uncertainty_sets[0]))))
    # gamma['solve_times'] = load_obj('gammasolve_times', 'goalResults')
    # gamma['simulation_results'] = load_obj('gammasimulation_results', 'goalResults')
    # gamma['number_of_constraints'] = load_obj('gammanumber_of_constraints', 'goalResults')

    # Goal programming (risk minimization) setup
    ndeltas = nGammas
    deltas = np.linspace(0.001, 1.0, ndeltas)
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
        v.save('goalResults/delta'+ str(i))
    save_obj(delta['solve_times'], 'deltasolve_times', 'goalResults')
    save_obj(delta['simulation_results'], 'deltasimulation_results', 'goalResults')
    save_obj(delta['number_of_constraints'], 'deltanumber_of_constraints', 'goalResults')

    # # Loading goal programming results
    # delta = {}
    # delta['solutions'] = {}
    # for i in range(ndeltas):
    #     delta['solutions'][deltas[i], methods[0]['name'], uncertainty_sets[0]] = pickle.load(open("goalResults\delta" +
    #                                                                 str((deltas[i], methods[0]['name'], uncertainty_sets[0]))))
    # delta['solve_times'] = load_obj('deltasolve_times', 'goalResults')
    # delta['simulation_results'] = load_obj('deltasimulation_results', 'goalResults')
    # delta['number_of_constraints'] = load_obj('deltanumber_of_constraints', 'goalResults')

    # Plotting of cost and probability of failure for Best Pairs with elliptical uncertainty
    for i in [delta, gamma]:
        filteredResult = filter_gamma_result_dict(i['solutions'], 1, 'Best Pairs', 2, 'elliptical')
        filteredSimulations = filter_gamma_result_dict(i['simulation_results'], 1, 'Best Pairs', 2, 'elliptical')
        objective_name = 'Total fuel weight'
        objective_units = 'N'
        title = ''
        uncertainty_set = 'elliptical'
        plot_gamma_result_PoFandCost(title, objective_name, objective_units, filteredResult, filteredSimulations)
