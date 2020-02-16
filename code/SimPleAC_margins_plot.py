# This script implements a goal programming approach with SimPleAC
from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import range
from robust.simulations.simulate import plot_goal_result_PoFandCost
from robust.simulations.simulate import filter_gamma_result_dict
from robust.simulations.read_simulation_data import objective_proboffailure_vs_gamma

import numpy as np
from SimPleAC_save import save_obj, load_obj
from SimPleAC_pof_simulate import pof_parameters
import pickle as pickle
from gpkit.small_scripts import mag


if __name__ == "__main__":
    # Retrieving pof parameters
    [model, methods, gammas, number_of_iterations,
    min_num_of_linear_sections, max_num_of_linear_sections, verbosity, linearization_tolerance,
    number_of_time_average_solves, uncertainty_sets, nominal_solution, directly_uncertain_vars_subs, parallel,
            nominal_number_of_constraints, nominal_solve_time] = pof_parameters()

    # # Loading margins results
    margin = {}
    nmargins = len(gammas)
    margins = np.linspace(0.,1.,nmargins)

    margin['solutions'] = {}
    for i in range(nmargins):
        margin['solutions'][margins[i]] = pickle.load(open("marginResults/" +
                                                                    str(margins[i]), 'rb'))
    margin['number_of_constraints'] = load_obj('marginnumber_of_constraints', 'marginResults')
    margin['simulation_results'] = load_obj('marginsimulation_results', 'marginResults')

    # Plotting of cost and probability of failure
    objective_name = 'Total fuel weight'
    objective_units = 'N'
    title = ''
    filteredResult = margin['solutions']
    filteredSimulations = margin['simulation_results']
    objective_varkey = 'W_{f_m}'

    objective_costs = []
    pofs = []
    objective_stddev = []
    for i in sorted(filteredResult.keys()):
        objective_stddev.append(filteredSimulations[i][2])
        objective_costs.append(mag(filteredSimulations[i][1]))
        pofs.append(filteredSimulations[i][0])
    objective_proboffailure_vs_gamma(margins, objective_costs, objective_name, objective_units,
                                     np.min(objective_costs), np.max(objective_costs), pofs, title, objective_stddev)
