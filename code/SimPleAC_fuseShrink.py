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

    nominal_solution, nominal_solve_time, nominal_number_of_constraints, directly_uncertain_vars_subs = \
        simulate.generate_model_properties(model, number_of_time_average_solves, number_of_iterations, 'normal')

    model_name = 'SimPleAC'
    nGammas = 10
    gammas = np.linspace(0.1, 1.0, nGammas)
    min_num_of_linear_sections = 3
    max_num_of_linear_sections = 99
    linearization_tolerance = 1e-4
    verbosity = 1

    solutions = []

    for i in gammas:
        nm = RobustModel(model, 'elliptical', twoTerm=True, boyd=False, simpleModel=False, gamma=i)
        solutions.append(nm.robustsolve(verbosity = 2))

    SimPleAC_draw(nominal_solution, color='blue', directory = 'fuseResults/', name='fuse0')
    count = int(0)
    for i in solutions:
        print i('S'), i['cost']
    for i in solutions:
        count+=1
        SimPleAC_draw(i, color='blue', directory = 'fuseResults/', name='fuse'+str(count))
