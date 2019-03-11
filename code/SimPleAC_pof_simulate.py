import numpy as np
from robust.simulations import simulate
from SimPleAC_setup import SimPleAC_setup
from SimPleAC_save import save_obj

if __name__ == '__main__':
    model, subs = SimPleAC_setup()
    number_of_time_average_solves = 3  # 100
    number_of_iterations = 100  # 1000
    nominal_solution, nominal_solve_time, nominal_number_of_constraints, directly_uncertain_vars_subs = \
        simulate.generate_model_properties(model, number_of_time_average_solves, number_of_iterations,'normal')

    model_name = 'SimPleAC'
    gammas = np.linspace(0, 1.0, 11)
    min_num_of_linear_sections = 3
    max_num_of_linear_sections = 99
    linearization_tolerance = 1e-4
    verbosity = 1

    methods = [{'name': 'Best Pairs', 'twoTerm': True, 'boyd': False, 'simpleModel': False},
               {'name': 'Linearized Perturbations', 'twoTerm': False, 'boyd': False, 'simpleModel': False},
               {'name': 'Simple Conservative', 'twoTerm': False, 'boyd': False, 'simpleModel': True}]
    uncertainty_sets = ['box', 'elliptical']

    solutions, solve_times, simulation_results, number_of_constraints = simulate.variable_gamma_results(
                                             model, methods, gammas, number_of_iterations,
                                             min_num_of_linear_sections,
                                             max_num_of_linear_sections, verbosity, linearization_tolerance,
                                             number_of_time_average_solves,
                                             uncertainty_sets, nominal_solution, directly_uncertain_vars_subs, parallel=False)

    # Saving results
    for i,v in solutions.iteritems():
        print i
        v.save('gammaResults/'+ str(i))
    save_obj(solve_times, 'gammasolve_times', 'gammaResults')
    save_obj(simulation_results, 'gammasimulation_results', 'gammaResults')
    save_obj(number_of_constraints, 'gammanumber_of_constraints', 'gammaResults')
