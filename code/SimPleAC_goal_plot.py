# This script implements a goal programming approach with SimPleAC

from SimPleAC_setup import SimPleAC_setup
from gpkit import units, Model, Variable, Monomial
from gpkit.constraints.bounded import Bounded
from gpkit.small_scripts import mag

from robust.robust import RobustModel
from robust.simulations.simulate import generate_model_properties
from robust.robust_gp_tools import RobustGPTools
from robust.simulations.simulate import simulate_robust_model
import robust.simulations.simulate as simulate
from robust.simulations.simulate import plot_gamma_result_PoFandCost
from robust.simulations.simulate import filter_gamma_result_dict

import numpy as np

import matplotlib.pyplot as plt

from SimPleAC_save import save_obj, load_obj
import cPickle as pickle

if __name__ == "__main__":
    model_name = 'SimPleAC'
    nGammas = 11
    gammas = np.linspace(0.0,1.0,nGammas)
    methods = [{'name': 'Best Pairs', 'twoTerm': True, 'boyd': False, 'simpleModel': False}]
    uncertainty_sets = ['elliptical']

    # Goal programming (risk minimization) setup
    ndeltas = nGammas
    deltas = np.linspace(0.0, 1.0, ndeltas)

    # # Loading goal programming results
    delta = {}
    delta['solutions'] = {}
    for i in range(ndeltas):
        delta['solutions'][deltas[i], methods[0]['name'], uncertainty_sets[0]] = pickle.load(open("goalResults\\" +
                                                                    str((deltas[i], methods[0]['name'], uncertainty_sets[0]))))
    delta['solve_times'] = load_obj('deltasolve_times', 'goalResults')
    delta['simulation_results'] = load_obj('deltasimulation_results', 'goalResults')
    delta['number_of_constraints'] = load_obj('deltanumber_of_constraints', 'goalResults')

    # Plotting of cost and probability of failure for Best Pairs with elliptical uncertainty
    for i in [delta]:
        filteredResult = filter_gamma_result_dict(i['solutions'], 1, 'Best Pairs', 2, 'elliptical')
        filteredSimulations = filter_gamma_result_dict(i['simulation_results'], 1, 'Best Pairs', 2, 'elliptical')
        objective_name = 'Total fuel weight'
        objective_units = 'N'
        title = ''
        uncertainty_set = 'elliptical'
        plot_goal_result_PoFandCost(title, objective_name, 'W_{f_m}', objective_units, filteredResult, filteredSimulations)
