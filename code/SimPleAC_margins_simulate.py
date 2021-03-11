from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import range
import numpy as np
from SimPleAC_setup import SimPleAC_setup
from SimPleAC_save import save_obj
from gpkit.small_scripts import mag
from gpkit import Model

from SimPleAC_pof_simulate import pof_parameters
from robust.simulations.simulate import RobustGPTools
import pickle as pickle

if __name__ == '__main__':
    [model, methods, gammas, number_of_iterations,
    min_num_of_linear_sections, max_num_of_linear_sections, verbosity, linearization_tolerance,
    number_of_time_average_solves, uncertainty_sets, nominal_solution, directly_uncertain_vars_subs, parallel,
    nominal_number_of_constraints, nominal_solve_time] = pof_parameters()

    # Loading directly_uncertain_vars_subs
    try:
        pickle_in = open('directly_uncertain_dict.pickle', 'rb')
        directly_uncertain_vars_subs = pickle.load(pickle_in)
        pickle_in.close()
    except:
        print('Warning: Please run pof_simulate first for consistent MC results.')


    nGammas = len(gammas)
    solutions = {}
    simulation_results = {}
    number_of_constraints = {}
    for i in range(nGammas):
        print(i)
        margin_subs = {k: v + gammas[i]*np.sign(mag(nominal_solution['sensitivities']['constants'](k.key)))*k.key.pr * v / 100.0
                                     for k, v in list(model.substitutions.items())
                                     if k in model.varkeys and RobustGPTools.is_directly_uncertain(k)}

        mm = Model(model.cost, model)
        mm.substitutions.update(margin_subs)
        solutions[gammas[i]] = mm.localsolve(verbosity=0)
        simulation_results[gammas[i]] = RobustGPTools.probability_of_failure(mm, solutions[gammas[i]], directly_uncertain_vars_subs,
                                                                             number_of_iterations)
        try:
            number_of_constraints[gammas[i]] = len([cnstrnt for cnstrnt in mm.flat()])
        except AttributeError:
            number_of_constraints[gammas[i]] = len([cnstrnt for cnstrnt in mm[-1].flat()])
        print(simulation_results[gammas[i]])

    # Saving results
    for i,v in solutions.items():
        v.save('marginResults/'+ str(i))
    save_obj(number_of_constraints, 'marginnumber_of_constraints', 'marginResults')
    save_obj(simulation_results, 'marginsimulation_results', 'marginResults')

