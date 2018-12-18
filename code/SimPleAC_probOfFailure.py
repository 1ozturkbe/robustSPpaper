from gpkit import Variable, Model, SignomialsEnabled, units
from gpkit.small_scripts import mag

from robust.simulations import simulate
from robust.simulations.simulate import plot_gamma_result_PoFandCost
from robust.simulations.simulate import filter_gamma_result_dict
from robust.simulations.read_simulation_data import generate_comparison_plots
import os

from SimPleAC_setup import SimPleAC_setup

import numpy as np

from SimPleAC_save import save_obj

if __name__ == '__main__':
    model, subs = SimPleAC_setup()
    number_of_time_average_solves = 3  # 100
    number_of_iterations = 150  # 1000
    nominal_solution, nominal_solve_time, nominal_number_of_constraints, directly_uncertain_vars_subs = \
        simulate.generate_model_properties(model, number_of_time_average_solves, number_of_iterations,'normal')

    model_name = 'SimPleAC'
    nGammas = 16
    gammas = np.linspace(0.8,1.05,nGammas)
    min_num_of_linear_sections = 3
    max_num_of_linear_sections = 99
    linearization_tolerance = 1e-4
    verbosity = 1

    methods = [{'name': 'Best Pairs', 'twoTerm': True, 'boyd': False, 'simpleModel': False},
               {'name': 'Linearized Perturbations', 'twoTerm': False, 'boyd': False, 'simpleModel': False},
               {'name': 'Simple Conservative', 'twoTerm': False, 'boyd': False, 'simpleModel': True}]
    uncertainty_sets = ['box', 'elliptical']
    # methods = [{'name': 'Best Pairs', 'twoTerm': True, 'boyd': False, 'simpleModel': False}]
    # uncertainty_sets = ['elliptical']

    solutions, solve_times, simulation_results, number_of_constraints = simulate.variable_gamma_results(
                                             model, methods, gammas, number_of_iterations,
                                             min_num_of_linear_sections,
                                             max_num_of_linear_sections, verbosity, linearization_tolerance,
                                             number_of_time_average_solves,
                                             uncertainty_sets, nominal_solution, directly_uncertain_vars_subs, parallel=False)

    # Saving results
    for i,v in solutions.iteritems():
        v.save('obj/'+ str(i))
    save_obj(solve_times, 'gammasolve_times')
    save_obj(simulation_results, 'gammasimulation_results')
    save_obj(number_of_constraints, 'gammanumber_of_constraints')

    # Plotting of cost and probability of failure for Best Pairs with elliptical uncertainty
    filteredResult = filter_gamma_result_dict(solutions, 1, 'Simple Conservative', 2, 'elliptical')
    filteredSimulations = filter_gamma_result_dict(simulation_results, 1, 'Simple Conservative', 2, 'elliptical')
    objective_name = 'Total fuel weight'
    objective_units = 'N'
    title = ''
    uncertainty_set = 'box'
    plot_gamma_result_PoFandCost(title, objective_name, objective_units, filteredResult, filteredSimulations)

    #Plotting of solution times
    gamma = gammas[14]
    filteredSolutions = filter_gamma_result_dict(solutions, 0, gamma, 2, uncertainty_set)
    filteredsetup_times = {}
    for i in filteredSolutions.iterkeys():
        filteredsetup_times[i] = filteredSolutions[i]['setuptime']
    filteredSimulations =  filter_gamma_result_dict(simulation_results, 0, gamma, 2, uncertainty_set)
    filteredsolve_times = filter_gamma_result_dict(solve_times, 0, gamma, 2, uncertainty_set)
    filteredCosts = {i:v[1] for i,v in filteredSimulations.iteritems()}
    filteredn_of_constr = filter_gamma_result_dict(number_of_constraints, 0, gamma, 2, uncertainty_set)

    relative_objective_values = [mag(v) for i,v in sorted(filteredCosts.iteritems())]
    relative_number_of_constraints = [v/nominal_number_of_constraints for i,v in sorted(filteredn_of_constr.iteritems())]
    relative_setup_times = [v/nominal_solve_time for i,v in sorted(filteredsetup_times.iteritems())]
    relative_solve_times = [v/nominal_solve_time for i,v in sorted(filteredsolve_times.iteritems())]

    generate_comparison_plots(relative_objective_values, objective_name, relative_number_of_constraints,
                              relative_setup_times, relative_solve_times, uncertainty_set, [method['name'] for method in methods])

    # gamma = 1
    # numbers_of_linear_sections = [40, 60]  # [12, 14, 15, 16, 17, 18, 20, 22, 24, 26, 28, 30, 32, 36, 44, 52, 60, 70, 80]

    # methods = [{'name': 'Best Pairs', 'twoTerm': True, 'boyd': False, 'simpleModel': False},
    #            {'name': 'Linearized Perturbations', 'twoTerm': False, 'boyd': False, 'simpleModel': False}]
    # uncertainty_sets = ['box', 'elliptical']
    #
    # variable_pwl_file_name = 'simulation_data_variable_pwl.txt'
    # simulate.generate_variable_piecewiselinearsections_results(model, model_name, gamma, number_of_iterations,
    #                                                            numbers_of_linear_sections, linearization_tolerance,
    #                                                            verbosity, variable_pwl_file_name,
    #                                                            number_of_time_average_solves, methods, uncertainty_sets,
    #                                                            nominal_solution, nominal_solve_time,
    #                                                            nominal_number_of_constraints,
    #                                                            directly_uncertain_vars_subs)
    #
    # file_path_gamma = 'simulation_data_variable_gamma.txt'
    # file_path_pwl = 'simulation_data_variable_pwl.txt'

