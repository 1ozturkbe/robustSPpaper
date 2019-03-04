from gpkit import Variable, Model, SignomialsEnabled, units
from gpkit.small_scripts import mag

from robust.simulations import simulate
# from robust.simulations.simulate import plot_gamma_result_PoFandCost
# from robust.simulations.simulate import filter_gamma_result_dict
# from robust.simulations.read_simulation_data import generate_comparison_plots
from robust.robust import RobustModel
import os

from SimPleAC_setup import SimPleAC_setup

import numpy as np

from SimPleAC_save import save_obj
from SimPleAC_draw import SimPleAC_draw

if __name__ == '__main__':
    model, subs = SimPleAC_setup()
    model.substitutions.update({'C_m': 120})
    model.cost = model['W_{f_m}'] + model['C_m'] * model['t_m'] * units('N')
    number_of_time_average_solves = 3  # 100
    number_of_iterations = 100  # 1000
    # nominal_solution, nominal_solve_time, nominal_number_of_constraints, directly_uncertain_vars_subs = \
    #     simulate.generate_model_properties(model, number_of_time_average_solves, number_of_iterations, 'normal')
    nominal_solution, nominal_solve_time, nominal_number_of_constraints, directly_uncertain_vars_subs = \
        simulate.generate_model_properties(model, number_of_time_average_solves, number_of_iterations)

    model_name = 'SimPleAC'
    nGammas = 3
    gammas = np.linspace(0.05, 1.05, nGammas)
    min_num_of_linear_sections = 3
    max_num_of_linear_sections = 99
    linearization_tolerance = 1e-4
    verbosity = 1

    solutions = []

    for i in gammas:
        nm = RobustModel(model, 'elliptical', twoTerm=True, boyd=False, simpleModel=False, gamma=i)
        solutions.append(nm.robustsolve())

    # solutions, solve_times, simulation_results, number_of_constraints = simulate.variable_gamma_results(
    #                                          model, methods, gammas, number_of_iterations,
    #                                          min_num_of_linear_sections,
    #                                          max_num_of_linear_sections, verbosity, linearization_tolerance,
    #                                          number_of_time_average_solves,
    #                                          uncertainty_sets, nominal_solution, directly_uncertain_vars_subs, parallel=False)

    # Saving results
    # for i,v in solutions.iteritems():
    #     v.save('fuseShrink/'+ str(i))
    # save_obj(solve_times, 'fusesolve_times', 'fuseResults')
    # save_obj(simulation_results, 'fusesimulation_results', 'fuseResults')
    # save_obj(number_of_constraints, 'fusenumber_of_constraints', 'fuseResults')
    #
    # # Plotting of cost and probability of failure for Best Pairs with elliptical uncertainty
    # filteredResult = filter_gamma_result_dict(solutions, 1, 'Best Pairs', 2, 'elliptical')
    # filteredSimulations = filter_gamma_result_dict(simulation_results, 1, 'Best Pairs', 2, 'elliptical')
    # objective_name = 'Total fuel weight'
    # objective_units = 'N'
    # title = ''
    # uncertainty_set = 'elliptical'
    # plot_gamma_result_PoFandCost(title, objective_name, objective_units, filteredResult, filteredSimulations)


    for i in solutions:
        print i('S')
    for i in solutions:
        SimPleAC_draw(i, color='blue')
