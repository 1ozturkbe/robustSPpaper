# This script implements a goal programming approach with SimPleAC
from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import range
from robust.simulations.simulate import plot_goal_result_PoFandCost
from robust.simulations.simulate import filter_gamma_result_dict

import numpy as np
from SimPleAC_save import save_obj, load_obj
from SimPleAC_pof_simulate import pof_parameters
import pickle as pickle

if __name__ == "__main__":
    # Retrieving pof parameters
    [model, methods, gammas, number_of_iterations,
    min_num_of_linear_sections, max_num_of_linear_sections, verbosity, linearization_tolerance,
    number_of_time_average_solves, uncertainty_sets, nominal_solution, directly_uncertain_vars_subs, parallel,
            nominal_number_of_constraints, nominal_solve_time] = pof_parameters()

    # Restricting method and uncertainty set to Best Pairs, elliptical for demonstration
    methods = [{'name': 'Best Pairs', 'twoTerm': True, 'boyd': False, 'simpleModel': False}]
    uncertainty_sets = ['elliptical']

    # # Loading goal programming results
    delta = {}
    deltas = load_obj('deltas'+ uncertainty_sets[0], 'goalResults')
    ndeltas = len(deltas)
    delta['solutions'] = {}
    for i in range(ndeltas):
        delta['solutions'][deltas[i], methods[0]['name'], uncertainty_sets[0]] = pickle.load(open("goalResults/" +
                                                                    str((deltas[i], methods[0]['name'], uncertainty_sets[0])),'rb'))
    delta['solve_times'] = load_obj('deltasolve_times' + uncertainty_sets[0], 'goalResults')
    delta['simulation_results'] = load_obj('deltasimulation_results' + uncertainty_sets[0], 'goalResults')
    delta['number_of_constraints'] = load_obj('deltanumber_of_constraints' + uncertainty_sets[0], 'goalResults')

    # Compute resulting gammas
    resGammas = []
    for i in range(ndeltas):
        resGammas.append(delta['solutions'][deltas[i], methods[0]['name'], uncertainty_sets[0]]('\\Gamma'))

    # Plotting of cost and probability of failure for Best Pairs with elliptical uncertainty
    filteredResult = filter_gamma_result_dict(delta['solutions'], 1, 'Best Pairs', 2, uncertainty_sets[0])
    filteredSimulations = filter_gamma_result_dict(delta['simulation_results'], 1, 'Best Pairs', 2, uncertainty_sets[0])
    objective_name = 'Total fuel weight'
    objective_units = 'N'
    title = ''
    uncertainty_set = uncertainty_sets[0]
    plot_goal_result_PoFandCost(title, objective_name, 'W_{f_m}', objective_units, filteredResult, filteredSimulations)
