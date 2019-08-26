from __future__ import print_function
from __future__ import division
# This script implements a goal programming approach with SimPleAC

from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import range
from SimPleAC_setup import SimPleAC_setup
from gpkit import units, Model, Variable, Monomial
from gpkit.small_scripts import mag

import robust.simulations.simulate as simulate
from robust.simulations.simulate import plot_gamma_result_PoFandCost
from robust.simulations.simulate import filter_gamma_result_dict

import numpy as np
import matplotlib.pyplot as plt

from SimPleAC_save import save_obj, load_obj
from SimPleAC_pof_simulate import pof_parameters
from SimPleAC_draw import SimPleAC_draw
import pickle as pickle

if __name__ == "__main__":
    """
    This script optimizes aircraft over the same deltas (change in objective)
    as the prob. of failure simulation
    """
    # Recalling pof simulation parameters
    [model, methods, gammas, number_of_iterations,
    min_num_of_linear_sections, max_num_of_linear_sections, verbosity, linearization_tolerance,
    number_of_time_average_solves, uncertainty_sets, nominal_solution, directly_uncertain_vars_subs, parallel,
     nominal_number_of_constraints, nominal_solve_time] = pof_parameters()
    nGammas = len(gammas)

    # Restricting method and uncertainty set to Best Pairs, elliptical and/or box for demonstration
    # Note: can only run this simulation one at a time!
    methods = [{'name': 'Best Pairs', 'twoTerm': True, 'boyd': False, 'simpleModel': False}]
    uncertainty_sets = ['elliptical']

    # Loading pof results
    gamma = {}
    gamma['solutions'] = {}
    for i in range(nGammas):
        for j in range(len(methods)):
            for k in range((len(uncertainty_sets))):
                gamma['solutions'][gammas[i], methods[j]['name'], uncertainty_sets[k]] = pickle.load(open("gammaResults\\" +
                                                                    str((gammas[i], methods[j]['name'], uncertainty_sets[k]))))
    gamma['solve_times'] = load_obj('gammasolve_times', 'gammaResults')
    gamma['simulation_results'] = load_obj('gammasimulation_results', 'gammaResults')
    gamma['number_of_constraints'] = load_obj('gammanumber_of_constraints', 'gammaResults')

    # Loading directly_uncertain_vars_subs
    try:
        pickle_in = open('directly_uncertain_dict.pickle', 'rb')
        directly_uncertain_vars_subs = pickle.load(pickle_in)
        pickle_in.close()
    except:
        print('Warning: Please run pof_simulate first for consistent MC results.')

    # Goal programming (risk minimization) setup
    deltas = []
    for i in range(nGammas):
        deltas.append(mag(gamma['solutions'][gammas[i], methods[0]['name'], uncertainty_sets[0]]['cost']/nominal_solution['cost'])-1.)
    offset = 1
    deltas = np.array(deltas)[offset:]

    # Solution using goal programming
    delta = {}
    delta['solutions'], delta['solve_times'], delta['simulation_results'], \
    delta['number_of_constraints'] = simulate.variable_goal_results(
                                             model, methods, deltas, number_of_iterations,
                                             min_num_of_linear_sections,
                                             max_num_of_linear_sections, verbosity, linearization_tolerance,
                                             number_of_time_average_solves,
                                             uncertainty_sets, nominal_solution, directly_uncertain_vars_subs, parallel=False)

    # # Saving goal programming results
    for i,v in delta['solutions'].items():
        v.save('goalResults/'+ str(i))
    save_obj(delta['solve_times'], 'deltasolve_times' + uncertainty_sets[0], 'goalResults')
    save_obj(delta['simulation_results'], 'deltasimulation_results' + uncertainty_sets[0], 'goalResults')
    save_obj(delta['number_of_constraints'], 'deltanumber_of_constraints' + uncertainty_sets[0], 'goalResults')
    save_obj(deltas, 'deltas'+ uncertainty_sets[0], 'goalResults')

    # Plotting gamma vs delta solutions
    count = 0
    for i,v in sorted(gamma['solutions'].items()):
        SimPleAC_draw(v, color='blue', directory = 'goalResults/gammaShape', name='gamma'+uncertainty_sets[0]+str(count))
        count += 1
    count = offset
    for i,v in sorted(delta['solutions'].items()):
        SimPleAC_draw(v, color='orange', directory = 'goalResults/deltaShape', name='delta'+uncertainty_sets[0]+str(count))
        count += 1



