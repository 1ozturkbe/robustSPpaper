
import numpy as np
from robust.simulations.simulate import plot_gamma_result_PoFandCost
from robust.simulations.simulate import filter_gamma_result_dict, generate_model_properties
from robust.simulations.read_simulation_data import generate_comparison_plots
from SimPleAC_save import load_obj
import cPickle as pickle
from gpkit.small_scripts import mag
from SimPleAC_setup import SimPleAC_setup
from SimPleAC_pof_simulate import pof_parameters


if __name__ == '__main__':
    # Recalling simulation parameters
    [model, methods, gammas, number_of_iterations,
    min_num_of_linear_sections, max_num_of_linear_sections, verbosity, linearization_tolerance,
    number_of_time_average_solves, uncertainty_sets, nominal_solution, directly_uncertain_vars_subs, parallel,
     nominal_number_of_constraints, nominal_solve_time] = pof_parameters()
    nGammas = len(gammas)

    # Loading results
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

    # Plotting of cost and probability of failure for all methods and uncertainty sets
    objective_name = 'Total fuel weight'
    objective_units = 'N'
    title = ''
    for i in range(len(methods)):
        for j in range(len(uncertainty_sets)):
            print "Method: " + methods[i]['name']
            print "Uncertainty Set: " + uncertainty_sets[j]
            filteredResult = filter_gamma_result_dict(gamma['solutions'], 1, methods[i]['name'], 2, uncertainty_sets[j])
            filteredSimulations = filter_gamma_result_dict(gamma['simulation_results'], 1, methods[i]['name'], 2, uncertainty_sets[j])
            uncertainty_set = uncertainty_sets[j]
            plot_gamma_result_PoFandCost(title, objective_name, objective_units, filteredResult, filteredSimulations)

    # Plotting solution times and costs
    for uncertainty_set in uncertainty_sets:
        gammaVal = 1.0
        filteredSolutions = filter_gamma_result_dict(gamma['solutions'], 0, gammaVal, 2, uncertainty_set)
        filteredsetup_times = {}
        for i in filteredSolutions.iterkeys():
            filteredsetup_times[i] = filteredSolutions[i]['setuptime']
        filteredSimulations =  filter_gamma_result_dict(gamma['simulation_results'], 0, gammaVal, 2, uncertainty_set)
        filteredsolve_times = filter_gamma_result_dict(gamma['solve_times'], 0, gammaVal, 2, uncertainty_set)
        filteredCosts = {i:v[1]/nominal_solution['cost'] for i,v in filteredSimulations.iteritems()}
        filteredn_of_constr = filter_gamma_result_dict(gamma['number_of_constraints'], 0, gammaVal, 2, uncertainty_set)

        relative_objective_values = [mag(v) for i,v in sorted(filteredCosts.iteritems())]
        relative_number_of_constraints = [v/nominal_number_of_constraints for i,v in sorted(filteredn_of_constr.iteritems())]
        relative_setup_times = [v/nominal_solve_time for i,v in sorted(filteredsetup_times.iteritems())]
        relative_solve_times = [v/nominal_solve_time for i,v in sorted(filteredsolve_times.iteritems())]

        generate_comparison_plots(relative_objective_values, objective_name, relative_number_of_constraints,
                                  relative_setup_times, relative_solve_times, uncertainty_set, [method['name'] for method in methods])
