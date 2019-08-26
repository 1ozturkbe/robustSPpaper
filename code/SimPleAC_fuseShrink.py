from __future__ import division
from builtins import str
from gpkit import Variable, Model, SignomialsEnabled, units
from gpkit.small_scripts import mag

from robust.simulations import simulate
from robust.simulations.simulate import plot_gamma_result_PoFandCost

from SimPleAC_setup import SimPleAC_setup

import numpy as np

from SimPleAC_save import save_obj
from SimPleAC_draw import SimPleAC_draw

import matplotlib.pyplot as plt

if __name__ == '__main__':
    model, subs = SimPleAC_setup()
    model.substitutions.update({'C_m': 120})
    model.cost = model['W_{f_m}'] + model['C_m'] * model['t_m'] * units('N')
    number_of_time_average_solves = 3
    number_of_iterations = 100

    nominal_solution, nominal_solve_time, nominal_number_of_constraints, directly_uncertain_vars_subs = \
        simulate.generate_model_properties(model, number_of_time_average_solves, number_of_iterations, 'normal')

    model_name = 'SimPleAC'
    nGammas = 11
    gammas = np.linspace(0.0, 1.0, nGammas)
    min_num_of_linear_sections = 3
    max_num_of_linear_sections = 99
    linearization_tolerance = 1e-4
    verbosity = 1

    methods = [{'name': 'Best Pairs', 'twoTerm': True, 'boyd': False, 'simpleModel': False}]
    uncertainty_sets = ['elliptical']

    # Simulating aircraft
    solutions, solve_times, simulation_results, number_of_constraints = simulate.variable_gamma_results(
                                             model, methods, gammas, number_of_iterations,
                                             min_num_of_linear_sections,
                                             max_num_of_linear_sections, verbosity, linearization_tolerance,
                                             number_of_time_average_solves,
                                             uncertainty_sets, nominal_solution, directly_uncertain_vars_subs, parallel=False)


    # Saving results
    for i,v in solutions.items():
        v.save('fuseResults/'+ str(i))
    save_obj(solve_times, 'fusesolve_times', 'fuseResults')
    save_obj(simulation_results, 'fusesimulation_results', 'fuseResults')
    save_obj(number_of_constraints, 'fusenumber_of_constraints', 'fuseResults')

    # Plotting probability of failure and cost
    objective_name = 'Total cost'
    objective_units = 'fuel & time'
    title = ''
    uncertainty_set = 'elliptical'
    plot_gamma_result_PoFandCost(title, objective_name, objective_units, solutions, simulation_results)

    # Plotting fuel vs. time cost
    fuelCost = np.array([mag(v(model['W_{f_m}'])) for i,v in sorted(solutions.items())])
    timeCost = np.array([mag(v(model['C_m']*model['t_m'])) for i,v in sorted(solutions.items())])
    timeSens = np.array([mag(v['sensitivities']['constants'][model['C_m']]) for i,v in sorted(solutions.items())])
    fig, ax1 = plt.subplots()
    ax1.set_xlabel(r'Size of uncertainty set, $\Gamma$', size='large')
    ax1.set_ylabel(r'Ratio of time to fuel cost, $c_t / c_f$', color='b', size='large')
    ax1.plot(gammas, timeCost/fuelCost, 'b-')
    ax2 = ax1.twinx()
    ax2.set_ylabel(r'Sensitivity to time cost index, $s(C_m)$', color='r', size='large')
    ax2. plot(gammas, timeSens, 'r-')
    plt.show()

    # Saving sketches of aircraft
    count = int(0)
    for i, v in sorted(solutions.items()):
        SimPleAC_draw(v, color='blue', directory = 'fuseResults/', name='fuse'+str(count))
        count+=1
