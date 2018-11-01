from gpkit import Variable, Model, SignomialsEnabled, units
from robust.simulations import simulate, read_simulation_data
import os

from SimPleAC_setup import SimPleAC_setup

import numpy as np

if __name__ == '__main__':
    model, subs = SimPleAC_setup()
    number_of_time_average_solves = 3  # 100
    number_of_iterations = 100  # 1000
    nominal_solution, nominal_solve_time, nominal_number_of_constraints, directly_uncertain_vars_subs = \
        simulate.generate_model_properties(model, number_of_time_average_solves, number_of_iterations)

    model_name = 'SimPleAC'
    nGammas = 21
    gammas = np.linspace(0,1,nGammas)
    min_num_of_linear_sections = 3
    max_num_of_linear_sections = 99
    linearization_tolerance = 1e-3
    verbosity = 1

    methods = [{'name': 'Best Pairs', 'twoTerm': True, 'boyd': False, 'simpleModel': False},
               {'name': 'Linearized Perturbations', 'twoTerm': False, 'boyd': False, 'simpleModel': False},
               {'name': 'Simple Conservative', 'twoTerm': False, 'boyd': False, 'simpleModel': True}]
    uncertainty_sets = ['box', 'elliptical']

    # results = {}
    # for i in range(0,nGammas):
    #     results[gammas[i]] =
    gamma = 1

    variable_gamma_file_name = os.path.dirname(__file__) + '/simulation_data_variable_gamma.txt'
    simulate.generate_variable_gamma_results(model, model_name, gammas, number_of_iterations,
                                             min_num_of_linear_sections,
                                             max_num_of_linear_sections, verbosity, linearization_tolerance,
                                             variable_gamma_file_name, number_of_time_average_solves, methods,
                                             uncertainty_sets, nominal_solution, nominal_solve_time,
                                             nominal_number_of_constraints, directly_uncertain_vars_subs)
